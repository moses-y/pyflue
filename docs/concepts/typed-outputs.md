# Typed Outputs

PyFlue validates structured results with Pydantic v2.

```python
from pydantic import BaseModel


class TriageResult(BaseModel):
    fix_applied: bool
    summary: str
```

Pass the model to `prompt` or `skill`:

```python
result = await session.skill(
    "triage",
    args={"issue_number": 123},
    result=TriageResult,
)
```

## Result Delimiters

When a result model is provided, PyFlue asks the backend to return JSON between
these delimiters:

```text
---RESULT_START---
{"fix_applied": true, "summary": "Fixed one typo."}
---RESULT_END---
```

PyFlue extracts the JSON and validates it with `pydantic.TypeAdapter`.

## Validation Errors

If the model returns invalid data, PyFlue asks the backend to repair the
response. The default retry count is `3` and can be configured with
`typed_retries` in `pyflue.toml`.

```toml
[agent]
typed_retries = 3
```

You can override retries for one call:

```python
result = await session.prompt(
    "Return a valid triage result",
    result=TriageResult,
    retries=1,
)
```
