# Python API

The Python API centers on `init`, `PyFlueAgent`, and `PyFlueSession`.

## `init`

```python
from pyflue import init

agent = await init(
    model="openai:gpt-5.5",
    harness="deepagents",
    sandbox="virtual",
    skills_dir=".agents/skills",
    allow_write=False,
    allow_shell=False,
    allowed_commands=("pytest", "git"),
)
```

Parameters:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `model` | `str | None` | config value | Model identifier passed to the backend. |
| `harness` | `str | None` | `deepagents` | Harness backend name. |
| `sandbox` | `str | None` | `virtual` | Sandbox name. |
| `skills_dir` | `str | Path | None` | `.agents/skills` | Skill directory. |
| `config_path` | `str | Path | None` | `pyflue.toml` | Config file path. |
| `env` | `dict[str, str] | None` | `{}` | Runtime environment metadata. |
| `allow_write` | `bool` | `False` | Enable sandbox writes. |
| `allow_shell` | `bool` | `False` | Enable sandbox shell execution. |
| `allowed_commands` | `tuple[str, ...] \| list[str] \| None` | config value | Optional command grant list. |
| `allow_compound_commands` | `bool \| None` | config value | Allow shell operators and redirects. |

## `PyFlueAgent.session`

```python
session = await agent.session("issue-123")
```

If no session id is supplied, PyFlue uses `default`.

## `PyFlueSession.prompt`

```python
result = await session.prompt("Summarize this repository")
print(result.text)
```

With typed output:

```python
result = await session.prompt(
    "Return a JSON triage result",
    result=TriageResult,
)
```

Use a role:

```python
result = await session.prompt(
    "Review this patch",
    role="coder",
)
```

Override the model for a single call:

```python
result = await session.prompt(
    "Use a larger model for this review",
    model="openai:gpt-5.5",
)
```

## `PyFlueSession.skill`

```python
result = await session.skill(
    "triage",
    args={"issue_number": 123},
    result=TriageResult,
)
```

## `PyFlueSession.stream`

```python
async for event in session.stream("Review this project"):
    print(event.type, event.data)
```

The stream emits normalized events:

```text
start
delta
end
error
```

## `PyFlueSession.subagent`

```python
result = await session.subagent("Inspect the tests in isolation")
```

`subagent` creates a child PyFlue session with isolated history and the same
sandbox.

## `PyFlueSession.task`

```python
result = await session.task(
    "Analyze the data files",
    role="data_analyst",
)
```

`task` is the Flue-style child-agent primitive. It shares the parent sandbox
and uses an isolated child history.

## Python Backend

When a Python backend is configured, use `run_python`:

```python
result = await session.run_python(
    "sum(items)",
    inputs={"items": [1, 2, 3]},
)
```

## Filesystem Helpers

```python
content = await session.read_file("README.md")
await session.write_file("report.txt", "Summary")
```

Writes require `allow_write=True`.

## Shell Helper

```python
result = await session.shell("pytest -q")
print(result["stdout"])
```

Shell execution requires `allow_shell=True`.

Grant secrets only for the command that needs them:

```python
await session.shell(
    "python -c 'import os; print(os.getenv(\"TOKEN\"))'",
    secrets=["TOKEN"],
)
```
