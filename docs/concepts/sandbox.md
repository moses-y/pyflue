# Sandbox

PyFlue ships with a zero-config virtual sandbox for local development.

The sandbox provides a safe workspace boundary and policy-controlled tools.

## Default Policy

By default:

- file reads are allowed
- file writes are disabled
- shell execution is disabled

Enable writes and shell explicitly:

```python
agent = await init(
    allow_write=True,
    allow_shell=True,
)
```

Or from the CLI:

```bash
pyflue run \
  --prompt "Inspect and write report.txt" \
  --allow-write \
  --allow-shell
```

## Sandbox Tools

| Tool | Status | Description |
| --- | --- | --- |
| `read_file` | Implemented | Read a file or list a directory. |
| `write_file` | Implemented | Write text to a file when writes are enabled. |
| `edit_file` | Implemented | Replace exact text in a file. |
| `grep` | Implemented | Search files with a regex. |
| `glob` | Implemented | Find files by glob pattern. |
| `shell` | Implemented | Run a shell command when shell is enabled. |

## Path Boundary

All paths are resolved under the sandbox root. Attempts to escape the root are
rejected.

```python
await session.read_file("../secrets.txt")
```

This raises an error because the path escapes the sandbox.

## Command Allowlist

`SandboxPolicy` supports command allowlists:

```python
from pyflue.sandbox import SandboxPolicy, VirtualSandbox

sandbox = VirtualSandbox(
    policy=SandboxPolicy(
        allow_shell=True,
        allowed_commands=("python", "git"),
    )
)
```

## DeepAgents Adapter

When using the DeepAgents backend, PyFlue adapts `VirtualSandbox` to the
DeepAgents backend protocol. The adapter supports:

- list
- read
- write
- edit
- grep
- glob
- execute
- upload files
- download files

This lets DeepAgents skills and memory load files from the PyFlue sandbox.
