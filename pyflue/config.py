"""pyflue.toml loading."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from pyflue.types import PyFlueConfig


def load_config(path: str | Path = "pyflue.toml") -> PyFlueConfig:
    """Load PyFlue configuration from TOML."""
    config_path = Path(path).expanduser()
    root = config_path.parent.resolve() if config_path.exists() else Path.cwd()
    data: dict[str, Any] = {}
    if config_path.exists():
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))

    agent = data.get("agent", {}) if isinstance(data.get("agent"), dict) else {}
    harness = str(agent.get("harness", "deepagents") or "deepagents")
    sandbox = str(agent.get("sandbox", "virtual") or "virtual")
    skills_dir = agent.get("skills_dir")
    state_dir = agent.get("state_dir")

    return PyFlueConfig(
        model=agent.get("model"),
        harness=harness,
        sandbox=sandbox,
        root=root,
        skills_dir=(root / skills_dir).resolve() if skills_dir else None,
        state_dir=(root / state_dir).resolve() if state_dir else None,
        harness_config={
            key: value
            for key, value in data.items()
            if key not in {"agent", "deployment"}
        },
    )
