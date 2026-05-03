from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from pyflue.core import PyFlueAgent
from pyflue.harnesses.base import HarnessBackend
from pyflue.sandbox import SandboxPolicy
from pyflue.types import HarnessResult, PyFlueConfig


class _Result(BaseModel):
    summary: str


class _FakeBackend(HarnessBackend):
    name = "fake"

    def __init__(self, responses: list[str] | None = None):
        self.calls = []
        self.responses = responses or ['---RESULT_START---\n{"summary": "ok"}\n---RESULT_END---']

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        text = self.responses[min(len(self.calls) - 1, len(self.responses) - 1)]
        return HarnessResult(
            text=text,
            raw=SimpleNamespace(),
            metadata={"harness": "fake"},
        )


@pytest.mark.asyncio
async def test_session_prompt_persists_and_parses_result(tmp_path):
    (tmp_path / "AGENTS.md").write_text("System", encoding="utf-8")
    config = PyFlueConfig(root=tmp_path, harness="deepagents")
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend()

    session = await agent.session("s1")
    result = await session.prompt("hello", result=_Result)

    assert result.summary == "ok"
    assert agent.backend.calls[0]["system_prompt"] == "System"


@pytest.mark.asyncio
async def test_session_skill_uses_markdown_skill(tmp_path):
    skill_dir = tmp_path / ".agents" / "skills"
    skill_dir.mkdir(parents=True)
    (skill_dir / "triage.md").write_text(
        "---\nname: triage\n---\nDo triage.",
        encoding="utf-8",
    )
    config = PyFlueConfig(root=tmp_path, harness="deepagents")
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend()

    await (await agent.session("s1")).skill("triage", args={"issue": 1})

    assert "Do triage" in agent.backend.calls[0]["prompt"]
    assert '"issue": 1' in agent.backend.calls[0]["prompt"]


@pytest.mark.asyncio
async def test_session_prompt_applies_role_and_model_override(tmp_path):
    role_dir = tmp_path / ".agents" / "roles"
    role_dir.mkdir(parents=True)
    (role_dir / "coder.md").write_text(
        "---\nname: coder\n---\nYou review code carefully.",
        encoding="utf-8",
    )
    config = PyFlueConfig(root=tmp_path, harness="deepagents", model="base-model")
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend()

    await (await agent.session("s1")).prompt("hello", role="coder", model="override-model")

    assert "You review code carefully." in agent.backend.calls[0]["prompt"]
    assert agent.backend.calls[0]["config"].model == "override-model"


@pytest.mark.asyncio
async def test_session_prompt_retries_invalid_typed_output(tmp_path):
    config = PyFlueConfig(root=tmp_path, harness="deepagents", typed_retries=1)
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend(
        responses=[
            "not json",
            '---RESULT_START---\n{"summary": "fixed"}\n---RESULT_END---',
        ]
    )

    result = await (await agent.session("s1")).prompt("hello", result=_Result)

    assert result.summary == "fixed"
    assert len(agent.backend.calls) == 2


@pytest.mark.asyncio
async def test_session_task_uses_isolated_child_history(tmp_path):
    config = PyFlueConfig(root=tmp_path, harness="deepagents")
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend()

    parent = await agent.session("parent")
    await parent.task("child work", task_id="child")

    assert parent.db_path != (await agent.session("child")).db_path
    assert "child work" in agent.backend.calls[0]["prompt"]


@pytest.mark.asyncio
async def test_session_stream_emits_events(tmp_path):
    config = PyFlueConfig(root=tmp_path, harness="deepagents")
    agent = PyFlueAgent(config=config)
    agent.backend = _FakeBackend(responses=["streamed text"])

    events = [event async for event in (await agent.session("s1")).stream("hello")]

    assert [event.type for event in events] == ["start", "delta", "end"]
    assert events[1].data["text"] == "streamed text"


@pytest.mark.asyncio
async def test_session_secrets_are_grant_based_for_shell(tmp_path):
    config = PyFlueConfig(root=tmp_path, harness="deepagents", env={"TOKEN": "secret"})
    agent = PyFlueAgent(
        config=config,
        sandbox_policy=SandboxPolicy(
            allow_shell=True,
            allowed_commands=("python",),
        ),
    )
    session = await agent.session("s1")

    without_grant = await session.shell("python -c 'import os; print(os.getenv(\"TOKEN\"))'")
    with_grant = await session.shell(
        "python -c 'import os; print(os.getenv(\"TOKEN\"))'",
        secrets=["TOKEN"],
    )

    assert without_grant["stdout"].strip() == "None"
    assert with_grant["stdout"].strip() == "secret"


@pytest.mark.asyncio
async def test_virtual_sandbox_persists_for_same_session_id(tmp_path):
    config = PyFlueConfig(root=tmp_path, harness="deepagents")
    agent = PyFlueAgent(
        config=config,
        sandbox_policy=SandboxPolicy(allow_write=True),
    )

    await (await agent.session("stable")).write_file("note.txt", "persisted")
    content = await (await agent.session("stable")).read_file("note.txt")

    assert content == "persisted"
