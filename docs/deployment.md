# Deployment

PyFlue is a Python package, so deployment is centered on Python runtimes,
containers, and CI jobs.

The closest PyFlue equivalent to a JavaScript server target is the Docker and
FastAPI target. It produces a small `app.py` and `Dockerfile` that can run on
any platform that accepts a Python container.

## Supported Targets

| Target | Status | Command | Notes |
| --- | --- | --- | --- |
| Docker/FastAPI | Implemented | `pyflue build --target docker` | General Python web target. Use this for local servers, VPS, Kubernetes, and container platforms. |
| GitHub Actions | Implemented | `pyflue build --target github-actions` | Generates `.github/workflows/pyflue-agent.yml`. |
| GitLab CI/CD | Implemented | `pyflue build --target gitlab-ci` | Generates `.gitlab-ci.yml`. |
| Railway | Implemented | `pyflue build --target railway` | Generates Docker/FastAPI artifacts and `railway.json`. |
| Render | Implemented | `pyflue build --target render` | Generates Docker/FastAPI artifacts and `render.yaml`. |
| Fly.io | Implemented | `pyflue build --target fly` | Generates Docker/FastAPI artifacts and `fly.toml`. |
| Cloudflare Workers | Planned | Not available yet | Python Worker support is not equivalent to a full Python agent runtime today. A Cloudflare Containers guide is planned. |
| Vercel | Planned | Not available yet | A Python serverless guide is planned. |
| Netlify | Planned | Not available yet | A Python function guide is planned. |

## Docker/FastAPI

Generate the default Python web artifacts:

```bash
pyflue build --target docker
```

This writes:

```text
Dockerfile
app.py
```

The generated `app.py` exposes a minimal `/prompt` endpoint:

```bash
curl http://localhost:8000/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Review this project", "session": "default"}'
```

The generated Dockerfile installs the package and runs Uvicorn.

## GitHub Actions

Generate a workflow:

```bash
pyflue build --target github-actions
```

This writes:

```text
.github/workflows/pyflue-agent.yml
```

The workflow is manual by default. Add provider keys as repository secrets,
then run it from the GitHub Actions tab.

## GitLab CI/CD

Generate a pipeline file:

```bash
pyflue build --target gitlab-ci
```

This writes:

```text
.gitlab-ci.yml
```

The generated job is designed for manual web pipelines. Add provider keys as
masked CI/CD variables.

## Railway

Generate Railway files:

```bash
pyflue build --target railway
```

This writes:

```text
Dockerfile
app.py
railway.json
```

Deploy the project with Railway's GitHub integration or CLI.

## Render

Generate Render files:

```bash
pyflue build --target render
```

This writes:

```text
Dockerfile
app.py
render.yaml
```

Create a new Blueprint in Render and point it at the repository.

## Fly.io

Generate Fly.io files:

```bash
pyflue build --target fly
```

This writes:

```text
Dockerfile
app.py
fly.toml
```

Review the generated app name and region before deploying with `fly deploy`.

## Cloudflare, Vercel, and Netlify

These targets are planned, not implemented.

For now, use the Docker/FastAPI target on a platform that supports Python
containers. That path covers most production deployments while keeping the
agent runtime fully Python-native.
