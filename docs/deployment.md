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
| Cloudflare | Partial | `pyflue build --target cloudflare` | Generates `wrangler.toml`. Full Python container guidance is still needed. |
| Vercel | Implemented | `pyflue build --target vercel` | Generates Python app artifacts and `vercel.json`. |
| Netlify | Implemented | `pyflue build --target netlify` | Generates Python app artifacts and `netlify.toml`. |

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

The generated `app.py` exposes the PyFlue server:

```bash
curl http://localhost:8000/prompt/default \
  -H "Content-Type: application/json" \
  -d '{"payload": {"prompt": "Review this project"}}'
```

File-based agents are exposed under `/agents/{name}/{agent_id}`.

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

```bash
pyflue deploy --target railway
```

When the Railway CLI is installed and authenticated, PyFlue runs
`railway up`.

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

```bash
pyflue deploy --target fly
```

When the Fly.io CLI is installed and authenticated, PyFlue runs `fly deploy`.

## Cloudflare

Generate the Cloudflare starter file:

```bash
pyflue build --target cloudflare
```

Cloudflare support is currently partial. The generated file is a starting point
for Cloudflare Python or container deployments. For production today, prefer the
Docker/FastAPI target on a container-capable platform.

## Vercel

Generate Vercel files:

```bash
pyflue build --target vercel
```

This writes:

```text
Dockerfile
app.py
vercel.json
```

Review the generated route config before deploying.

```bash
pyflue deploy --target vercel
```

When the Vercel CLI is installed and authenticated, PyFlue runs
`vercel deploy`.

## Netlify

Generate Netlify files:

```bash
pyflue build --target netlify
```

This writes:

```text
Dockerfile
app.py
netlify.toml
```

Review the generated function settings before deploying.

```bash
pyflue deploy --target netlify
```

When the Netlify CLI is installed and authenticated, PyFlue runs
`netlify deploy`.
