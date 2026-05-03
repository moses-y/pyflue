# Sessions

Sessions give an agent persistent conversation history.

```python
session = await agent.session("issue-123")
```

If a session already exists, PyFlue resumes it. If it does not exist, PyFlue
creates it.

## Storage

Sessions are stored as SQLite databases under:

```text
.pyflue/sessions
```

Each session stores:

- user messages
- assistant messages
- tool messages

## Prompt History

PyFlue includes recent session history in future turns:

```python
await session.prompt("Inspect the failure")
await session.prompt("Now suggest the smallest fix")
```

The second prompt includes the recent conversation so the harness can continue
from the same context.

## Session Methods

| Method | Status | Purpose |
| --- | --- | --- |
| `prompt(text, result=None, role=None, model=None)` | Implemented | Run a direct prompt. |
| `skill(name, args=None, result=None, role=None, model=None)` | Implemented | Run a Markdown skill. |
| `task(prompt, result=None, role=None, model=None)` | Implemented | Run an isolated child task using the same sandbox. |
| `subagent(prompt, result=None)` | Implemented | Alias-style helper for child sessions. |
| `shell(command, timeout=120)` | Implemented | Run shell through sandbox policy. |
| `read_file(path)` | Implemented | Read a sandbox file. |
| `write_file(path, content)` | Implemented | Write a sandbox file when enabled. |

## Tasks

Tasks give you a child history while keeping the same sandbox:

```python
result = await session.task(
    "Inspect only the failing tests",
    role="coder",
)
```

This is useful when the parent agent needs focused work without mixing every
intermediate step into the parent conversation.
