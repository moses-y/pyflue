from __future__ import annotations

import asyncio
from pathlib import Path

from pydantic import BaseModel

from pyflue import init


class TriageResult(BaseModel):
    severity: str
    summary: str
    suggested_labels: list[str] = []
    fix_recommended: bool = False


async def ensure_triage_skill() -> Path:
    skills_dir = Path(".agents/skills")
    skills_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skills_dir / "triage_issue.md"
    if not skill_path.exists():
        skill_path.write_text(
            "---\n"
            "name: triage_issue\n"
            "description: Triage a software issue.\n"
            "---\n\n"
            "Assess the issue severity, summarize the likely problem, suggest labels, "
            "and decide whether a fix should be attempted now.\n",
            encoding="utf-8",
        )
    return skills_dir


async def triage_issue(issue_number: int, title: str, body: str) -> TriageResult:
    skills_dir = await ensure_triage_skill()
    agent = await init(model="openai:gpt-5.5", skills_dir=skills_dir)
    session = await agent.session(f"issue-{issue_number}")
    return await session.skill(
        "triage_issue",
        args={"issue_number": issue_number, "title": title, "body": body},
        result=TriageResult,
    )


async def main() -> None:
    result = await triage_issue(
        issue_number=123,
        title="CLI build target fails on GitLab",
        body="Running pyflue build --target gitlab-ci creates a pipeline that cannot find uv.",
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
