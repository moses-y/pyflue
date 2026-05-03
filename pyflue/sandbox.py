"""Backward-compatible sandbox imports."""

from pyflue.sandboxes.base import SandboxFileInfo, SandboxPolicy
from pyflue.sandboxes.virtual import VirtualSandbox

__all__ = ["SandboxFileInfo", "SandboxPolicy", "VirtualSandbox"]
