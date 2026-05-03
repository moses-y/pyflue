from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from pyflue.core import PyFlueAgent
from pyflue.harnesses.base import HarnessBackend
from pyflue.types import HarnessResult, PyFlueConfig


class _Result(BaseModel):
    summary: str


class _FakeBackend(HarnessBackend):
    name = "fake"

    def __init__(self):
        self.calls = []

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        return HarnessResult(
            text='---RESULT_START---\n{"summary": "ok"}\n---RESULT_END---',
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
