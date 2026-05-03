# Build a Coding Agent

This guide builds a small coding-agent workflow with a Markdown skill and a
typed result.

## Create the Project

```bash
pyflue init code-agent
cd code-agent
```

## Edit the Skill

Open `.agents/skills/triage.md` and use:

```markdown
---
name: triage
description: Inspect a request and decide whether a safe fix was applied.
output_schema:
  type: object
  properties:
    fix_applied:
      type: boolean
    summary:
      type: string
  required: [fix_applied, summary]
---

# Role

You are a careful Python coding agent.

## Instructions

Inspect the request, make only safe changes, and summarize the result.
```

## Write the Agent Script

```python
import asyncio

from pydantic import BaseModel
from pyflue import init


class TriageResult(BaseModel):
    fix_applied: bool
    summary: str


async def main():
    agent = await init(
        model="openai:gpt-4o",
        harness="deepagents",
        allow_write=True,
        allow_shell=True,
    )

    session = await agent.session("coding-agent")
    result = await session.skill(
        "triage",
        args={"request": "Review the repository and suggest a safe fix."},
        result=TriageResult,
    )

    if result.fix_applied:
        await session.shell("git status --short")

    print(result.summary)


asyncio.run(main())
```

## Notes

- Shell execution requires `allow_shell=True`.
- File writes require `allow_write=True`.
- The current implementation does not commit changes automatically.
- Add your own approval and commit logic for production workflows.
