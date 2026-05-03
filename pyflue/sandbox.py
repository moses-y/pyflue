"""Virtual sandbox for PyFlue sessions."""

from __future__ import annotations

import glob as globlib
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SandboxPolicy:
    """Controls model-callable filesystem and shell capabilities."""

    allow_write: bool = False
    allow_shell: bool = False
    allowed_commands: tuple[str, ...] = ()


class VirtualSandbox:
    """Zero-config local workspace sandbox with path boundary checks."""

    def __init__(self, root: str | Path | None = None, policy: SandboxPolicy | None = None):
        self._owned_tmp: tempfile.TemporaryDirectory[str] | None = None
        if root is None:
            self._owned_tmp = tempfile.TemporaryDirectory(prefix="pyflue-")
            root = self._owned_tmp.name
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.policy = policy or SandboxPolicy()

    def read_file(self, path: str, *, offset: int = 1, limit: int | None = None) -> str:
        target = self.resolve(path)
        if target.is_dir():
            return "\n".join(sorted(child.name + ("/" if child.is_dir() else "") for child in target.iterdir()))
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(offset - 1, 0)
        selected = lines[start : start + limit if limit else None]
        return "\n".join(selected)

    def write_file(self, path: str, content: str) -> str:
        self._require_write()
        target = self.resolve(path, must_exist=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {self.relative(target)}"

    def edit_file(self, path: str, old: str, new: str, *, replace_all: bool = False) -> str:
        self._require_write()
        target = self.resolve(path)
        content = target.read_text(encoding="utf-8", errors="replace")
        count = content.count(old)
        if count == 0:
            raise ValueError(f"Text not found in {path}")
        updated = content.replace(old, new) if replace_all else content.replace(old, new, 1)
        target.write_text(updated, encoding="utf-8")
        return f"Edited {self.relative(target)} ({count if replace_all else 1} replacement)"

    def grep(self, pattern: str, *, path: str = ".", include: str | None = None) -> str:
        root = self.resolve(path)
        files = root.rglob(include or "*") if root.is_dir() else [root]
        regex = re.compile(pattern)
        matches: list[str] = []
        for file_path in files:
            if not file_path.is_file():
                continue
            for index, line in enumerate(file_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                if regex.search(line):
                    matches.append(f"{self.relative(file_path)}:{index}:{line}")
        return "\n".join(matches)

    def glob(self, pattern: str) -> str:
        search = str(self.resolve(pattern, must_exist=False))
        paths = sorted(globlib.glob(search, recursive=True))
        return "\n".join(self.relative(Path(path)) for path in paths)

    def shell(self, command: str, *, timeout: int | None = 120) -> dict[str, Any]:
        if not self.policy.allow_shell:
            raise PermissionError("Shell execution is disabled for this sandbox.")
        if self.policy.allowed_commands:
            executable = command.strip().split()[0] if command.strip() else ""
            if executable not in self.policy.allowed_commands:
                raise PermissionError(f"Command is not allowed: {executable}")
        completed = subprocess.run(
            command,
            cwd=self.root,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "exit_code": completed.returncode,
        }

    def resolve(self, path: str, *, must_exist: bool = True) -> Path:
        raw = str(path or ".")
        target = Path(raw).expanduser()
        if not target.is_absolute():
            target = self.root / target
        target = target.resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Path escapes sandbox root: {path}") from exc
        if must_exist and not target.exists():
            raise FileNotFoundError(path)
        return target

    def relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def _require_write(self) -> None:
        if not self.policy.allow_write:
            raise PermissionError("Write access is disabled for this sandbox.")
