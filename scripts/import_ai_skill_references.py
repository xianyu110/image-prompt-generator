#!/usr/bin/env python3
"""Import image prompts from YouMind OpenLab AI skill reference data."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/source-repos"
OWNER = "YouMind-OpenLab"
REPO = "ai-image-prompts-skill"
SOURCE_REPO = f"{OWNER}/{REPO}"
REFERENCES = CACHE / OWNER / REPO / "references"
ASSET_ROOT = ROOT / "assets/imported" / OWNER / REPO
PROMPTS_DATA = ROOT / "data/prompts.json"
IMPORTED_DATA = ROOT / "data/imported-prompts.json"

TARGET_TOTAL = int(os.environ.get("PROMPT_TARGET_TOTAL", "3000"))
MAX_ITEMS_ENV = os.environ.get("AI_SKILL_MAX_ITEMS")
WORKERS = int(os.environ.get("AI_SKILL_WORKERS", "8"))
MAX_SOURCE_BYTES = int(os.environ.get("AI_SKILL_MAX_SOURCE_BYTES", str(8 * 1024 * 1024)))
MAX_IMAGE_SIDE = int(os.environ.get("AI_SKILL_MAX_IMAGE_SIDE", "1024"))
WEBP_QUALITY = int(os.environ.get("AI_SKILL_WEBP_QUALITY", "78"))
USER_AGENT = "image-prompt-generator-importer/1.0"

CATEGORY_META = {
    "app-web-design": ("App / Web Design", "App / Web Design"),
    "comic-storyboard": ("Comic / Storyboard", "Comic / Storyboard"),
    "ecommerce-main-image": ("Ecommerce Main Image", "Ecommerce"),
    "game-asset": ("Game Asset", "Game Asset"),
    "infographic-edu-visual": ("Infographic / Education", "Infographic"),
    "others": ("Creative", "Creative"),
    "poster-flyer": ("Poster / Flyer", "Poster"),
    "product-marketing": ("Product Marketing", "Product"),
    "profile-avatar": ("Profile / Avatar", "Portrait"),
    "social-media-post": ("Social Media Post", "Social"),
    "youtube-thumbnail": ("YouTube Thumbnail", "Thumbnail"),
}


@dataclass(frozen=True)
class Candidate:
    category_slug: str
    category: str
    style: str
    source_file: Path
    index: int
    item: dict
    media_url: str


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:110] or "item"


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reference_files() -> list[Path]:
    manifest = REFERENCES / "manifest.json"
    if manifest.exists():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        items = payload.get("categories", []) if isinstance(payload, dict) else payload
        files = [REFERENCES / item["file"] for item in items if item.get("file") != "manifest.json"]
        return [path for path in files if path.exists()]
    return sorted(path for path in REFERENCES.glob("*.json") if path.name != "manifest.json")


def github_source_url(file_path: Path) -> str:
    return f"https://github.com/{SOURCE_REPO}/blob/main/references/{file_path.name}"


def model_for(item: dict) -> str:
    text = " ".join(
        clean(item.get(key)).lower()
        for key in ("title", "description", "content")
    )
    if "seedream" in text or "doubao" in text:
        return "Seedream 5 Pro"
    if "gpt image 2" in text or "gpt-image-2" in text:
        return "GPT Image 2"
    if "gpt image" in text or "gpt-image" in text:
        return "GPT Image"
    if "nano banana pro" in text:
        return "Nano Banana Pro"
    if "nano banana" in text or "gemini" in text:
        return "Nano Banana Pro"
    if "midjourney" in text:
        return "Midjourney"
    if "flux" in text:
        return "Flux"
    if "stable diffusion" in text:
        return "Stable Diffusion"
    return "AI Image Model"


def valid_media(source_media: object) -> list[str]:
    if not isinstance(source_media, list):
        return []
    urls = []
    for value in source_media:
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            urls.append(value)
    return urls


def iter_candidates() -> list[Candidate]:
    grouped: list[list[Candidate]] = []
    seen: set[str] = set()
    for file_path in reference_files():
        category_slug = file_path.stem
        category, style = CATEGORY_META.get(category_slug, (category_slug.replace("-", " ").title(), "Creative"))
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        group = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            prompt = clean(item.get("content"))
            media = valid_media(item.get("sourceMedia"))
            if len(prompt) < 40 or not media:
                continue
            dedupe_key = hashlib.sha1(f"{prompt}\n{media[0]}".encode("utf-8")).hexdigest()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            group.append(Candidate(category_slug, category, style, file_path, index, item, media[0]))
        if group:
            grouped.append(group)

    ordered = []
    for bundle in itertools.zip_longest(*grouped):
        ordered.extend(candidate for candidate in bundle if candidate is not None)
    return ordered


def fetch_bytes(url: str) -> bytes | None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".download") as handle:
        tmp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "--silent",
                "--show-error",
                "--max-time",
                "10",
                "--max-filesize",
                str(MAX_SOURCE_BYTES),
                "--user-agent",
                USER_AGENT,
                "--output",
                str(tmp_path),
                url,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0 or not tmp_path.exists() or tmp_path.stat().st_size == 0:
            return None
        if tmp_path.stat().st_size > MAX_SOURCE_BYTES:
            return None
        return tmp_path.read_bytes()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def to_webp(data: bytes) -> bytes | None:
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError):
        return None

    if max(image.size) > MAX_IMAGE_SIDE:
        image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS)

    if image.mode in {"RGBA", "LA"} or image.info.get("transparency") is not None:
        base = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        base.paste(image, mask=image.getchannel("A"))
        image = base
    elif image.mode != "RGB":
        image = image.convert("RGB")

    output = BytesIO()
    image.save(output, format="WEBP", quality=WEBP_QUALITY, method=6)
    return output.getvalue()


def image_path_for(candidate: Candidate) -> Path:
    item_id = clean(candidate.item.get("id")) or str(candidate.index + 1)
    title = clean(candidate.item.get("title")) or f"{candidate.category} prompt"
    stem = slug(f"{candidate.category_slug}-{item_id}-{candidate.index + 1}-{title}")
    return ASSET_ROOT / candidate.category_slug / f"{stem}.webp"


def save_image(candidate: Candidate) -> str | None:
    dest = image_path_for(candidate)
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest.relative_to(ROOT))

    data = fetch_bytes(candidate.media_url)
    if not data:
        return None
    webp = to_webp(data)
    if not webp:
        return None

    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, suffix=".tmp") as handle:
        tmp_path = Path(handle.name)
        handle.write(webp)
    tmp_path.replace(dest)
    return str(dest.relative_to(ROOT))


def row_from(candidate: Candidate) -> dict | None:
    prompt = clean(candidate.item.get("content"))
    title = clean(candidate.item.get("title")) or f"{candidate.category} prompt"
    image = save_image(candidate)
    if not image:
        return None
    item_id = clean(candidate.item.get("id")) or str(candidate.index + 1)
    row = {
        "id": f"ym-ai-skill-{slug(candidate.category_slug)}-{slug(item_id)}-{candidate.index + 1}",
        "title": title,
        "model": model_for(candidate.item),
        "category": candidate.category,
        "style": candidate.style,
        "useCase": candidate.category,
        "source": "YouMind OpenLab",
        "sourceUrl": github_source_url(candidate.source_file),
        "sourceRepo": SOURCE_REPO,
        "sourceFile": f"references/{candidate.source_file.name}#{item_id}",
        "image": image,
        "prompt": prompt,
        "language": "en",
        "license": "check source repository",
    }
    description = clean(candidate.item.get("description"))
    if description:
        row["description"] = description
    return row


def import_limit() -> int:
    if MAX_ITEMS_ENV:
        return int(MAX_ITEMS_ENV)
    payload = load_json(PROMPTS_DATA)
    base_count = sum(1 for item in payload.get("prompts", []) if item.get("sourceRepo") != SOURCE_REPO)
    return max(0, TARGET_TOTAL - base_count + 200)


def collect_rows(limit: int) -> list[dict]:
    rows = []
    candidates = iter_candidates()
    print(f"candidate image prompts: {len(candidates)}")

    offset = 0
    batch_size = max(WORKERS * 4, 16)
    while len(rows) < limit and offset < len(candidates):
        batch = candidates[offset : offset + batch_size]
        offset += batch_size
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for row in executor.map(row_from, batch):
                if row:
                    rows.append(row)
                    if len(rows) % 100 == 0:
                        print(f"downloaded image prompts: {len(rows)}")
                    if len(rows) >= limit:
                        break
    return rows


def merge_prompts(imported_rows: list[dict]) -> None:
    payload = load_json(PROMPTS_DATA)
    existing = [item for item in payload.get("prompts", []) if item.get("sourceRepo") != SOURCE_REPO]
    by_id = {item["id"]: item for item in existing if item.get("id")}
    for item in imported_rows:
        by_id[item["id"]] = item
    payload["prompts"] = list(by_id.values())
    payload.setdefault("meta", {})["count"] = len(payload["prompts"])
    payload["meta"]["importedCount"] = sum(1 for item in payload["prompts"] if item.get("sourceRepo"))
    generated_from = payload["meta"].setdefault("generatedFrom", [])
    source_name = f"{SOURCE_REPO}/references/*.json"
    if source_name not in generated_from:
        generated_from.append(source_name)
    write_json(PROMPTS_DATA, payload)


def merge_imported(imported_rows: list[dict]) -> None:
    if IMPORTED_DATA.exists():
        payload = load_json(IMPORTED_DATA)
        prompts = payload.get("prompts", [])
        sources = payload.get("meta", {}).get("sources", [])
    else:
        prompts = []
        sources = []

    prompts = [item for item in prompts if item.get("sourceRepo") != SOURCE_REPO]
    prompts.extend(imported_rows)

    counts: dict[str, int] = {}
    for row in imported_rows:
        source_file = row.get("sourceFile", "").split("#", 1)[0]
        counts[source_file] = counts.get(source_file, 0) + 1

    sources = [item for item in sources if item.get("repo") != SOURCE_REPO]
    sources.append(
        {
            "repo": SOURCE_REPO,
            "file": "references/*.json",
            "items": len(imported_rows),
            "categories": counts,
        }
    )
    write_json(IMPORTED_DATA, {"meta": {"count": len(prompts), "sources": sources}, "prompts": prompts})


def main() -> int:
    if not REFERENCES.exists():
        print(f"missing source references: {REFERENCES}")
        return 2

    limit = import_limit()
    if limit <= 0:
        print("target already satisfied; nothing to import")
        return 0

    print(f"source: {SOURCE_REPO}")
    print(f"target import count: {limit}")
    rows = collect_rows(limit)
    if len(rows) < limit:
        print(f"warning: imported {len(rows)} image prompts, below requested {limit}")

    merge_imported(rows)
    merge_prompts(rows)
    print(f"imported image prompts: {len(rows)}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
