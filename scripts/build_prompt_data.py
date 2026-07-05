#!/usr/bin/env python3
import json
import re
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://image-prompt-generator.com"
RAW_ASSET_BASE = "https://raw.githubusercontent.com/xianyu110/image-prompt-generator/main/"
PROMPTS_DIR = ROOT / "data" / "prompts"

MODEL_PAGE_SLUGS = {
    "GPT Image 2": "gpt-image-2-prompts",
    "Seedream 5 Pro": "seedream-5-pro-prompts",
    "Seedance 2.0": "seedance-2-prompts",
    "Grok Imagine": "grok-imagine-prompts",
    "Gemini 3 Pro": "gemini-3-pro-prompts",
}

PUBLIC_FIELDS = (
    "id",
    "title",
    "model",
    "category",
    "source",
    "sourceUrl",
    "image",
    "prompt",
)


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "prompts"


def load_prompts():
    data = json.loads((ROOT / "data" / "prompts.json").read_text())
    return data.get("prompts", [])


def clean_prompt(item, order):
    prompt = {key: item.get(key, "") for key in PUBLIC_FIELDS}
    prompt["image"] = optimized_image_path(prompt.get("image") or "")
    prompt["order"] = order
    return prompt


def optimized_image_path(image):
    if image.startswith("assets/thumbs/"):
        source = Path(image)
        optimized = ROOT / "assets" / "thumbs-optimized" / f"{source.stem}.webp"
        if optimized.is_file():
            return f"assets/thumbs-optimized/{source.stem}.webp"
    return image


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


def image_url(image):
    if image.startswith("assets/thumbs-optimized/"):
        return f"{SITE_URL}/{image}"
    if image.startswith(("assets/imported/", "assets/thumbs/")):
        return RAW_ASSET_BASE + image
    if image.startswith(("http://", "https://")):
        return image
    return ""


def page_url_for_model(model):
    slug = MODEL_PAGE_SLUGS.get(model)
    if slug:
        return f"{SITE_URL}/{slug}/"
    return f"{SITE_URL}/"


def image_caption(item):
    prompt = " ".join(str(item.get("prompt") or "").split())
    if len(prompt) > 180:
        prompt = prompt[:180].rstrip() + "..."
    return prompt


def write_image_sitemap(prompts):
    grouped = defaultdict(list)
    seen = set()
    for item in prompts:
        image = image_url(item.get("image") or "")
        if not image or image in seen:
            continue
        seen.add(image)
        grouped[page_url_for_model(item.get("model"))].append(item)

    url_blocks = []
    for loc in sorted(grouped):
        images = sorted(
            grouped[loc],
            key=lambda item: (
                not image_url(item.get("image") or "").startswith(SITE_URL),
                not bool(MODEL_PAGE_SLUGS.get(item.get("model"))),
                item.get("order", 0),
            ),
        )[:1000]
        image_blocks = []
        for item in images:
            image = image_url(item.get("image") or "")
            title = item.get("title") or f"{item.get('model') or 'AI image'} prompt example"
            caption = image_caption(item)
            image_blocks.append(
                "    <image:image>\n"
                f"      <image:loc>{escape(image)}</image:loc>\n"
                f"      <image:title>{escape(str(title))}</image:title>\n"
                f"      <image:caption>{escape(caption)}</image:caption>\n"
                "    </image:image>"
            )
        url_blocks.append(
            "  <url>\n"
            f"    <loc>{escape(loc)}</loc>\n"
            + "\n".join(image_blocks)
            + "\n  </url>"
        )

    (ROOT / "image-sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(url_blocks)
        + "\n</urlset>\n"
    )


def main():
    prompts = load_prompts()
    by_model = defaultdict(list)
    categories = set()

    for order, item in enumerate(prompts):
        model = item.get("model") or "AI Image Model"
        clean = clean_prompt(item, order)
        by_model[model].append(clean)
        if clean.get("category"):
            categories.add(clean["category"])

    generated_files = set()
    index = {
        "generatedAt": date.today().isoformat(),
        "total": len(prompts),
        "categories": sorted(categories),
        "models": {},
    }

    for model in sorted(by_model):
        items = by_model[model]
        filename = f"{slugify(model)}.json"
        output = PROMPTS_DIR / filename
        write_json(output, {"model": model, "count": len(items), "prompts": items})
        generated_files.add(output.name)
        index["models"][model] = {
            "file": f"data/prompts/{filename}",
            "count": len(items),
            "images": sum(1 for item in items if item.get("image")),
            "categories": sorted({item.get("category") for item in items if item.get("category")}),
        }

    for stale in PROMPTS_DIR.glob("*.json"):
        if stale.name not in generated_files:
            stale.unlink()

    split_prompts = [item for model in sorted(by_model) for item in by_model[model]]
    write_json(ROOT / "data" / "prompt-index.json", index)
    write_image_sitemap(split_prompts)
    print(f"wrote {len(generated_files)} model prompt data files")
    print("updated data/prompt-index.json")
    print("updated image-sitemap.xml")


if __name__ == "__main__":
    main()
