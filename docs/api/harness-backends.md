# Harness Backends

PyFlue uses a backend registry so the public session API can stay stable while
teams can choose the harness runtime that fits their project.

## Built-In Backends

| Backend | Status | Package line |
| --- | --- | --- |
| `deepagents` | Implemented | `deepagents>=0.5.6,<0.6.0` |
| `openai_agents` | Extension point | `openai-agents>=0.15.1,<0.16.0` |
| `google_adk` | Extension point | `google-adk>=1.32.0,<1.33.0` |
| `pydanticai` | Extension point | `pydantic-ai>=1.89.1,<1.90.0` |

## DeepAgents Backend

The DeepAgents backend is the default:

```python
agent = await init(harness="deepagents")
```

The DeepAgents backend provides:

- model
- project instructions
- Markdown skills
- session continuity
- sandbox file tools
- shell execution through policy
- task-friendly agent behavior
- optional Python code tool when Monty is enabled

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

## Optional Backends

OpenAI Agents SDK, Google ADK, and Pydantic AI are available as optional package
extras for teams that want to build custom backends behind the PyFlue API.

```bash
uv add "pyflue[openai]"
uv add "pyflue[google]"
uv add "pyflue[pydanticai]"
```

```bash
pip install "pyflue[openai]"
pip install "pyflue[google]"
pip install "pyflue[pydanticai]"
```
