"""Runloop sandbox provider."""

from __future__ import annotations

from typing import Any

from pyflue.sandboxes.base import SandboxPolicy
from pyflue.sandboxes.remote import ShellSandboxMixin


class RunloopSandbox(ShellSandboxMixin):
    """Remote Linux sandbox backed by a Runloop devbox."""

    provider = "runloop"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        devbox: Any | None = None,
        policy: SandboxPolicy | None = None,
        workspace: str = "/workspace",
        options: dict[str, Any] | None = None,
    ):
        super().__init__(policy=policy)
        self.workspace = workspace
        self.devbox = devbox or self._create_devbox(api_key=api_key, options=options or {})

    @property
    def id(self) -> str:
        return str(getattr(self.devbox, "id", getattr(self.devbox, "devbox_id", "runloop")))

    def _create_devbox(self, *, api_key: str | None, options: dict[str, Any]) -> Any:
        try:
            from runloop_api_client import Runloop
        except Exception as exc:
            raise ImportError(
                "Runloop sandbox support requires the Runloop Python SDK. "
                "Install with: pip install 'pyflue[runloop]'"
            ) from exc
        client = Runloop(api_key=api_key) if api_key else Runloop()
        devboxes = getattr(client, "devboxes", None)
        if devboxes is None or not hasattr(devboxes, "create"):
            raise RuntimeError("Unsupported Runloop client object: missing devboxes.create API.")
        return devboxes.create(**options)

    def _run_provider(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        target = self.devbox
        if hasattr(target, "exec"):
            raw = target.exec(command, timeout=timeout)
        elif hasattr(target, "execute"):
            raw = target.execute(command, timeout=timeout)
        elif hasattr(target, "run"):
            raw = target.run(command, timeout=timeout)
        else:
            raise RuntimeError("Unsupported Runloop devbox object: missing exec/execute/run API.")
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
