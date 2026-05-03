from __future__ import annotations

from typer.testing import CliRunner

from pyflue.cli import app


def test_cli_init_and_skill_new(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["init", "demo"])
    assert result.exit_code == 0
    assert (tmp_path / "demo" / "pyflue.toml").exists()
    assert (tmp_path / "demo" / ".agents" / "skills" / "triage.md").exists()

    monkeypatch.chdir(tmp_path / "demo")
    result = runner.invoke(app, ["skill", "new", "review"])
    assert result.exit_code == 0
    assert (tmp_path / "demo" / ".agents" / "skills" / "review.md").exists()


def test_cli_build_targets(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert (tmp_path / "app.py").exists()

    result = runner.invoke(app, ["build", "--target", "github-actions"])
    assert result.exit_code == 0
    assert (tmp_path / ".github" / "workflows" / "pyflue-agent.yml").exists()

    result = runner.invoke(app, ["build", "--target", "gitlab-ci"])
    assert result.exit_code == 0
    assert (tmp_path / ".gitlab-ci.yml").exists()

    result = runner.invoke(app, ["build", "--target", "railway"])
    assert result.exit_code == 0
    assert (tmp_path / "railway.json").exists()

    result = runner.invoke(app, ["build", "--target", "render"])
    assert result.exit_code == 0
    assert (tmp_path / "render.yaml").exists()

    result = runner.invoke(app, ["build", "--target", "fly"])
    assert result.exit_code == 0
    assert (tmp_path / "fly.toml").exists()
