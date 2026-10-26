#!/usr/bin/env python3
"""Check repository hygiene without importing GPU dependencies."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "tmp", "data", "checkpoints", "outputs", "__pycache__"}
REQUIRED = [
    "README.md",
    "README_zh.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CITATION.cff",
    "deepaction/train_dupo.sh",
    "docs/REPRODUCIBILITY.md",
    "verl/LICENSE",
    "verl/verl/utils/reward_score/rlla.py",
]
FORBIDDEN = {
    "local user directory": re.compile(r"(?:/Users|/home)/[A-Za-z0-9._-]+/"),
    "embedded W&B credential": re.compile(r"WANDB_API_KEY\s*=\s*[A-Za-z0-9_-]{24,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "OpenAI-style secret": re.compile(r"sk-[A-Za-z0-9_-]{24,}"),
    "embedded bearer token": re.compile(
        r"Authorization\s*[:=]\s*[\"']?Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE
    ),
    "private key material": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path == Path(__file__).resolve():
            continue
        if path.stat().st_size > 15 * 1024 * 1024:
            yield path, None
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def main() -> None:
    errors: list[str] = []

    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path, content in iter_text_files():
        relative = path.relative_to(ROOT)
        if content is None:
            errors.append(f"oversized tracked candidate (>15 MiB): {relative}")
            continue
        for label, pattern in FORBIDDEN.items():
            if pattern.search(content):
                errors.append(f"{label}: {relative}")

    compile_result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(ROOT / "scripts"), str(ROOT / "verl" / "verl")],
        check=False,
    )
    if compile_result.returncode:
        errors.append("Python syntax compilation failed")

    if errors:
        print("release check failed:")
        for error in sorted(set(errors)):
            print(f"- {error}")
        raise SystemExit(1)

    print("release check passed")


if __name__ == "__main__":
    main()
