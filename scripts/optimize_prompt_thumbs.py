#!/usr/bin/env python3
"""Build small WebP card previews for imported prompt images.

Deploy publishes assets/prompt-thumbs (not assets/imported). Cards should point at
these same-origin thumbs instead of raw.githubusercontent.com hotlinks.
"""
from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "data" / "prompts"
OUTPUT_DIR = ROOT / "assets" / "prompt-thumbs"
VARIANTS_PATH = ROOT / "data" / "prompt-image-variants.json"
MAX_WIDTH = 640
QUALITY = 72
WORKERS = max(2, min(8, (os.cpu_count() or 4)))


def thumb_name(source_rel: str) -> str:
    digest = hashlib.sha1(source_rel.encode("utf-8")).hexdigest()[:20]
    return f"{digest}.webp"


def collect_imported_images() -> list[str]:
    images: set[str] = set()
    for path in sorted(PROMPTS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        for prompt in data.get("prompts", []):
            image = prompt.get("image") or ""
            if image.startswith("assets/imported/"):
                images.add(image)
    return sorted(images)


def optimize_one(source_rel: str) -> tuple[str, str, int] | tuple[str, None, str]:
    source = ROOT / source_rel
    if not source.is_file():
        return source_rel, None, "missing"
    target_rel = f"assets/prompt-thumbs/{thumb_name(source_rel)}"
    target = ROOT / target_rel
    try:
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            if image.width > MAX_WIDTH:
                height = round(image.height * MAX_WIDTH / image.width)
                image = image.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
            target.parent.mkdir(parents=True, exist_ok=True)
            save_kwargs = {"format": "WEBP", "quality": QUALITY, "method": 4}
            if image.mode == "RGBA":
                image.save(target, **save_kwargs)
            else:
                image.convert("RGB").save(target, **save_kwargs)
        return source_rel, target_rel, target.stat().st_size
    except Exception as exc:  # noqa: BLE001 - keep batch going
        return source_rel, None, str(exc)


def main() -> None:
    sources = collect_imported_images()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    variants: dict[str, str] = {}
    errors = 0
    total_bytes = 0

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(optimize_one, source) for source in sources]
        for future in as_completed(futures):
            source_rel, target_rel, meta = future.result()
            if target_rel:
                variants[source_rel] = target_rel
                total_bytes += int(meta)
            else:
                errors += 1
                print(f"skip {source_rel}: {meta}")

    keep = {Path(path).name for path in variants.values()}
    for stale in OUTPUT_DIR.glob("*.webp"):
        if stale.name not in keep:
            stale.unlink()

    VARIANTS_PATH.write_text(
        json.dumps(
            {
                "generatedFor": "card-previews",
                "maxWidth": MAX_WIDTH,
                "quality": QUALITY,
                "count": len(variants),
                "variants": variants,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    print(f"optimized {len(variants)} / {len(sources)} imported images")
    print(f"prompt-thumbs size {total_bytes / 1024 / 1024:.2f} MB")
    print(f"errors {errors}")
    print(f"wrote {VARIANTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
