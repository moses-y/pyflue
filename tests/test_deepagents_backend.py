from __future__ import annotations

import sys
from types import ModuleType

from pyflue.harnesses.deepagents import _DeepAgentsSandboxBackend, _permissions
from pyflue.sandbox import SandboxPolicy, VirtualSandbox


def test_deepagents_backend_upload_download_and_execute(monkeypatch, tmp_path):
    _install_fake_deepagents_protocol(monkeypatch)
    sandbox = VirtualSandbox(
        tmp_path,
        SandboxPolicy(allow_write=True, allow_shell=True),
    )
    backend = _DeepAgentsSandboxBackend(sandbox)

    upload = backend.upload_files([("/AGENTS.md", b"instructions")])
    download = backend.download_files(["/AGENTS.md"])
    execute = backend.execute("cat AGENTS.md")

    assert getattr(upload[0], "error", None) is None
    assert download[0].content == b"instructions"
    assert execute.output == "instructions"
    assert execute.exit_code == 0


def test_deepagents_permissions_mirror_sandbox_policy(monkeypatch, tmp_path):
    class _Permission:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_deepagents = ModuleType("deepagents")
    fake_deepagents.FilesystemPermission = _Permission
    monkeypatch.setitem(sys.modules, "deepagents", fake_deepagents)

    readonly = _permissions(VirtualSandbox(tmp_path))
    writable = _permissions(
        VirtualSandbox(tmp_path, SandboxPolicy(allow_write=True)),
    )

    assert readonly[0].kwargs == {
        "operations": ["write"],
        "paths": ["/**"],
        "mode": "deny",
    }
    assert writable[0].kwargs == {
        "operations": ["read", "write"],
        "paths": ["/**"],
    }


def _install_fake_deepagents_protocol(monkeypatch):
    protocol = ModuleType("deepagents.backends.protocol")

    class _Result:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    protocol.EditResult = _Result
    protocol.ExecuteResponse = _Result
    protocol.FileDownloadResponse = _Result
    protocol.FileUploadResponse = _Result
    protocol.GlobResult = _Result
    protocol.GrepResult = _Result
    protocol.LsResult = _Result
    protocol.ReadResult = _Result
    protocol.WriteResult = _Result

    backends = ModuleType("deepagents.backends")
    backends.protocol = protocol
    monkeypatch.setitem(sys.modules, "deepagents.backends", backends)
    monkeypatch.setitem(sys.modules, "deepagents.backends.protocol", protocol)
