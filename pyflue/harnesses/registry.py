"""Harness backend registry."""

from __future__ import annotations

from collections.abc import Callable

from pyflue.harnesses.base import HarnessBackend

_REGISTRY: dict[str, Callable[[], HarnessBackend]] = {}


def register_harness(name: str, factory: Callable[[], HarnessBackend]) -> None:
    """Register a harness backend factory."""
    key = _normalize(name)
    if not key:
        raise ValueError("Harness name cannot be empty.")
    _REGISTRY[key] = factory


def create_backend(name: str) -> HarnessBackend:
    """Create a backend by name."""
    _ensure_defaults()
    key = _normalize(name)
    if key not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown harness backend '{name}'. Available: {available}")
    return _REGISTRY[key]()


def _normalize(name: str) -> str:
    return str(name or "").strip().lower().replace("-", "_")


def _ensure_defaults() -> None:
    if _REGISTRY:
        return
    from pyflue.harnesses.deepagents import DeepAgentsBackend
    from pyflue.harnesses.google_adk import GoogleADKBackend
    from pyflue.harnesses.openai_agents import OpenAIAgentsBackend
    from pyflue.harnesses.pydanticai import PydanticAIBackend

    register_harness("deepagents", DeepAgentsBackend)
    register_harness("openai_agents", OpenAIAgentsBackend)
    register_harness("google_adk", GoogleADKBackend)
    register_harness("pydanticai", PydanticAIBackend)
