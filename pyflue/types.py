"""Shared PyFlue types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

SandboxName = Literal["virtual", "local", "modal", "daytona", "runloop"]


@dataclass(frozen=True)
class Skill:
    """Markdown-defined reusable agent workflow."""

    name: str
    description: str = ""
    instructions: str = ""
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    path: Path | None = None


@dataclass
class PyFlueConfig:
    """Runtime configuration for one PyFlue agent."""

    model: str | None = None
    harness: str = "deepagents"
    sandbox: str = "virtual"
    root: Path = field(default_factory=Path.cwd)
    skills_dir: Path | None = None
    state_dir: Path | None = None
    env: dict[str, str] = field(default_factory=dict)
    harness_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessResult:
    """Normalized response from a harness backend."""

    text: str
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
