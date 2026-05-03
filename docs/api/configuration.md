# Configuration

PyFlue reads `pyflue.toml` by default.

```toml
[agent]
model = "openai:gpt-4o"
harness = "deepagents"
sandbox = "virtual"
skills_dir = ".agents/skills"
state_dir = ".pyflue/sessions"
```

## Agent Settings

| Key | Default | Description |
| --- | --- | --- |
| `model` | `None` | Model identifier passed to the backend. |
| `harness` | `deepagents` | Harness backend name. |
| `sandbox` | `virtual` | Sandbox name. |
| `skills_dir` | `.agents/skills` | Markdown skill directory. |
| `state_dir` | `.pyflue/sessions` | Session database directory. |

## Runtime Overrides

Values passed to `init` override config file values:

```python
agent = await init(
    config_path="pyflue.toml",
    model="openai:gpt-4o-mini",
    harness="deepagents",
)
```

## Dependency Extras

PyFlue tracks the current supported package lines:

| Extra | Packages |
| --- | --- |
| default | `deepagents==0.5.6` through `>=0.5.6,<0.6.0` |
| `openai` | `openai-agents>=0.15.1,<0.16.0` |
| `google` | `google-adk>=1.32.0,<1.33.0` |
| `pydanticai` | `pydantic-ai>=1.89.1,<1.90.0` |

Install with extras:

```bash
pip install "pyflue[openai]"
pip install "pyflue[google]"
pip install "pyflue[pydanticai]"
```

The non-DeepAgents backends are planned extension points in the current
implementation.
