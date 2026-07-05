#!/usr/bin/env python3
"""Clone or update source repositories used by the prompt importer."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/source-repos"

REPOS = [
    ("xianyu110", "awesome-nanobananapro-prompts"),
    ("xianyu110", "awesome-gptimage2"),
    ("xianyu110", "awesome-gemini-3-prompts"),
    ("xianyu110", "awesome-seedream-4.5"),
    ("YouMind-OpenLab", "ai-image-prompts-skill"),
    ("YouMind-OpenLab", "awesome-gpt-image-2"),
    ("YouMind-OpenLab", "awesome-nano-banana-pro-prompts"),
    ("YouMind-OpenLab", "awesome-gpt-image-1.5"),
    ("YouMind-OpenLab", "awesome-seedream-4.5"),
    ("YouMind-OpenLab", "awesome-gemini-3-prompts"),
    ("YouMind-OpenLab", "awesome-christmas-card-prompts"),
    ("YouMind-OpenLab", "awesome-grok-imagine-prompts"),
    ("YouMind-OpenLab", "awesome-seedance-2-prompts"),
]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def sync_repo(owner: str, repo: str) -> None:
    dest = CACHE / owner / repo
    if (dest / ".git").exists():
        print(f"update {owner}/{repo}")
        run(["git", "fetch", "--depth", "1", "origin", "main"], cwd=dest)
        run(["git", "checkout", "-q", "FETCH_HEAD"], cwd=dest)
        return

    print(f"clone {owner}/{repo}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", str(dest)])


def main() -> int:
    for owner, repo in REPOS:
        sync_repo(owner, repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
