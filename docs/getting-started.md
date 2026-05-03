# Getting Started

This guide creates a new PyFlue project, runs a prompt, and explains the files
that are generated.

## Requirements

- Python 3.11 or newer
- `uv` or `pip`
- A model provider key if you run a real model

PyFlue depends on DeepAgents `0.5.6`, which requires Python 3.11 or newer.

## Install

Add PyFlue to a project with `uv`:

```bash
uv add pyflue
```

Or install it with `pip`:

```bash
pip install pyflue
```

## Create a Project

```bash
pyflue init my-agent
cd my-agent
```

The command creates:

```text
AGENTS.md
pyflue.toml
.agents/
  skills/
    triage.md
```

## Run a Prompt

```bash
pyflue run --prompt "Review this project"
```

By default, PyFlue uses:

- `harness = "deepagents"`
- `sandbox = "virtual"`
- session id `default`
- read-only sandbox policy

Enable writes and shell execution explicitly:

```bash
pyflue run \
  --prompt "Inspect the project and write a short report to report.txt" \
  --allow-write \
  --allow-shell
```

## Use a Named Session

```bash
pyflue run --session issue-123 --prompt "Inspect the failure"
pyflue run --session issue-123 --prompt "Suggest the smallest fix"
```

Session history is stored under `.pyflue/sessions`.

## Project Configuration

`pyflue.toml` controls the default agent settings:

```toml
[agent]
model = "openai:gpt-4o"
harness = "deepagents"
sandbox = "virtual"
skills_dir = ".agents/skills"
state_dir = ".pyflue/sessions"
```

## Current CLI Coverage

| Command | Status |
| --- | --- |
| `pyflue init` | Implemented |
| `pyflue run` | Implemented |
| `pyflue skill new` | Implemented |
| `pyflue build` | Implemented for selected targets |
| `pyflue dev` | Placeholder |
| `pyflue deploy` | Placeholder |
