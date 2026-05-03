"""Daytona sandbox provider."""

from __future__ import annotations

from typing import Any

from pyflue.sandboxes.base import SandboxPolicy
from pyflue.sandboxes.remote import ShellSandboxMixin


class DaytonaSandbox(ShellSandboxMixin):
    """Remote Linux sandbox backed by Daytona."""

    provider = "daytona"

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
        return str(getattr(self.sandbox, "id", getattr(self.sandbox, "sandbox_id", "daytona")))

    def _create_sandbox(self, *, api_key: str | None, options: dict[str, Any]) -> Any:
        try:
            from daytona_sdk import Daytona
        except Exception as exc:
            raise ImportError(
                "Daytona sandbox support requires the Daytona Python SDK. "
                "Install with: pip install 'pyflue[daytona]'"
            ) from exc
        client = Daytona(api_key=api_key) if api_key else Daytona()
        return client.create(**options)

    def _run_provider(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        target = self.sandbox
        if hasattr(target, "process") and hasattr(target.process, "exec"):
            raw = target.process.exec(command, timeout=timeout)
        elif hasattr(target, "exec"):
            raw = target.exec(command, timeout=timeout)
        elif hasattr(target, "run"):
            raw = target.run(command, timeout=timeout)
        else:
            raise RuntimeError("Unsupported Daytona sandbox object: missing exec/run API.")
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
