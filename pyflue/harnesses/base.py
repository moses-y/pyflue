"""Harness backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pyflue.types import HarnessResult, PyFlueConfig, Skill


class HarnessBackend(ABC):
    """Backend contract implemented by all harness integrations."""

    name: str

    @abstractmethod
    async def run(
        self,
        *,
        prompt: str,
        system_prompt: str,
        config: PyFlueConfig,
        skills: dict[str, Skill],
        sandbox: Any,
        session_id: str,
    ) -> HarnessResult:
        """Run one prompt turn."""

    async def shell(self, command: str, *, sandbox: Any, timeout: int | None = None) -> dict[str, Any]:
        """Run a shell command through the configured sandbox."""
        return sandbox.shell(command, timeout=timeout)
