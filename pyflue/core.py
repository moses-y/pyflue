"""PyFlue core agent and session API."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

import aiosqlite
from pydantic import BaseModel, TypeAdapter

from pyflue.config import load_config
from pyflue.harnesses.registry import create_backend
from pyflue.sandbox import SandboxPolicy, VirtualSandbox
from pyflue.skills import load_project_instructions, load_skills, render_skill_prompt
from pyflue.types import HarnessResult, PyFlueConfig

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
    skills_dir: str | Path | None = None,
    config_path: str | Path | None = None,
    env: dict[str, str] | None = None,
    allow_write: bool = False,
    allow_shell: bool = False,
) -> PyFlueAgent:
    """Initialize a PyFlue agent."""
    config = load_config(config_path or "pyflue.toml")
    if model is not None:
        config.model = model
    if harness is not None:
        config.harness = harness
    if sandbox is not None:
        config.sandbox = sandbox
    if skills_dir is not None:
        path = Path(skills_dir).expanduser()
        config.skills_dir = path if path.is_absolute() else config.root / path
    if env:
        config.env.update({str(key): str(value) for key, value in env.items()})
    return PyFlueAgent(
        config=config,
        sandbox_policy=SandboxPolicy(allow_write=allow_write, allow_shell=allow_shell),
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
        self.sandbox = VirtualSandbox(config.root, policy=sandbox_policy)
        self.state_dir = config.state_dir or config.root / ".pyflue" / "sessions"
        self.state_dir.mkdir(parents=True, exist_ok=True)

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
        self.db_path = self.agent.state_dir / f"{safe_id}.sqlite3"

    async def prompt(
        self,
        text: str,
        *,
        result: type[BaseModel] | Any | None = None,
    ) -> HarnessResult | Any:
        """Run one prompt turn."""
        prompt = self._build_prompt(text, result=result)
        await self._append("user", text)
        history = await self._history_prompt(prompt)
        output = await self.agent.backend.run(
            prompt=history,
            system_prompt=self.agent.instructions,
            config=self.agent.config,
            skills=self.agent.skills,
            sandbox=self.agent.sandbox,
            session_id=self.session_id,
        )
        await self._append("assistant", output.text)
        if result is not None:
            return _parse_typed_result(output.text, result)
        return output

    async def skill(
        self,
        name: str,
        *,
        args: dict[str, Any] | None = None,
        result: type[BaseModel] | Any | None = None,
    ) -> HarnessResult | Any:
        """Run a Markdown-defined skill."""
        skill = self.agent.skills.get(name)
        if skill is None:
            available = ", ".join(sorted(self.agent.skills)) or "(none)"
            raise KeyError(f"Unknown skill '{name}'. Available skills: {available}")
        prompt = render_skill_prompt(skill, args=args)
        return await self.prompt(prompt, result=result)

    async def subagent(
        self,
        prompt: str,
        *,
        result: type[BaseModel] | Any | None = None,
    ) -> HarnessResult | Any:
        """Run a child session with isolated history and shared sandbox."""
        child_id = f"{self.session_id}:task:{uuid.uuid4().hex[:10]}"
        child = await self.agent.session(child_id)
        output = await child.prompt(prompt, result=result)
        await self._append("assistant", f"Subagent {child_id} completed.")
        return output

    async def shell(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        """Run a shell command through the configured sandbox."""
        output = await self.agent.backend.shell(
            command,
            sandbox=self.agent.sandbox,
            timeout=timeout,
        )
        await self._append("tool", json.dumps(output, sort_keys=True))
        return output

    async def read_file(self, path: str) -> str:
        """Read a file from the session sandbox."""
        return self.agent.sandbox.read_file(path)

    async def write_file(self, path: str, content: str) -> str:
        """Write a file into the session sandbox."""
        return self.agent.sandbox.write_file(path, content)

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

    def _build_prompt(self, text: str, *, result: Any | None = None) -> str:
        parts = [
            "You are running inside PyFlue, a headless Python agent harness.",
            text.strip(),
        ]
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
