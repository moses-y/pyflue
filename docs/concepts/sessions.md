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
| `prompt(text, result=None)` | Implemented | Run a direct prompt. |
| `skill(name, args=None, result=None)` | Implemented | Run a Markdown skill. |
| `subagent(prompt, result=None)` | Implemented | Run an isolated child session using the same sandbox. |
| `shell(command, timeout=120)` | Implemented | Run shell through sandbox policy. |
| `read_file(path)` | Implemented | Read a sandbox file. |
| `write_file(path, content)` | Implemented | Write a sandbox file when enabled. |
