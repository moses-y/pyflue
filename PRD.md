# PyFlue Product Requirements Document

Version: 0.1 implementation draft  
Date: 2026-05-02  
Status: Ready for coding-agent implementation

## Vision

PyFlue is a Python-native agent harness framework inspired by the modern
Markdown-first agent framework pattern. It gives Python developers a low
boilerplate way to build autonomous agents with sessions, skills, typed
outputs, sandboxed filesystem access, shell execution, and deployable HTTP
entry points.

The default harness backend is DeepAgents. PyFlue must not expose low-level
graph concepts to users. The public mental model is:

```python
agent = await init(model="openai:gpt-4o", harness="deepagents")
session = await agent.session("issue-123")
result = await session.skill("triage", args={...}, result=MyModel)
```

## Goals

1. Provide a Markdown-first agent framework for Python.
2. Default to DeepAgents for the best batteries-included harness experience.
3. Support a pluggable harness registry for OpenAI Agents SDK, Google ADK,
   Pydantic AI, and custom future backends.
4. Provide a zero-config virtual sandbox for local development.
5. Persist sessions by default.
6. Use Pydantic for typed outputs.
7. Provide a user-facing CLI: `pyflue init`, `pyflue run`, `pyflue dev`,
   `pyflue build`, `pyflue deploy`, and `pyflue skill new`.

## Non-Goals

1. No JavaScript or TypeScript runtime.
2. No low-level graph API in public examples.
3. No built-in terminal UI in v0.1.
4. No remote sandbox implementation in v0.1; define the config shape and keep
   the virtual sandbox working first.

## Users

- Python application developers building service agents.
- Data and ML teams that need Python libraries inside agent workflows.
- Agent developers who want Markdown skills rather than framework boilerplate.
- Teams evaluating different harness runtimes behind one stable API.

## Core Concepts

### Project Instructions

PyFlue loads root `AGENTS.md` and `CLAUDE.md` when present. These become the
base system instructions for the harness backend.

### Skills

Skills live under `.agents/skills/**/*.md`. Each skill uses YAML frontmatter:

```markdown
---
name: triage
description: Triage an issue and decide whether it can be fixed safely.
input_schema:
  type: object
  properties:
    issue_number:
      type: integer
  required: [issue_number]
output_schema:
  type: object
  properties:
    fix_applied:
      type: boolean
    summary:
      type: string
  required: [fix_applied, summary]
---

# Role

You are a senior Python engineer.

## Instructions

Inspect the issue, decide whether it can be fixed safely, and summarize the
result.
```

Acceptance criteria:

- Missing `.agents/skills` is valid and loads zero skills.
- Duplicate skill names are resolved by last path in sorted order.
- Invalid empty names raise a clear `ValueError`.
- Skill prompts include instructions, args, and output schema.

### Sessions

Sessions are SQLite-backed by default under `.pyflue/sessions`. A session must:

- Persist user, assistant, and tool messages.
- Include recent conversation history in future prompts.
- Provide `prompt`, `skill`, `subagent`, `shell`, `read_file`, and `write_file`.

### Sandbox

The default sandbox is `VirtualSandbox`.

Required tools:

- `read_file(path, offset=1, limit=None)`
- `write_file(path, content)`
- `edit_file(path, old, new, replace_all=False)`
- `grep(pattern, path=".", include=None)`
- `glob(pattern)`
- `shell(command, timeout=120)`

Security requirements:

- All paths must stay within the sandbox root.
- Write operations require `allow_write=True`.
- Shell execution requires `allow_shell=True`.
- Shell command allowlists are supported through `SandboxPolicy`.

### Typed Outputs

`session.prompt(..., result=Model)` and `session.skill(..., result=Model)` must
parse and validate the final result using Pydantic v2 `TypeAdapter`.

The model should be instructed to return JSON between:

```text
---RESULT_START---
...
---RESULT_END---
```

### Harness Backends

Backends implement `HarnessBackend.run(...)`.

Built-in backend names:

- `deepagents`: default, implemented first.
- `openai_agents`: planned extension point.
- `google_adk`: planned extension point.
- `pydanticai`: planned extension point.

Users can register custom backends with:

```python
from pyflue import register_harness

register_harness("custom", CustomBackend)
```

### DeepAgents Backend

Requirements:

- Use only public `deepagents.create_deep_agent`.
- Pass model, system prompt, skill sources, memory sources, backend adapter, and
  DeepAgents-managed memory.
- Adapt `VirtualSandbox` to DeepAgents' backend protocol for filesystem and
  shell tools.
- Do not expose low-level graph concepts in user-facing docs or examples.

### CLI

Commands:

- `pyflue init [name] [--force]`
- `pyflue run --prompt TEXT [--session ID] [--allow-write] [--allow-shell]`
- `pyflue dev [--port 2024]`
- `pyflue build`
- `pyflue deploy [--dry-run]`
- `pyflue skill new NAME`

`pyflue init` creates:

```text
AGENTS.md
pyflue.toml
.agents/skills/triage.md
```

### Python Version

PyFlue requires Python 3.11 or newer because the default DeepAgents backend
requires Python 3.11+.

### Dependency Baseline

PyFlue tracks the current public package lines for the supported harnesses:

- `deepagents>=0.5.6,<0.6.0`
- `openai-agents>=0.15.1,<0.16.0` through the `openai` extra
- `google-adk>=1.32.0,<1.33.0` through the `google` extra
- `pydantic-ai>=1.89.1,<1.90.0`, `pydantic-ai-slim>=1.89.1,<1.90.0`, and
  `pydantic-ai-harness[code-mode]` through the `pydanticai` extra

Core dependencies use Pydantic v2.12+, aiosqlite 0.21+, and Python 3.11+.

## Implementation Status

This PRD describes the product direction. The current repository implements the
v0.1 foundation and leaves some harnesses as explicit extension points.

| Area | Status | Notes |
| --- | --- | --- |
| Package metadata and CLI entry point | Implemented | `pyproject.toml` and `pyflue` console script exist. |
| Config loader | Implemented | Loads `pyflue.toml` and agent settings. |
| Markdown skill parser | Implemented | Loads frontmatter skills from `.agents/skills`. |
| Project instructions | Implemented | Loads `AGENTS.md` and `CLAUDE.md`. |
| Virtual sandbox | Implemented | Read, write, edit, grep, glob, shell, path boundary, and policy gates. |
| SQLite sessions | Implemented | Persists message history per session. |
| Typed outputs | Implemented | Uses Pydantic `TypeAdapter` and result delimiters. |
| DeepAgents backend | Implemented | Uses public `create_deep_agent`, skill sources, memory sources, permissions, and sandbox adapter. |
| DeepAgents file transfer protocol | Implemented | Adapter supports upload/download methods used by skills and memory. |
| Harness registry | Implemented | Supports default and custom backend registration. |
| OpenAI Agents SDK backend | Planned | Dependency extra is pinned; backend currently raises a clear planned-backend error. |
| Google ADK backend | Planned | Dependency extra is pinned; backend currently raises a clear planned-backend error. |
| Pydantic AI backend | Planned | Dependency extra is pinned; backend currently raises a clear planned-backend error. |
| `pyflue init` | Implemented | Scaffolds `AGENTS.md`, `pyflue.toml`, and a sample skill. |
| `pyflue run` | Implemented | Runs one prompt through a session. |
| `pyflue skill new` | Implemented | Scaffolds a Markdown skill. |
| `pyflue build` | Partial | Generates starter `Dockerfile` and `app.py`; full FastAPI agent endpoint is planned. |
| `pyflue dev` | Planned | Command exists with placeholder output; hot reload server is not implemented yet. |
| `pyflue deploy` | Planned | Command exists with dry-run placeholder; provider deployment is not implemented yet. |
