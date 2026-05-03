# CLI

PyFlue exposes the `pyflue` command.

## `pyflue init`

Create a new project:

```bash
pyflue init my-agent
```

Overwrite an existing directory:

```bash
pyflue init my-agent --force
```

Generated files:

```text
AGENTS.md
pyflue.toml
.agents/skills/triage.md
```

## `pyflue run`

Run one prompt:

```bash
pyflue run --prompt "Review this project"
```

Use a named session:

```bash
pyflue run --session issue-123 --prompt "Inspect the failure"
```

Enable sandbox writes and shell:

```bash
pyflue run \
  --prompt "Write a short report" \
  --allow-write \
  --allow-shell
```

## `pyflue skill new`

Create a new Markdown skill:

```bash
pyflue skill new review
```

## `pyflue build`

```bash
pyflue build
```

The default target is Docker/FastAPI.

```bash
pyflue build --target docker
```

Available targets:

| Target | Status | Generated files |
| --- | --- | --- |
| `docker` | Implemented | `Dockerfile`, `app.py` |
| `github-actions` | Implemented | `.github/workflows/pyflue-agent.yml` |
| `gitlab-ci` | Implemented | `.gitlab-ci.yml` |
| `railway` | Implemented | `Dockerfile`, `app.py`, `railway.json` |
| `render` | Implemented | `Dockerfile`, `app.py`, `render.yaml` |
| `fly` | Implemented | `Dockerfile`, `app.py`, `fly.toml` |

## `pyflue dev`

Current status: placeholder.

```bash
pyflue dev --port 2024
```

A hot-reload development server is planned.

## `pyflue deploy`

Current status: placeholder.

```bash
pyflue deploy --dry-run
```

Provider deployment is planned.
