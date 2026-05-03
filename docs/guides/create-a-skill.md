# Create a Skill

Create a skill from the CLI:

```bash
pyflue skill new summarize
```

This creates:

```text
.agents/skills/summarize.md
```

## Skill Structure

```markdown
---
name: summarize
description: Summarize input into a concise report.
input_schema:
  type: object
  properties:
    topic:
      type: string
  required: [topic]
output_schema:
  type: object
  properties:
    summary:
      type: string
  required: [summary]
---

# Role

You are a concise technical writer.

## Instructions

Write a short, accurate summary.
```

## Call the Skill

```python
result = await session.skill(
    "summarize",
    args={"topic": "PyFlue sessions"},
)
```

## Add a Typed Result

```python
from pydantic import BaseModel


class SummaryResult(BaseModel):
    summary: str


result = await session.skill(
    "summarize",
    args={"topic": "PyFlue sessions"},
    result=SummaryResult,
)
```
