"""E2B sandbox provider."""

from __future__ import annotations

from typing import Any

from pyflue.sandboxes.base import SandboxPolicy
from pyflue.sandboxes.remote import ShellSandboxMixin


class E2BSandbox(ShellSandboxMixin):
    """Remote Linux sandbox backed by E2B."""

    provider = "e2b"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        sandbox: Any | None = None,
        policy: SandboxPolicy | None = None,
        workspace: str = "/workspace",
        options: dict[str, Any] | None = None,
    ):
        super().__init__(policy=policy)
        self.workspace = workspace
        self.sandbox = sandbox or self._create_sandbox(api_key=api_key, options=options or {})

    @property
    def id(self) -> str:
        return str(getattr(self.sandbox, "sandbox_id", getattr(self.sandbox, "id", "e2b")))

    def _create_sandbox(self, *, api_key: str | None, options: dict[str, Any]) -> Any:
        try:
            from e2b import Sandbox
        except Exception as exc:
            raise ImportError(
                "E2B sandbox support requires the E2B Python SDK. "
                "Install with: pip install 'pyflue[e2b]'"
            ) from exc
        if api_key:
            return Sandbox(api_key=api_key, **options)
        return Sandbox(**options)

    def _run_provider(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        target = self.sandbox
        if hasattr(target, "commands") and hasattr(target.commands, "run"):
            raw = target.commands.run(command, timeout=timeout)
        elif hasattr(target, "run_code"):
            raw = target.run_code(command, timeout=timeout)
        elif hasattr(target, "run"):
            raw = target.run(command, timeout=timeout)
        else:
            raise RuntimeError("Unsupported E2B sandbox object: missing commands.run/run API.")
        return _normalize_result(raw)


def _normalize_result(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {
            "stdout": str(raw.get("stdout", raw.get("output", "")) or ""),
            "stderr": str(raw.get("stderr", raw.get("error", "")) or ""),
            "exit_code": int(raw.get("exit_code", raw.get("exitCode", raw.get("code", 0))) or 0),
        }
    return {
        "stdout": str(getattr(raw, "stdout", getattr(raw, "output", "")) or ""),
        "stderr": str(getattr(raw, "stderr", getattr(raw, "error", "")) or ""),
        "exit_code": int(getattr(raw, "exit_code", getattr(raw, "exitCode", getattr(raw, "code", 0))) or 0),
    }
