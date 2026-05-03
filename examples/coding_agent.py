"""Minimal PyFlue coding-agent example."""

from __future__ import annotations

import asyncio

from pydantic import BaseModel

from pyflue import init


class TriageResult(BaseModel):
    fix_applied: bool
    summary: str


async def main() -> None:
    agent = await init(
        model="openai:gpt-5.5all",
        harness="deepagents",
        sandbox="virtual",
        allow_write=True,
        allow_shell=True,
    )
    session = await agent.session("demo")
    result = await session.skill(
        "triage",
        args={"issue_number": 123},
        result=TriageResult,
    )
    if result.fix_applied:
        await session.shell("git status --short")
    print(result.summary)


if __name__ == "__main__":
    asyncio.run(main())
