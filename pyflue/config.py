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
    python_backend = agent.get("python_backend")
    skills_dir = agent.get("skills_dir")
    roles_dir = agent.get("roles_dir")
    agents_dir = agent.get("agents_dir")
    state_dir = agent.get("state_dir")
    allowed_commands = agent.get("allowed_commands", ())
    allow_compound_commands = bool(agent.get("allow_compound_commands", False))
    typed_retries = int(agent.get("typed_retries", 3) or 0)

    return PyFlueConfig(
        model=agent.get("model"),
        harness=harness,
        sandbox=sandbox,
        python_backend=str(python_backend) if python_backend else None,
        root=root,
        skills_dir=(root / skills_dir).resolve() if skills_dir else None,
        roles_dir=(root / roles_dir).resolve() if roles_dir else None,
        agents_dir=(root / agents_dir).resolve() if agents_dir else None,
        state_dir=(root / state_dir).resolve() if state_dir else None,
        allowed_commands=tuple(str(item) for item in allowed_commands),
        allow_compound_commands=allow_compound_commands,
        typed_retries=typed_retries,
        harness_config={
            key: value
            for key, value in data.items()
            if key not in {"agent", "deployment"}
        },
    )
