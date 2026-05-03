# Python API

The Python API centers on `init`, `PyFlueAgent`, and `PyFlueSession`.

## `init`

```python
from pyflue import init

agent = await init(
    model="openai:gpt-4o",
    harness="deepagents",
    sandbox="virtual",
    skills_dir=".agents/skills",
    allow_write=False,
    allow_shell=False,
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

## `PyFlueSession.skill`

```python
result = await session.skill(
    "triage",
    args={"issue_number": 123},
    result=TriageResult,
)
```

## `PyFlueSession.subagent`

```python
result = await session.subagent("Inspect the tests in isolation")
```

The current implementation creates a child PyFlue session with isolated history
and the same sandbox.

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
