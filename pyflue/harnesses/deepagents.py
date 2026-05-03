"""DeepAgents harness backend."""

from __future__ import annotations

import asyncio
from typing import Any

from pyflue.harnesses.base import HarnessBackend
from pyflue.sandboxes.base import SandboxBackend
from pyflue.types import HarnessResult, PyFlueConfig, Skill


class DeepAgentsBackend(HarnessBackend):
    """Default PyFlue harness powered by the public DeepAgents API."""

    name = "deepagents"

    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        config: PyFlueConfig,
        skills: dict[str, Skill],
        sandbox: Any,
        session_id: str,
        python_backend: Any | None = None,
        stream: bool = False,
    ) -> HarnessResult:
        try:
            from deepagents import create_deep_agent
        except Exception as exc:
            raise ImportError(
                "The DeepAgents backend requires the 'deepagents' package. "
                "Install with: pip install pyflue"
            ) from exc

        backend = _DeepAgentsSandboxBackend(sandbox) if _is_pyflue_sandbox(sandbox) else None
        skill_sources = _skill_sources(config)
        memory = _memory_sources(config)
        agent = create_deep_agent(
            model=config.model,
            tools=_tools(python_backend),
            system_prompt=system_prompt or None,
            backend=backend,
            skills=skill_sources or None,
            memory=memory or None,
            permissions=_permissions(sandbox),
            checkpointer=True,
            name="pyflue",
        )
        inputs = {"messages": [{"role": "user", "content": prompt}]}
        run_config = {"configurable": {"thread_id": session_id}}
        if hasattr(agent, "ainvoke"):
            raw = await agent.ainvoke(inputs, config=run_config)
        else:
            raw = await asyncio.to_thread(agent.invoke, inputs, config=run_config)
        return HarnessResult(
            text=_extract_text(raw),
            raw=raw,
            metadata={
                "harness": self.name,
                "skill_count": len(skills),
                "skill_sources": skill_sources,
                "memory": memory,
                "stream": stream,
            },
        )


class _DeepAgentsSandboxBackend:
    """Adapter from PyFlue sandboxes to DeepAgents' public backend protocol."""

    def __init__(self, sandbox: SandboxBackend):
        self.sandbox = sandbox

    @property
    def id(self) -> str:
        return self.sandbox.id

    def ls(self, path: str) -> Any:
        from deepagents.backends.protocol import LsResult

        try:
            entries = []
            for child in self.sandbox.list_files(_from_backend_path(path)):
                entries.append(
                    {
                        "path": child.path,
                        "is_dir": child.is_dir,
                        "size": child.size,
                    }
                )
            return LsResult(entries=entries)
        except Exception as exc:
            return LsResult(error=str(exc))

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> Any:
        from deepagents.backends.protocol import ReadResult

        try:
            content = self.sandbox.read_file(_from_backend_path(file_path), offset=offset + 1, limit=limit)
            return ReadResult(file_data={"content": content, "encoding": "utf-8"})
        except Exception as exc:
            return ReadResult(error=str(exc))

    def write(self, file_path: str, content: str) -> Any:
        from deepagents.backends.protocol import WriteResult

        try:
            self.sandbox.write_file(_from_backend_path(file_path), content)
            return WriteResult(path=file_path)
        except Exception as exc:
            return WriteResult(error=str(exc))

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> Any:
        from deepagents.backends.protocol import EditResult

        try:
            self.sandbox.edit_file(
                _from_backend_path(file_path),
                old_string,
                new_string,
                replace_all=replace_all,
            )
            return EditResult(path=file_path)
        except Exception as exc:
            return EditResult(error=str(exc))

    def grep(self, pattern: str, path: str | None = None, glob: str | None = None) -> Any:
        from deepagents.backends.protocol import GrepResult

        try:
            output = self.sandbox.grep(pattern, path=_from_backend_path(path or "/"), include=glob)
            matches = []
            for line in output.splitlines():
                file_path, _, rest = line.partition(":")
                line_no, _, text = rest.partition(":")
                if file_path and line_no.isdigit():
                    normalized = file_path if file_path.startswith("/") else "/" + file_path
                    matches.append({"path": normalized, "line": int(line_no), "text": text})
            return GrepResult(matches=matches)
        except Exception as exc:
            return GrepResult(error=str(exc))

    def glob(self, pattern: str, path: str = "/") -> Any:
        from deepagents.backends.protocol import GlobResult

        try:
            base = _from_backend_path(path)
            search = pattern if base == "." else f"{base.rstrip('/')}/{pattern}"
            matches = []
            for item in self.sandbox.glob(search).splitlines():
                matches.append(
                    {
                        "path": item if item.startswith("/") else "/" + item,
                        "is_dir": False,
                        "size": 0,
                    }
                )
            return GlobResult(matches=matches)
        except Exception as exc:
            return GlobResult(error=str(exc))

    def execute(self, command: str, *, timeout: int | None = None) -> Any:
        from deepagents.backends.protocol import ExecuteResponse

        try:
            result = self.sandbox.shell(command, timeout=timeout)
            output = "\n".join(part for part in [result["stdout"], result["stderr"]] if part)
            return ExecuteResponse(output=output.strip(), exit_code=result["exit_code"], truncated=False)
        except Exception as exc:
            return ExecuteResponse(output=str(exc), exit_code=-1, truncated=False)

    def upload_files(self, files: list[tuple[str, bytes]]) -> Any:
        from deepagents.backends.protocol import FileUploadResponse

        responses = []
        for path, content in files:
            try:
                self.sandbox.write_file(
                    _from_backend_path(path),
                    content.decode("utf-8", errors="replace"),
                )
                responses.append(FileUploadResponse(path=path))
            except Exception as exc:
                responses.append(FileUploadResponse(path=path, error=str(exc)))
        return responses

    def download_files(self, paths: list[str]) -> Any:
        from deepagents.backends.protocol import FileDownloadResponse

        responses = []
        for path in paths:
            try:
                content = self.sandbox.read_file(_from_backend_path(path))
                responses.append(FileDownloadResponse(path=path, content=content.encode()))
            except FileNotFoundError:
                responses.append(FileDownloadResponse(path=path, error="file_not_found"))
            except PermissionError:
                responses.append(FileDownloadResponse(path=path, error="permission_denied"))
            except Exception as exc:
                responses.append(FileDownloadResponse(path=path, error=str(exc)))
        return responses


def _skill_sources(config: PyFlueConfig) -> list[str]:
    directory = config.skills_dir or config.root / ".agents" / "skills"
    return ["/" + directory.resolve().relative_to(config.root.resolve()).as_posix()] if directory.exists() else []


def _memory_sources(config: PyFlueConfig) -> list[str]:
    sources = []
    for name in ["AGENTS.md", "CLAUDE.md"]:
        if (config.root / name).exists():
            sources.append(f"/{name}")
    return sources


def _permissions(sandbox: Any) -> Any:
    if not _is_pyflue_sandbox(sandbox):
        return None
    try:
        from deepagents import FilesystemPermission
    except Exception:
        return None
    if getattr(sandbox, "policy", None) and sandbox.policy.allow_write:
        return [FilesystemPermission(operations=["read", "write"], paths=["/**"])]
    return [
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        FilesystemPermission(operations=["read"], paths=["/**"]),
    ]


def _tools(python_backend: Any | None) -> list[Any]:
    tools: list[Any] = []
    if python_backend is None:
        return tools

    async def run_code(code: str) -> str:
        """Run Python code in the configured PyFlue Python backend."""
        result = await python_backend.run(code)
        parts = []
        if result.stdout:
            parts.append("stdout:\n" + result.stdout)
        parts.append("result:\n" + repr(result.result))
        if result.stderr:
            parts.append("stderr:\n" + result.stderr)
        return "\n\n".join(parts)

    tools.append(run_code)
    return tools


def _extract_text(raw: Any) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        messages = raw.get("messages")
        if isinstance(messages, list) and messages:
            last = messages[-1]
            return str(getattr(last, "content", last.get("content") if isinstance(last, dict) else last)).strip()
    for attr in ["output", "final_output", "content", "text"]:
        if hasattr(raw, attr):
            return str(getattr(raw, attr)).strip()
    return str(raw).strip()


def _from_backend_path(path: str | None) -> str:
    raw = str(path or "/").strip() or "/"
    if raw in {"/", "/workspace"}:
        return "."
    if raw.startswith("/workspace/"):
        return raw.removeprefix("/workspace/")
    if raw.startswith("/"):
        return raw[1:]
    return raw


def _is_pyflue_sandbox(sandbox: Any) -> bool:
    return all(
        hasattr(sandbox, name)
        for name in [
            "list_files",
            "read_file",
            "write_file",
            "edit_file",
            "grep",
            "glob",
            "shell",
        ]
    )
