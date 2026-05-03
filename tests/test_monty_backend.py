from __future__ import annotations

import pytest
from pydantic import BaseModel

from pyflue import init

pydantic_monty = pytest.importorskip("pydantic_monty")


class Metrics(BaseModel):
    total: int
    count: int


async def test_session_run_python_with_monty():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-basic")

    result = await session.run_python("x + 1", inputs={"x": 41})

    assert result.result == 42
    assert result.backend == "monty"


async def test_session_run_python_typed_result():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-typed")

    result = await session.run_python(
        '{"total": sum(items), "count": len(items)}',
        inputs={"items": [1, 2, 3]},
        result=Metrics,
    )

    assert result == Metrics(total=6, count=3)


@pytest.mark.skip(reason="Monty stateless API does not preserve state between runs")
async def test_monty_repl_state_is_preserved():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-state")

    await session.run_python("x = 10")
    result = await session.run_python("x + 5")

    assert result.result == 15


@pytest.mark.skip(reason="External functions not supported in new Monty API")
async def test_monty_external_function():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-external")

    async def double(value: int) -> int:
        return value * 2

    result = await session.run_python(
        "double(value=21)",
        inputs={"value": 21},
        external_functions={"double": double},
    )

    assert result.result == 42


async def test_monty_reads_virtual_sandbox_file(tmp_path):
    agent = await init(
        python_backend="monty",
        config_path=tmp_path / "missing.toml",
        allow_write=True,
    )
    session = await agent.session("monty-files")
    await session.write_file("data.txt", "hello monty")

    result = await session.run_python(
        "from pathlib import Path\nPath('/data.txt').read_text()",
    )

    assert result.result == "hello monty"


@pytest.mark.skip(reason="Monty stateless API does not support state dump/load")
async def test_monty_state_dump_and_load():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-dump")
    await session.run_python("value = 37")
    state = session.dump_python_state()

    assert isinstance(state, bytes)

    await session.run_python("value = 0")
    session.load_python_state(state)
    result = await session.run_python("value")

    assert result.result == 37


async def test_monty_resource_limits():
    agent = await init(python_backend="monty")
    session = await agent.session("monty-limits")

    result = await session.run_python(
        "sum(items)",
        inputs={"items": [1, 2, 3]},
        resource_limits={"max_memory": 20_000_000},
    )

    assert result.result == 6
