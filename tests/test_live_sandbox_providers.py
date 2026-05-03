from __future__ import annotations

import os

import pytest

from pyflue.sandboxes.base import SandboxPolicy
from pyflue.sandboxes.registry import create_sandbox

pytestmark = pytest.mark.live


@pytest.mark.parametrize(
    ("provider", "env_name"),
    [
        ("daytona", "DAYTONA_API_KEY"),
        ("e2b", "E2B_API_KEY"),
        ("modal", "MODAL_TOKEN_ID"),
        ("runloop", "RUNLOOP_API_KEY"),
    ],
)
def test_live_sandbox_provider_smoke(provider: str, env_name: str):
    if os.getenv("PYFLUE_LIVE_SANDBOX_TESTS") != "1":
        pytest.skip("Set PYFLUE_LIVE_SANDBOX_TESTS=1 to run live sandbox smoke tests.")
    if not os.getenv(env_name):
        pytest.skip(f"Missing provider credential: {env_name}")

    sandbox = create_sandbox(
        provider,
        policy=SandboxPolicy(allow_write=True, allow_shell=True, allowed_commands=("python",)),
        env=dict(os.environ),
    )

    sandbox.write_file("pyflue-smoke.txt", "ok")
    assert sandbox.read_file("pyflue-smoke.txt") == "ok"
    result = sandbox.shell("python -c 'print(42)'")
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "42"
