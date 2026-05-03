"""Python execution backend interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class PythonRunResult:
    """Normalized result from a Python execution backend."""

    result: Any = None
    stdout: str = ""
    stderr: str = ""
    backend: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PythonBackend(Protocol):
    """Common protocol for safe Python execution backends."""

    name: str

    async def run(
        self,
        code: str,
        *,
        inputs: dict[str, Any] | None = None,
        external_functions: dict[str, Any] | None = None,
        type_check: bool = False,
        type_check_stubs: str | None = None,
        restart: bool = False,
        timeout: float | None = 5.0,
        resource_limits: dict[str, Any] | None = None,
        mount: Any | None = None,
    ) -> PythonRunResult:
        """Execute Python code and return a normalized result."""

    def dump(self) -> bytes | None:
        """Return serialized backend state when supported."""

    def load(self, data: bytes) -> None:
        """Restore serialized backend state when supported."""

    def register_dataclass(self, cls: type[Any]) -> None:
        """Register a dataclass type when supported by the backend."""
