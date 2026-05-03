# Use the Sandbox

The virtual sandbox gives agents controlled access to a workspace.

## Read Files

```python
content = await session.read_file("README.md")
```

Read access is enabled by default.

## Write Files

```python
agent = await init(allow_write=True)
session = await agent.session()
await session.write_file("report.txt", "Repository summary")
```

Without `allow_write=True`, writes raise `PermissionError`.

## Run Shell Commands

```python
agent = await init(allow_shell=True)
session = await agent.session()
result = await session.shell("python --version")
```

Without `allow_shell=True`, shell commands raise `PermissionError`.

## Enable Both

```python
agent = await init(
    allow_write=True,
    allow_shell=True,
)
```

## Keep Commands Narrow

For production use, prefer command allowlists:

```python
from pyflue.sandbox import SandboxPolicy, VirtualSandbox

sandbox = VirtualSandbox(
    policy=SandboxPolicy(
        allow_shell=True,
        allowed_commands=("python", "pytest"),
    )
)
```

The high-level `init` helper does not expose command allowlists yet. Create a
custom `VirtualSandbox` through lower-level integration when you need that
control.
