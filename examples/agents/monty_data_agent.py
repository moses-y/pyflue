from __future__ import annotations

import asyncio

from pydantic import BaseModel

from pyflue import init


class Metrics(BaseModel):
    total: int
    count: int
    average: float


async def main() -> None:
    agent = await init(python_backend="monty")
    session = await agent.session("monty-data-agent")

    metrics = await session.run_python(
        """
total = sum(items)
count = len(items)
{"total": total, "count": count, "average": total / count}
""",
        inputs={"items": [10, 20, 30]},
        result=Metrics,
    )
    print(metrics.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
