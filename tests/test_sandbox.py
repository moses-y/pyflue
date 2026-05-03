from __future__ import annotations

import pytest

from pyflue.sandbox import SandboxPolicy, VirtualSandbox


def test_virtual_sandbox_path_boundary(tmp_path):
    sandbox = VirtualSandbox(tmp_path)

    with pytest.raises(ValueError):
        sandbox.resolve("../outside.txt", must_exist=False)


def test_virtual_sandbox_write_and_shell_policy(tmp_path):
    sandbox = VirtualSandbox(tmp_path)

    with pytest.raises(PermissionError):
        sandbox.write_file("x.txt", "x")
    with pytest.raises(PermissionError):
        sandbox.shell("echo hi")

    enabled = VirtualSandbox(
        tmp_path,
        SandboxPolicy(allow_write=True, allow_shell=True),
    )
    enabled.write_file("x.txt", "hello")
    assert enabled.read_file("x.txt") == "hello"
    assert enabled.shell("cat x.txt")["stdout"] == "hello"


def test_virtual_sandbox_grep_glob_and_edit(tmp_path):
    sandbox = VirtualSandbox(tmp_path, SandboxPolicy(allow_write=True))
    sandbox.write_file("src/app.py", "print('needle')\n")

    assert "src/app.py" in sandbox.glob("**/*.py")
    assert "needle" in sandbox.grep("needle", include="*.py")
    assert "Edited" in sandbox.edit_file("src/app.py", "needle", "value")
    assert "value" in sandbox.read_file("src/app.py")
