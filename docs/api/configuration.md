# Configuration

PyFlue reads `pyflue.toml` by default.

```toml
[agent]
model = "openai:gpt-4o"
harness = "deepagents"
sandbox = "virtual"
python_backend = "monty"
skills_dir = ".agents/skills"
roles_dir = ".agents/roles"
agents_dir = "agents"
state_dir = ".pyflue/sessions"
allowed_commands = ["git", "pytest"]
allow_compound_commands = false
typed_retries = 3

[sandbox]
workspace = "/workspace"
options = {}
```

## Agent Settings

| Key | Default | Description |
| --- | --- | --- |
| `model` | `None` | Model identifier passed to the backend. |
| `harness` | `deepagents` | Harness backend name. |
| `sandbox` | `virtual` | Sandbox name. |
| `python_backend` | `None` | Optional Python execution backend. Use `monty` for safe host-side Python. |
| `skills_dir` | `.agents/skills` | Markdown skill directory. |
| `roles_dir` | `.agents/roles` | Markdown role directory. |
| `agents_dir` | `agents` | File-based agent route directory. |
| `state_dir` | `.pyflue/sessions` | Session database directory. |
| `allowed_commands` | `[]` | Optional shell command grant list. |
| `allow_compound_commands` | `false` | Allow shell operators such as `&&`, pipes, and redirects. Keep disabled for untrusted workflows. |
| `typed_retries` | `3` | Structured output repair attempts. |

## Secret Grants

Values passed through `env` are treated as secrets. PyFlue keeps them out of
prompts and does not mount them into the virtual sandbox unless a call requests
them.

```python
agent = await init(env={"GITHUB_TOKEN": "..."}, allow_shell=True)
session = await agent.session("issue-123")

await session.shell(
    "python -c 'import os; print(os.getenv(\"GITHUB_TOKEN\"))'",
    secrets=["GITHUB_TOKEN"],
)
```

## Sandbox Settings

The `[sandbox]` table is passed to the selected sandbox provider:

```toml
[agent]
model = "openai:gpt-4o"
sandbox = "daytona"

[sandbox]
workspace = "/workspace"

[sandbox.options]
# provider-specific creation options
```

Provider credentials are passed through `env` in Python code or through normal
environment variables in your process:

```python
agent = await init(
    sandbox="e2b",
    env={"E2B_API_KEY": "..."},
)
```

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
| `daytona` | `daytona-sdk>=0.22.0` |
| `e2b` | `e2b>=2.7.0` |
| `modal` | `modal>=1.3.0` |
| `runloop` | `runloop-api-client>=0.82.0` |
| `sandboxes` | Daytona, E2B, Modal, and Runloop extras |
| `monty` | `pydantic-monty>=0.0.17,<0.0.18` |

Install with extras:

```bash
pip install "pyflue[openai]"
pip install "pyflue[google]"
pip install "pyflue[pydanticai]"
pip install "pyflue[sandboxes]"
pip install "pyflue[monty]"
```

Equivalent `uv` commands:

```bash
uv add "pyflue[openai]"
uv add "pyflue[google]"
uv add "pyflue[pydanticai]"
uv add "pyflue[sandboxes]"
uv add "pyflue[monty]"
```

DeepAgents is the default harness backend. OpenAI Agents SDK, Google ADK, and
Pydantic AI are available as optional package extras for projects that want to
build custom backends against the same PyFlue API.
