# PyFlue

[![CI](https://github.com/SuperagenticAI/pyflue/actions/workflows/ci.yml/badge.svg)](https://github.com/SuperagenticAI/pyflue/actions/workflows/ci.yml)
[![Docs](https://github.com/SuperagenticAI/pyflue/actions/workflows/docs.yml/badge.svg)](https://github.com/SuperagenticAI/pyflue/actions/workflows/docs.yml)

PyFlue is a Python-first agent harness framework with Markdown skills,
stateful sessions, sandboxed filesystem/shell access, typed Pydantic outputs,
and pluggable harness backends.

PyFlue is inspired by Flue's agent harness model and adapts the same broad
developer experience for Python projects.

The default backend is DeepAgents. Other harnesses are represented behind the
same PyFlue API so users can switch later without rewriting skills or sessions.

## Quick Start

Add PyFlue to a project with `uv`:

```bash
uv add pyflue
```

Or install it with `pip`:

```bash
pip install pyflue
```

Then scaffold and run an agent:

```bash
pyflue init my-agent
cd my-agent
pyflue run --prompt "Review this project"
```

## Python API

```python
from pydantic import BaseModel
from pyflue import init


class FixResult(BaseModel):
    fix_applied: bool
    summary: str


async def main():
    agent = await init(
        model="openai:gpt-4o",
        harness="deepagents",
        sandbox="virtual",
        allow_write=True,
        allow_shell=True,
    )
    session = await agent.session("fix-123")
    result = await session.skill(
        "triage",
        args={"issue_number": 123},
        result=FixResult,
    )
    if result.fix_applied:
        await session.shell("git status --short")
```

## Harness Backends

| Backend | Status | Use case |
| --- | --- | --- |
| `deepagents` | Default | Coding/research agents with skills, files, shell, and subagents. |
| `openai_agents` | Planned | OpenAI-native agent workflows. |
| `google_adk` | Planned | Google/Gemini-oriented agent workflows. |
| `pydanticai` | Planned | Type-safe service agents. |

## Project Layout

```text
AGENTS.md
pyflue.toml
.agents/
  skills/
    triage.md
```

## Flue-Inspired Feature Mapping

| Concept | PyFlue |
| --- | --- |
| `AGENTS.md` | Root project instructions loaded into the harness. |
| Markdown skills | `.agents/skills/*.md` parsed with frontmatter. |
| Sessions | SQLite-backed session history under `.pyflue/sessions`. |
| Sandbox | `VirtualSandbox` by default; remote providers planned. |
| Typed outputs | Pydantic v2 validation. |
| CLI | `pyflue init`, `pyflue run`, `pyflue dev`, `pyflue build`. |
| Deployment | Docker/FastAPI, GitHub Actions, GitLab CI, Railway, Render, and Fly.io artifact generation. |

## Status

The DeepAgents backend is the primary runtime. OpenAI Agents SDK, Google ADK,
and Pydantic AI are exposed as planned extension points behind the same public
PyFlue API.

## Development

```bash
uv sync --extra dev --extra docs
uv run --extra dev ruff check .
uv run --extra dev pytest
uv run --extra docs mkdocs build --strict
uv build
```
