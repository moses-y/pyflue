from __future__ import annotations

import asyncio

from pydantic import BaseModel

from pyflue import init


class CodingResult(BaseModel):
    summary: str
    files_changed: list[str] = []
    tests_run: list[str] = []


async def run_coding_agent(repo: str, prompt: str) -> CodingResult:
    agent = await init(
        model="openai:gpt-5.5",
        sandbox="virtual",
        allow_write=True,
        allow_shell=True,
    )
    session = await agent.session("code")

    await session.shell("mkdir -p workspace")
    await session.shell(f"git clone {repo} workspace/project", timeout=600)

    return await session.prompt(
        "Work in workspace/project. "
        "Make the smallest safe change needed for this task, then summarize it.\n\n"
        f"Task: {prompt}",
        result=CodingResult,
    )


async def main() -> None:
    result = await run_coding_agent(
        repo="https://github.com/SuperagenticAI/pyflue",
        prompt="Review the project structure and suggest one improvement.",
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
