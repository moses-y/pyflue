# Feature Matrix

This page shows what users can rely on today and what is planned next.

| Feature | Status | Notes |
| --- | --- | --- |
| Python package | Implemented | `pyflue` package with console script. |
| DeepAgents backend | Implemented | Default backend. |
| OpenAI Agents backend | Planned | Dependency pinned, runtime not implemented. |
| Google ADK backend | Planned | Dependency pinned, runtime not implemented. |
| Pydantic AI backend | Planned | Dependency pinned, runtime not implemented. |
| Markdown skills | Implemented | `.agents/skills/**/*.md`. |
| Project instructions | Implemented | `AGENTS.md` and `CLAUDE.md`. |
| Sessions | Implemented | SQLite-backed history. |
| Subagent helper | Implemented | Child PyFlue session with shared sandbox. |
| Virtual sandbox | Implemented | Local path-bounded sandbox. |
| Shell policy | Implemented | Requires `allow_shell=True`. |
| Write policy | Implemented | Requires `allow_write=True`. |
| DeepAgents file transfer | Implemented | Upload and download methods. |
| Typed outputs | Implemented | Pydantic `TypeAdapter`. |
| CLI init | Implemented | Scaffolds project files. |
| CLI run | Implemented | Runs a prompt. |
| CLI skill new | Implemented | Scaffolds a skill. |
| CLI build | Implemented | Generates Docker/FastAPI and selected CI/platform artifacts. |
| CLI dev | Planned | Placeholder command. |
| CLI deploy | Planned | Placeholder command. |
| Remote sandboxes | Planned | Config direction only. |
| Automatic typed-output retries | Planned | Validation exists, retry does not. |

## Deployment Targets

| Target | Status | Notes |
| --- | --- | --- |
| Docker/FastAPI | Implemented | Python replacement for a JavaScript server target. |
| GitHub Actions | Implemented | Generates a manual workflow. |
| GitLab CI/CD | Implemented | Generates a manual pipeline job. |
| Railway | Implemented | Uses the Docker/FastAPI app. |
| Render | Implemented | Uses the Docker/FastAPI app. |
| Fly.io | Implemented | Uses the Docker/FastAPI app. |
| Cloudflare Workers | Planned | Python runtime support needs a separate design. |
| Vercel | Planned | Python serverless guide planned. |
| Netlify | Planned | Python function guide planned. |
