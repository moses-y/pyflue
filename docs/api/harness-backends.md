# Harness Backends

PyFlue uses a backend registry so the public session API can stay stable while
the runtime implementation changes.

## Built-In Backends

| Backend | Status | Package line |
| --- | --- | --- |
| `deepagents` | Implemented | `deepagents>=0.5.6,<0.6.0` |
| `openai_agents` | Planned | `openai-agents>=0.15.1,<0.16.0` |
| `google_adk` | Planned | `google-adk>=1.32.0,<1.33.0` |
| `pydanticai` | Planned | `pydantic-ai>=1.89.1,<1.90.0` |

## DeepAgents Backend

The DeepAgents backend is the default:

```python
agent = await init(harness="deepagents")
```

It currently passes these values into the backend:

- model
- system prompt
- skill source paths
- memory source paths
- sandbox backend adapter
- filesystem permissions
- session thread id

## Custom Backend Registration

```python
from pyflue import register_harness
from pyflue.harnesses.base import HarnessBackend


class CustomBackend(HarnessBackend):
    name = "custom"

    async def run(self, **kwargs):
        ...


register_harness("custom", CustomBackend)
```

Then use it:

```python
agent = await init(harness="custom")
```

## Planned Backends

The OpenAI Agents SDK, Google ADK, and Pydantic AI backends are registered and
dependency-pinned, but their runtime methods currently raise a clear planned
backend error. This prevents silent fallback and keeps the implementation honest.
