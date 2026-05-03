from __future__ import annotations

import pytest

from pyflue.harnesses.registry import create_backend


def test_default_registry_resolves_deepagents():
    assert create_backend("deepagents").name == "deepagents"


def test_planned_backends_are_registered():
    assert create_backend("openai-agents").name == "openai_agents"
    assert create_backend("google-adk").name == "google_adk"
    assert create_backend("pydanticai").name == "pydanticai"


def test_unknown_backend_error_lists_available():
    with pytest.raises(KeyError, match="Available"):
        create_backend("missing")
