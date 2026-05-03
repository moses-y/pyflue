"""Modal sandbox provider."""

from __future__ import annotations

from typing import Any

from pyflue.sandboxes.base import SandboxPolicy
from pyflue.sandboxes.remote import ShellSandboxMixin


class ModalSandbox(ShellSandboxMixin):
    """Remote Linux sandbox backed by Modal Sandbox."""

    provider = "modal"

    def __init__(
        self,
        *,
        sandbox: Any | None = None,
        policy: SandboxPolicy | None = None,
        workspace: str = "/workspace",
        options: dict[str, Any] | None = None,
    ):
        super().__init__(policy=policy)
        self.workspace = workspace
        self.sandbox = sandbox or self._create_sandbox(options=options or {})

    @property
    def id(self) -> str:
        return str(getattr(self.sandbox, "object_id", getattr(self.sandbox, "id", "modal")))

    def _create_sandbox(self, *, options: dict[str, Any]) -> Any:
        try:
            import modal
        except Exception as exc:
            raise ImportError(
                "Modal sandbox support requires the Modal Python SDK. "
                "Install with: pip install 'pyflue[modal]'"
            ) from exc
        return modal.Sandbox.create(**options)

    def _run_provider(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        target = self.sandbox
        if not hasattr(target, "exec"):
            raise RuntimeError("Unsupported Modal sandbox object: missing exec API.")
        process = target.exec("bash", "-lc", command, timeout=timeout)
        stdout = _read_stream(getattr(process, "stdout", ""))
        stderr = _read_stream(getattr(process, "stderr", ""))
        if hasattr(process, "wait"):
            exit_code = process.wait()
        else:
            exit_code = getattr(process, "returncode", 0)
        return {"stdout": stdout, "stderr": stderr, "exit_code": int(exit_code or 0)}


def _read_stream(stream: Any) -> str:
    if stream is None:
        return ""
    if isinstance(stream, str):
        return stream
    if hasattr(stream, "read"):
        data = stream.read()
        return data.decode() if isinstance(data, bytes) else str(data or "")
    return str(stream)
