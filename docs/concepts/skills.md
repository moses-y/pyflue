# Skills

Skills are Markdown-defined workflows stored under `.agents/skills`.

Each skill has YAML frontmatter and a Markdown instruction body.

```markdown
---
name: triage
description: Triage an issue and decide whether it can be fixed safely.
input_schema:
  type: object
  properties:
    issue_number:
      type: integer
  required: [issue_number]
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

You are a senior Python engineer.

## Instructions

Inspect the issue and return a concise result.
```

## Loading

PyFlue scans:

```text
.agents/skills/**/*.md
```

If the directory does not exist, PyFlue loads zero skills. That is valid.

## Calling a Skill

```python
result = await session.skill(
    "triage",
    args={"issue_number": 123},
    result=FixResult,
)
```

When a skill is called, PyFlue builds a prompt from:

- the Markdown instruction body
- the `args` dictionary
- the optional output schema from the skill

## Name Resolution

The skill name comes from frontmatter:

```yaml
name: triage
```

If `name` is missing, PyFlue uses the Markdown filename stem. If the final name
is empty, PyFlue raises `ValueError`.

## Create a New Skill

```bash
pyflue skill new review
```

This creates:

```text
.agents/skills/review.md
```
