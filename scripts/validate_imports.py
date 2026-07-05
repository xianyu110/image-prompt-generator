#!/usr/bin/env python3
"""Validate prompt JSON and imported image references."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    prompts = load_json(ROOT / "data/prompts.json").get("prompts", [])
    imported = load_json(ROOT / "data/imported-prompts.json").get("prompts", [])

    missing = []
    for item in imported:
        image = item.get("image")
        if not image or not (ROOT / image).is_file():
            missing.append((item.get("id"), image))

    print(f"prompts: {len(prompts)}")
    print(f"imported prompts: {len(imported)}")
    print(f"missing imported images: {len(missing)}")
    for item_id, image in missing[:20]:
        print(f"missing: {item_id} -> {image}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
