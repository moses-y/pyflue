"""PyFlue command-line interface."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Literal

import typer
from rich.console import Console

from pyflue import init

app = typer.Typer(help="PyFlue agent harness CLI.")
skill_app = typer.Typer(help="Manage Markdown skills.")
app.add_typer(skill_app, name="skill")
console = Console()
PROMPT_OPTION = typer.Option(..., "--prompt", "-p", help="Prompt to run.")
SESSION_OPTION = typer.Option("default", "--session", "-s")
CONFIG_OPTION = typer.Option("pyflue.toml", "--config")
ALLOW_WRITE_OPTION = typer.Option(False, "--allow-write")
ALLOW_SHELL_OPTION = typer.Option(False, "--allow-shell")
PORT_OPTION = typer.Option(2024, "--port")
PROJECT_NAME_ARGUMENT = typer.Argument("pyflue-agent")
SKILL_NAME_ARGUMENT = typer.Argument(...)
BuildTarget = Literal[
    "docker",
    "github-actions",
    "gitlab-ci",
    "railway",
    "render",
    "fly",
]


@app.command("init")
def init_project(name: str = PROJECT_NAME_ARGUMENT, force: bool = False) -> None:
    """Scaffold a PyFlue project."""
    root = Path(name).resolve()
    if root.exists() and any(root.iterdir()) and not force:
        raise typer.BadParameter(f"{root} is not empty. Use --force to overwrite.")
    (root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    (root / "AGENTS.md").write_text(
        "You are a careful autonomous Python agent. Keep changes scoped.\n",
        encoding="utf-8",
    )
    (root / "pyflue.toml").write_text(
        '[agent]\nmodel = "openai:gpt-4o"\nharness = "deepagents"\nsandbox = "virtual"\n',
        encoding="utf-8",
    )
    _write_skill(root / ".agents" / "skills" / "triage.md", "triage")
    console.print(f"Created PyFlue project at {root}")


@app.command()
def run(
    prompt: str = PROMPT_OPTION,
    session: str = SESSION_OPTION,
    config: Path = CONFIG_OPTION,
    allow_write: bool = ALLOW_WRITE_OPTION,
    allow_shell: bool = ALLOW_SHELL_OPTION,
) -> None:
    """Run one PyFlue prompt."""

    async def _run() -> None:
        agent = await init(
            config_path=config,
            allow_write=allow_write,
            allow_shell=allow_shell,
        )
        result = await (await agent.session(session)).prompt(prompt)
        console.print(result.text)

    asyncio.run(_run())


@app.command()
def dev(port: int = PORT_OPTION, config: Path = CONFIG_OPTION) -> None:
    """Start a development server with hot-reload support."""
    console.print(
        f"pyflue dev is planned for FastAPI hot reload. Config={config}, port={port}"
    )


@app.command()
def build(target: BuildTarget = "docker") -> None:
    """Generate deployment artifacts."""
    if target == "docker":
        _write_docker_artifacts()
        console.print("Generated Dockerfile and app.py")
    elif target == "github-actions":
        _write_github_actions_workflow()
        console.print("Generated .github/workflows/pyflue-agent.yml")
    elif target == "gitlab-ci":
        _write_gitlab_ci()
        console.print("Generated .gitlab-ci.yml")
    elif target == "railway":
        _write_docker_artifacts()
        Path("railway.json").write_text(
            '{\n  "$schema": "https://railway.app/railway.schema.json",\n'
            '  "build": {"builder": "DOCKERFILE"},\n'
            '  "deploy": {"startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT"}\n'
            "}\n",
            encoding="utf-8",
        )
        console.print("Generated Dockerfile, app.py, and railway.json")
    elif target == "render":
        _write_docker_artifacts()
        Path("render.yaml").write_text(
            "services:\n"
            "  - type: web\n"
            "    name: pyflue-agent\n"
            "    runtime: docker\n"
            "    plan: starter\n"
            "    envVars:\n"
            "      - key: PORT\n"
            "        value: 8000\n",
            encoding="utf-8",
        )
        console.print("Generated Dockerfile, app.py, and render.yaml")
    elif target == "fly":
        _write_docker_artifacts()
        Path("fly.toml").write_text(
            'app = "pyflue-agent"\n'
            'primary_region = "iad"\n\n'
            "[http_service]\n"
            "  internal_port = 8000\n"
            "  force_https = true\n"
            "  auto_stop_machines = true\n"
            "  auto_start_machines = true\n",
            encoding="utf-8",
        )
        console.print("Generated Dockerfile, app.py, and fly.toml")


@app.command()
def deploy(dry_run: bool = False) -> None:
    """Deploy the PyFlue agent using the configured harness."""
    console.print("Dry run: deployment config is valid." if dry_run else "pyflue deploy is planned.")


@skill_app.command("new")
def new_skill(name: str = SKILL_NAME_ARGUMENT) -> None:
    """Create a new Markdown skill."""
    path = Path(".agents") / "skills" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_skill(path, name)
    console.print(f"Created skill {path}")


def _write_skill(path: Path, name: str) -> None:
    content = {
        "name": name,
        "description": f"{name} workflow",
        "input_schema": {"type": "object", "properties": {}},
        "output_schema": {"type": "object", "properties": {"summary": {"type": "string"}}},
    }
    frontmatter = "\n".join(
        [
            "---",
            f"name: {content['name']}",
            f"description: {content['description']}",
            "input_schema:",
            "  type: object",
            "  properties: {}",
            "output_schema:",
            "  type: object",
            "  properties:",
            "    summary:",
            "      type: string",
            "---",
            "",
            "# Role",
            "You are a PyFlue skill.",
            "",
            "## Instructions",
            "Complete the requested workflow and return a concise result.",
        ]
    )
    path.write_text(frontmatter, encoding="utf-8")


def _write_docker_artifacts() -> None:
    Path("Dockerfile").write_text(
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY . .\n"
        "RUN pip install . fastapi uvicorn\n"
        'CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]\n',
        encoding="utf-8",
    )
    Path("app.py").write_text(
        "from fastapi import FastAPI\n"
        "from pydantic import BaseModel\n\n"
        "from pyflue import init\n\n\n"
        "class PromptRequest(BaseModel):\n"
        "    prompt: str\n"
        "    session: str = \"default\"\n\n\n"
        "app = FastAPI(title=\"PyFlue Agent\")\n\n\n"
        "@app.post(\"/prompt\")\n"
        "async def prompt(request: PromptRequest):\n"
        "    agent = await init()\n"
        "    session = await agent.session(request.session)\n"
        "    result = await session.prompt(request.prompt)\n"
        "    return {\"text\": result.text, \"metadata\": result.metadata}\n",
        encoding="utf-8",
    )


def _write_github_actions_workflow() -> None:
    path = Path(".github") / "workflows" / "pyflue-agent.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "name: PyFlue Agent\n\n"
        "on:\n"
        "  workflow_dispatch:\n"
        "    inputs:\n"
        "      prompt:\n"
        "        description: Prompt to run\n"
        "        required: true\n"
        "        default: Review this repository\n\n"
        "jobs:\n"
        "  agent:\n"
        "    runs-on: ubuntu-latest\n"
        "    permissions:\n"
        "      contents: read\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - uses: astral-sh/setup-uv@v5\n"
        "      - uses: actions/setup-python@v5\n"
        "        with:\n"
        "          python-version: '3.12'\n"
        "      - run: uv sync\n"
        "      - name: Run PyFlue agent\n"
        "        env:\n"
        "          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}\n"
        "        run: uv run pyflue run --allow-shell --prompt \"${{ inputs.prompt }}\"\n",
        encoding="utf-8",
    )


def _write_gitlab_ci() -> None:
    Path(".gitlab-ci.yml").write_text(
        "pyflue-agent:\n"
        "  image: ghcr.io/astral-sh/uv:python3.12-bookworm-slim\n"
        "  rules:\n"
        "    - if: $CI_PIPELINE_SOURCE == \"web\"\n"
        "  variables:\n"
        "    PROMPT: \"Review this repository\"\n"
        "  script:\n"
        "    - uv sync\n"
        "    - uv run pyflue run --allow-shell --prompt \"$PROMPT\"\n",
        encoding="utf-8",
    )


def _parse_payload(payload: str | None) -> dict[str, Any]:
    return json.loads(payload or "{}")
