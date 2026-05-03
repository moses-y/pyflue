"""OpenAI Agents SDK backend placeholder."""

from __future__ import annotations

from typing import Any

from pyflue.harnesses.base import HarnessBackend
from pyflue.types import HarnessResult, PyFlueConfig, Skill


class OpenAIAgentsBackend(HarnessBackend):
    """Optional backend for OpenAI Agents SDK."""

    name = "openai_agents"

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
        raise NotImplementedError(
            "OpenAI Agents SDK backend is planned. Use harness='deepagents' for v0.1."
        )
