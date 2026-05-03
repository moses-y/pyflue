from __future__ import annotations

import asyncio

from pydantic import BaseModel

from pyflue import init


class SupportAnswer(BaseModel):
    answer: str
    cited_articles: list[str]
    confidence: str


async def answer_support_question(
    question: str,
    articles: dict[str, str],
) -> SupportAnswer:
    agent = await init(model="openai:gpt-5.5all", allow_write=True, allow_shell=True)
    session = await agent.session("support")

    for name, content in articles.items():
        await session.write_file(f"knowledge/{name}.md", content)

    first_term = question.split()[0] if question.split() else "support"
    matches = await session.shell(f"grep -Rni {first_term!r} knowledge || true")
    return await session.prompt(
        "Answer this customer question using the articles in knowledge/*.md. "
        "Cite article filenames when possible.\n\n"
        f"Question: {question}\n\nSearch matches:\n{matches['stdout']}",
        result=SupportAnswer,
    )


async def main() -> None:
    result = await answer_support_question(
        "How do I reset my API key?",
        {
            "api-keys": "Users can reset API keys from Settings > API keys.",
            "billing": "Billing questions are handled from Settings > Billing.",
        },
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
