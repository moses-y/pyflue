# Contributing

Thanks for contributing to PyFlue. This project is early, so changes should be
small, tested, and clearly documented.

## Development Setup

```bash
uv sync --extra dev --extra docs
```

## Checks

Run these before opening a pull request:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
uv run --extra docs mkdocs build --strict
uv build
```

## Pull Request Guidelines

- Keep changes focused.
- Add or update tests for behavior changes.
- Update docs when public behavior changes.
- Do not expose low-level runtime internals in user-facing docs.
- Keep public docs professional and concise.

## Dependency Changes

When changing dependencies:

```bash
uv lock
```

Commit the updated `uv.lock`.
