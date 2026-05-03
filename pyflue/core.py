"""PyFlue core agent and session API."""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import AsyncIterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import aiosqlite
from pydantic import BaseModel, TypeAdapter

from pyflue.code.base import PythonRunResult
from pyflue.code.registry import create_python_backend
from pyflue.config import load_config
from pyflue.harnesses.registry import create_backend
from pyflue.sandbox import SandboxPolicy
from pyflue.sandboxes.registry import create_sandbox
from pyflue.skills import (
    load_project_instructions,
    load_roles,
    load_skills,
    render_skill_prompt,
)
from pyflue.types import HarnessResult, PyFlueConfig, PyFlueEvent

RESULT_START = "---RESULT_START---"
RESULT_END = "---RESULT_END---"
_RESULT_RE = re.compile(
    rf"{RESULT_START}\s*\n(?P<body>[\s\S]*?)\n?{RESULT_END}",
    re.MULTILINE,
)


async def init(
    *,
    model: str | None = None,
    harness: str | None = None,
    sandbox: str | None = None,
    python_backend: str | None = None,
    skills_dir: str | Path | None = None,
    config_path: str | Path | None = None,
    env: dict[str, str] | None = None,
    allow_write: bool = False,
    allow_shell: bool = False,
    allowed_commands: tuple[str, ...] | list[str] | None = None,
    allow_compound_commands: bool | None = None,
) -> PyFlueAgent:
    """Initialize a PyFlue agent."""
    config = load_config(config_path or "pyflue.toml")
    if model is not None:
        config.model = model
    if harness is not None:
        config.harness = harness
    if sandbox is not None:
        config.sandbox = sandbox
    if python_backend is not None:
        config.python_backend = python_backend
    if skills_dir is not None:
        path = Path(skills_dir).expanduser()
        config.skills_dir = path if path.is_absolute() else config.root / path
    if env:
        config.env.update({str(key): str(value) for key, value in env.items()})
    if allowed_commands is not None:
        config.allowed_commands = tuple(str(item) for item in allowed_commands)
    if allow_compound_commands is not None:
        config.allow_compound_commands = allow_compound_commands
    return PyFlueAgent(
        config=config,
        sandbox_policy=SandboxPolicy(
            allow_write=allow_write,
            allow_shell=allow_shell,
            allowed_commands=config.allowed_commands,
            allow_compound_commands=config.allow_compound_commands,
        ),
    )


class PyFlueAgent:
    """Factory for stateful PyFlue sessions."""

    def __init__(
        self,
        *,
        config: PyFlueConfig,
        sandbox_policy: SandboxPolicy | None = None,
    ):
        self.config = config
        self.backend = create_backend(config.harness)
        self.instructions = load_project_instructions(config.root)
        self.skills = load_skills(config.root, config.skills_dir)
        self.roles = load_roles(config.root, config.roles_dir)
        self.sandbox_policy = sandbox_policy or SandboxPolicy()
        self.state_dir = config.state_dir or config.root / ".pyflue" / "sessions"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sandbox_state_dir = config.root / ".pyflue" / "sandboxes"
        self.sandbox_state_dir.mkdir(parents=True, exist_ok=True)

    async def session(self, session_id: str | None = None) -> PyFlueSession:
        """Open or create a persistent session."""
        sid = session_id or "default"
        session = PyFlueSession(agent=self, session_id=sid)
        await session._ensure_store()
        return session


class PyFlueSession:
    """One persistent PyFlue conversation."""

    def __init__(self, *, agent: PyFlueAgent, session_id: str):
        self.agent = agent
        self.session_id = session_id
        safe_id = re.sub(r"[^a-zA-Z0-9_.-]+", "_", session_id)
        self.safe_id = safe_id
        self.db_path = self.agent.state_dir / f"{safe_id}.sqlite3"
        self.sandbox = create_sandbox(
            self.agent.config.sandbox,
            root=self.agent.sandbox_state_dir / safe_id,
            policy=self.agent.sandbox_policy,
            env=self.agent.config.env,
            config=dict(self.agent.config.harness_config.get("sandbox", {})),
        )
        self.python_backend = create_python_backend(
            self.agent.config.python_backend,
            sandbox=self.sandbox,
        )

    async def prompt(
        self,
        text: str,
        *,
        result: type[BaseModel] | Any | None = None,
        role: str | None = None,
        model: str | None = None,
        retries: int | None = None,
        stream: bool = False,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> HarnessResult | Any:
        """Run one prompt turn."""
        prompt = self._build_prompt(text, result=result, role=role)
        await self._append("user", text)
        history = await self._history_prompt(prompt)
        with self._grant_secrets(secrets):
            output = await self._run_backend(history, model=model, stream=stream)
        await self._append("assistant", output.text)
        if result is not None:
            return await self._parse_with_retry(
                output,
                result,
                original_prompt=history,
                model=model,
                retries=self.agent.config.typed_retries if retries is None else retries,
                stream=stream,
            )
        return output

    async def stream(
        self,
        text: str,
        *,
        role: str | None = None,
        model: str | None = None,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> AsyncIterator[PyFlueEvent]:
        """Stream normalized PyFlue events for one prompt turn."""
        yield PyFlueEvent("start", {"session_id": self.session_id})
        try:
            result = await self.prompt(
                text,
                role=role,
                model=model,
                stream=True,
                secrets=secrets,
            )
            if isinstance(result, HarnessResult):
                if result.text:
                    yield PyFlueEvent("delta", {"text": result.text})
                yield PyFlueEvent("end", {"text": result.text, "metadata": result.metadata})
            else:
                yield PyFlueEvent("end", {"result": result})
        except Exception as exc:
            yield PyFlueEvent("error", {"message": str(exc), "type": type(exc).__name__})
            raise

    async def skill(
        self,
        name: str,
        *,
        args: dict[str, Any] | None = None,
        result: type[BaseModel] | Any | None = None,
        role: str | None = None,
        model: str | None = None,
        retries: int | None = None,
        stream: bool = False,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> HarnessResult | Any:
        """Run a Markdown-defined skill."""
        skill = self.agent.skills.get(name)
        if skill is None:
            available = ", ".join(sorted(self.agent.skills)) or "(none)"
            raise KeyError(f"Unknown skill '{name}'. Available skills: {available}")
        prompt = render_skill_prompt(skill, args=args)
        return await self.prompt(
            prompt,
            result=result,
            role=role,
            model=model,
            retries=retries,
            stream=stream,
            secrets=secrets,
        )

    async def subagent(
        self,
        prompt: str,
        *,
        result: type[BaseModel] | Any | None = None,
        role: str | None = None,
        model: str | None = None,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> HarnessResult | Any:
        """Run a child session with isolated history and shared sandbox."""
        output = await self.task(prompt, result=result, role=role, model=model, secrets=secrets)
        return output

    async def task(
        self,
        prompt: str,
        *,
        result: type[BaseModel] | Any | None = None,
        role: str | None = None,
        model: str | None = None,
        task_id: str | None = None,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> HarnessResult | Any:
        """Run a Flue-style child task with shared sandbox and isolated history."""
        child_id = task_id or f"{self.session_id}:task:{uuid.uuid4().hex[:10]}"
        child = await self.agent.session(child_id)
        child.sandbox = self.sandbox
        child.python_backend = self.python_backend
        output = await child.prompt(prompt, result=result, role=role, model=model, secrets=secrets)
        await self._append("assistant", f"Subagent {child_id} completed.")
        return output

    async def run_python(
        self,
        code: str,
        *,
        inputs: dict[str, Any] | None = None,
        external_functions: dict[str, Any] | None = None,
        result: type[BaseModel] | Any | None = None,
        type_check: bool = False,
        type_check_stubs: str | None = None,
        restart: bool = False,
        timeout: float | None = 5.0,
        resource_limits: dict[str, Any] | None = None,
        mount: Any | None = None,
    ) -> PythonRunResult | Any:
        """Run Python code through the configured Python backend."""
        if self.python_backend is None:
            raise RuntimeError(
                "No Python backend configured. Use init(python_backend='monty') "
                "or set python_backend = 'monty' in pyflue.toml."
            )
        output = await self.python_backend.run(
            code,
            inputs=inputs,
            external_functions=external_functions,
            type_check=type_check,
            type_check_stubs=type_check_stubs,
            restart=restart,
            timeout=timeout,
            resource_limits=resource_limits,
            mount=mount,
        )
        if result is not None:
            return TypeAdapter(result).validate_python(output.result)
        return output

    async def start_python(
        self,
        code: str,
        *,
        inputs: dict[str, Any] | None = None,
        type_check: bool = False,
        type_check_stubs: str | None = None,
        timeout: float | None = 5.0,
        resource_limits: dict[str, Any] | None = None,
        mount: Any | None = None,
    ) -> Any:
        """Start snapshot-driven Python execution when the backend supports it."""
        if self.python_backend is None or not hasattr(self.python_backend, "start"):
            raise RuntimeError("The configured Python backend does not support start_python().")
        return await self.python_backend.start(
            code,
            inputs=inputs,
            type_check=type_check,
            type_check_stubs=type_check_stubs,
            timeout=timeout,
            resource_limits=resource_limits,
            mount=mount,
        )

    def dump_python_state(self) -> bytes | None:
        """Serialize Python backend state when supported."""
        return self.python_backend.dump() if self.python_backend is not None else None

    def load_python_state(self, data: bytes) -> None:
        """Restore Python backend state when supported."""
        if self.python_backend is None:
            raise RuntimeError("No Python backend configured.")
        self.python_backend.load(data)

    def register_python_dataclass(self, cls: type[Any]) -> None:
        """Register a dataclass with the Python backend when supported."""
        if self.python_backend is None:
            raise RuntimeError("No Python backend configured.")
        self.python_backend.register_dataclass(cls)

    async def shell(
        self,
        command: str,
        *,
        timeout: int | None = 120,
        secrets: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        """Run a shell command through the configured sandbox."""
        with self._grant_secrets(secrets):
            output = await self.agent.backend.shell(
                command,
                sandbox=self.sandbox,
                timeout=timeout,
            )
        await self._append("tool", json.dumps(output, sort_keys=True))
        return output

    async def read_file(self, path: str) -> str:
        """Read a file from the session sandbox."""
        return self.sandbox.read_file(path)

    async def write_file(self, path: str, content: str) -> str:
        """Write a file into the session sandbox."""
        return self.sandbox.write_file(path, content)

    async def _ensure_store(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "create table if not exists messages "
                "(id integer primary key autoincrement, role text not null, content text not null)"
            )
            await db.commit()

    async def _append(self, role: str, content: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "insert into messages(role, content) values (?, ?)",
                (role, content),
            )
            await db.commit()

    async def _messages(self) -> list[tuple[str, str]]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "select role, content from messages order by id desc limit 12"
            )
            rows = await cursor.fetchall()
        return list(reversed([(str(role), str(content)) for role, content in rows]))

    async def _history_prompt(self, prompt: str) -> str:
        rows = await self._messages()
        if not rows:
            return prompt
        history = "\n\n".join(f"{role}: {content}" for role, content in rows)
        return f"Conversation so far:\n{history}\n\nNext:\n{prompt}"

    async def _run_backend(
        self,
        prompt: str,
        *,
        model: str | None,
        stream: bool,
    ) -> HarnessResult:
        config = self.agent.config
        if model is not None:
            config = PyFlueConfig(**{**config.__dict__, "model": model})
        return await self.agent.backend.run(
            prompt=prompt,
            system_prompt=self.agent.instructions,
            config=config,
            skills=self.agent.skills,
            sandbox=self.sandbox,
            session_id=self.session_id,
            python_backend=self.python_backend,
            stream=stream,
        )

    @contextmanager
    def _grant_secrets(self, names: list[str] | tuple[str, ...] | None):
        if not names:
            yield
            return
        missing = [name for name in names if name not in self.agent.config.env]
        if missing:
            raise KeyError(f"Unknown secret(s): {', '.join(missing)}")
        env = getattr(self.sandbox, "env", None)
        if not isinstance(env, dict):
            yield
            return
        previous = dict(env)
        try:
            env.update({name: self.agent.config.env[name] for name in names})
            yield
        finally:
            env.clear()
            env.update(previous)

    async def _parse_with_retry(
        self,
        output: HarnessResult,
        result: Any,
        *,
        original_prompt: str,
        model: str | None,
        retries: int,
        stream: bool,
    ) -> Any:
        last_error: Exception | None = None
        current = output
        for attempt in range(max(retries, 0) + 1):
            try:
                return _parse_typed_result(current.text, result)
            except Exception as exc:
                last_error = exc
                if attempt >= retries:
                    break
                schema = TypeAdapter(result).json_schema()
                repair_prompt = (
                    f"{original_prompt}\n\n"
                    "The previous response failed structured output validation.\n"
                    f"Validation error: {exc}\n\n"
                    "Return only valid JSON between the required result delimiters "
                    "that satisfies this schema:\n"
                    f"{json.dumps(schema, indent=2, sort_keys=True)}"
                )
                current = await self._run_backend(repair_prompt, model=model, stream=stream)
                await self._append("assistant", current.text)
        raise ValueError(f"Structured output validation failed: {last_error}") from last_error

    def _build_prompt(
        self,
        text: str,
        *,
        result: Any | None = None,
        role: str | None = None,
    ) -> str:
        parts = [
            "You are running inside PyFlue, a headless Python agent harness.",
        ]
        if role:
            selected = self.agent.roles.get(role)
            if selected is None:
                available = ", ".join(sorted(self.agent.roles)) or "(none)"
                raise KeyError(f"Unknown role '{role}'. Available roles: {available}")
            parts.append(f"Role: {selected.name}\n{selected.instructions}")
        parts.append(text.strip())
        if result is not None:
            schema = TypeAdapter(result).json_schema()
            parts.extend(
                [
                    "Return the final structured result between these exact delimiters:",
                    RESULT_START,
                    json.dumps(schema, indent=2, sort_keys=True),
                    RESULT_END,
                ]
            )
        return "\n\n".join(parts)


def _parse_typed_result(text: str, result: Any) -> Any:
    matches = list(_RESULT_RE.finditer(text or ""))
    raw = matches[-1].group("body").strip() if matches else text.strip()
    value: Any = raw
    if raw.startswith("{") or raw.startswith("["):
        value = json.loads(raw)
    return TypeAdapter(result).validate_python(value)
