"""Python execution backend registry."""

from __future__ import annotations

from pyflue.code.base import PythonBackend
from pyflue.code.monty import MontyPythonBackend
from pyflue.sandboxes.base import SandboxBackend


def create_python_backend(
    name: str | None,
    *,
    sandbox: SandboxBackend | None = None,
) -> PythonBackend | None:
    """Create a Python execution backend by name."""
    if not name:
        return None
    normalized = name.replace("_", "-").lower()
    if normalized == "monty":
        return MontyPythonBackend(sandbox=sandbox)
    raise ValueError(f"Unknown Python backend: {name}")
