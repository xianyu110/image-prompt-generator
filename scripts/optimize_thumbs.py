#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "thumbs"
OUTPUT_DIR = ROOT / "assets" / "thumbs-optimized"
MAX_WIDTH = 720
QUALITY = 78


def output_path(source):
    return OUTPUT_DIR / f"{source.stem}.webp"


def optimize(source):
    target = output_path(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        if image.width > MAX_WIDTH:
            height = round(image.height * MAX_WIDTH / image.width)
            image = image.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
        save_kwargs = {"format": "WEBP", "quality": QUALITY, "method": 6}
        if image.mode == "RGBA":
            image.save(target, **save_kwargs)
        else:
            image.convert("RGB").save(target, **save_kwargs)
    return target


def main():
    generated = set()
    for source in sorted(SOURCE_DIR.iterdir()):
        if not source.is_file():
            continue
        target = optimize(source)
        generated.add(target.name)

    for stale in OUTPUT_DIR.glob("*.webp"):
        if stale.name not in generated:
            stale.unlink()

    total = sum(path.stat().st_size for path in OUTPUT_DIR.glob("*.webp"))
    print(f"optimized {len(generated)} thumbs into assets/thumbs-optimized")
    print(f"optimized size {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
