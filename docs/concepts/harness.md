# Agent Harness

An agent is more than a model call. A useful autonomous agent also needs
instructions, tools, state, and a safe workspace.

PyFlue packages these pieces into a Python harness:

1. Load project instructions from `AGENTS.md` and `CLAUDE.md`.
2. Load reusable skills from `.agents/skills`.
3. Create or resume a session.
4. Route the prompt through the selected harness backend.
5. Give the backend controlled access to the sandbox.
6. Persist the result back into the session.

## Default Backend

The default backend is DeepAgents:

```python
agent = await init(
    model="openai:gpt-4o",
    harness="deepagents",
)
```

The DeepAgents backend provides:

- model selection
- system prompt forwarding
- skill source forwarding
- memory source forwarding
- virtual sandbox adapter
- filesystem permissions
- upload and download file transfer methods
- session thread ids

## Pluggable Backends

PyFlue includes a registry so future backends can implement the same public
session API:

```python
from pyflue import register_harness

register_harness("custom", CustomBackend)
```

The current built-in backend names are:

| Backend | Status |
| --- | --- |
| `deepagents` | Implemented |
| `openai_agents` | Extension point |
| `google_adk` | Extension point |
| `pydanticai` | Extension point |

DeepAgents is the default harness for normal PyFlue projects. The other names
are reserved extension points for teams that want to build a custom backend
while keeping the same PyFlue project layout and session API.
