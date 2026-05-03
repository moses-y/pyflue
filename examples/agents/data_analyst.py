from __future__ import annotations

import asyncio

from pydantic import BaseModel

from pyflue import init


class AnalysisResult(BaseModel):
    summary: str
    metrics: dict[str, float]
    recommendations: list[str]


async def analyze_csv(csv_text: str, question: str) -> AnalysisResult:
    agent = await init(model="openai:gpt-5.5", allow_write=True, allow_shell=True)
    session = await agent.session("data-analysis")
    await session.write_file("data/input.csv", csv_text)
    preview = await session.shell(
        "python - <<'PY'\n"
        "import pandas as pd\n"
        "df = pd.read_csv('data/input.csv')\n"
        "print(df.describe(numeric_only=True).to_string())\n"
        "PY"
    )
    return await session.prompt(
        f"Analyze data/input.csv for this question: {question}\n\n"
        f"Data preview:\n{preview['stdout']}",
        result=AnalysisResult,
    )


async def main() -> None:
    csv_text = "month,revenue,cost\njan,100,50\nfeb,140,65\nmar,180,90\n"
    result = await analyze_csv(csv_text, "What changed across the quarter?")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
