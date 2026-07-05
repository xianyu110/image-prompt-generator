#!/usr/bin/env python3
"""Fast importer for selected image prompt sources."""

from __future__ import annotations

import json
import re
import shutil
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CACHE = ROOT / ".cache/source-repos"
ASSET_ROOT = ROOT / "assets/imported"
IMPORTED_DATA = ROOT / "data/imported-prompts.json"
PROMPTS_DATA = ROOT / "data/prompts.json"
MAX_PER_SOURCE = 80
MAX_BYTES = 5 * 1024 * 1024
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


SOURCES = [
    ("xianyu110", "awesome-nanobananapro-prompts", WORKSPACE / "awesome-nanobananapro-prompts/gpt4o-image-prompts-master/100.md"),
    ("xianyu110", "awesome-gptimage2", WORKSPACE / "awesome-gptimage2/data/latest-prompts.json"),
    ("YouMind-OpenLab", "awesome-gpt-image-2", CACHE / "YouMind-OpenLab/awesome-gpt-image-2/README.md"),
    ("YouMind-OpenLab", "awesome-nano-banana-pro-prompts", CACHE / "YouMind-OpenLab/awesome-nano-banana-pro-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-gpt-image-1.5", CACHE / "YouMind-OpenLab/awesome-gpt-image-1.5/README.md"),
    ("YouMind-OpenLab", "awesome-seedream-4.5", CACHE / "YouMind-OpenLab/awesome-seedream-4.5/README.md"),
    ("YouMind-OpenLab", "awesome-gemini-3-prompts", CACHE / "YouMind-OpenLab/awesome-gemini-3-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-christmas-card-prompts", CACHE / "YouMind-OpenLab/awesome-christmas-card-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-grok-imagine-prompts", CACHE / "YouMind-OpenLab/awesome-grok-imagine-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-seedance-2-prompts", CACHE / "YouMind-OpenLab/awesome-seedance-2-prompts/README.md"),
]


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:100] or "item"


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def model_for(repo: str) -> str:
    text = repo.lower()
    if "gpt-image-2" in text or "gptimage2" in text:
        return "GPT Image 2"
    if "gpt-image-1.5" in text:
        return "GPT Image 1.5"
    if "seedream" in text:
        return "Seedream"
    if "grok" in text:
        return "Grok Imagine"
    if "seedance" in text:
        return "Seedance"
    if "nano" in text or "banana" in text or "gemini" in text:
        return "Nano Banana Pro"
    return "AI Image Model"


def category_for(title: str, prompt: str) -> str:
    text = f"{title} {prompt}".lower()
    if any(x in text for x in ["product", "brand", "logo", "商品", "品牌", "包装", "广告"]):
        return "Product"
    if any(x in text for x in ["portrait", "character", "avatar", "人物", "肖像", "角色"]):
        return "Portrait"
    if any(x in text for x in ["3d", "diorama", "miniature", "clay", "立体", "微型", "雕塑"]):
        return "3D"
    if any(x in text for x in ["poster", "typography", "海报", "字体", "文字"]):
        return "Poster"
    if any(x in text for x in ["infographic", "diagram", "card", "信息图", "卡片"]):
        return "Infographic"
    if any(x in text for x in ["video", "cinematic", "film", "视频", "电影"]):
        return "Video"
    return "Creative"


def source_url(owner: str, repo: str, file_path: Path) -> str:
    try:
        rel = file_path.relative_to(CACHE / owner / repo)
    except ValueError:
        try:
            rel = file_path.relative_to(WORKSPACE / repo)
        except ValueError:
            rel = file_path.name
    return f"https://github.com/{owner}/{repo}/blob/main/{rel}"


def parse_blocks(text: str) -> list[tuple[str, str]]:
    no_matches = list(re.finditer(r"^### No\.\s*\d+:\s*(.+)$", text, re.M))
    if no_matches:
        blocks = []
        for index, match in enumerate(no_matches):
            title = clean(match.group(1))
            start = match.end()
            end = no_matches[index + 1].start() if index + 1 < len(no_matches) else len(text)
            blocks.append((title, text[start:end]))
        return blocks
    matches = list(re.finditer(r"^(#{2,4})\s+(.+)$", text, re.M))
    blocks = []
    for index, match in enumerate(matches):
        title = clean(match.group(2))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((title, text[start:end]))
    return blocks


def images_from(block: str) -> list[str]:
    values = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)["\']', block, re.I)
    values += re.findall(r"!\[[^\]]*\]\(([^)]+)\)", block)
    result = []
    for value in values:
        value = value.strip()
        if not value or "img.shields.io" in value or "awesome.re/" in value or "badge" in value:
            continue
        result.append(value)
    return result


def prompt_from(block: str) -> str | None:
    if not any(label in block for label in ["Prompt", "prompt", "提示词", "📝"]):
        return None
    for code in re.findall(r"```(?:[a-zA-Z]+)?\s*(.*?)```", block, re.S):
        code = code.strip()
        if len(code) > 40 and not code.startswith(("npm ", "pnpm ", "git ")):
            return code
    match = re.search(r"(?:Prompt|prompt|提示词)[:：]\s*(.+)", block)
    if match:
        value = clean(match.group(1))
        if len(value) > 40:
            return value
    return None


def save_image(src: str, owner: str, repo: str, file_path: Path, item_slug: str) -> str | None:
    suffix = Path(src.split("?", 1)[0]).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        suffix = ".jpg"
    dest_dir = ASSET_ROOT / slug(owner) / slug(repo)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{item_slug}{suffix}"
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest.relative_to(ROOT))

    if src.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                return None
            dest.write_bytes(data)
            return str(dest.relative_to(ROOT))
        except Exception:
            return None

    base = file_path.parent
    local = (base / src.split("#", 1)[0].split("?", 1)[0]).resolve()
    try:
        local.relative_to(file_path.parents[0].resolve())
    except ValueError:
        pass
    if local.exists() and local.is_file() and local.stat().st_size <= MAX_BYTES:
        shutil.copy2(local, dest)
        return str(dest.relative_to(ROOT))
    return None


def parse_markdown(owner: str, repo: str, file_path: Path) -> list[dict]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    rows = []
    for title, block in parse_blocks(text):
        prompt = prompt_from(block)
        image_candidates = images_from(block)
        if not prompt or not image_candidates:
            continue
        item_slug = slug(f"{file_path.stem}-{len(rows) + 1}-{title}")
        image = None
        for candidate in image_candidates:
            image = save_image(candidate, owner, repo, file_path, item_slug)
            if image:
                break
        if not image:
            continue
        author = repo
        author_match = re.search(r"\*\*Author:\*\*\s*\[?([^\]\n]+)|作者\s*[:：]\s*([^\n]+)|来源\s+\[([^\]]+)\]", block)
        if author_match:
            author = clean(next(group for group in author_match.groups() if group))
        category = category_for(title, prompt)
        rows.append(
            {
                "id": f"import-{slug(owner)}-{slug(repo)}-{len(rows) + 1}",
                "title": title,
                "model": model_for(repo),
                "category": category,
                "style": category,
                "useCase": category,
                "source": author,
                "sourceUrl": source_url(owner, repo, file_path),
                "sourceRepo": f"{owner}/{repo}",
                "sourceFile": str(file_path),
                "image": image,
                "prompt": prompt,
                "language": "mixed",
                "license": "check source repository",
            }
        )
        if len(rows) >= MAX_PER_SOURCE:
            break
    return rows


def parse_json(owner: str, repo: str, file_path: Path) -> list[dict]:
    data = json.loads(file_path.read_text(encoding="utf-8"))
    items = []
    if isinstance(data, dict):
        for group in data.get("dates", []):
            items.extend(group.get("items", []))
        for key in ["prompts", "items", "data"]:
            if isinstance(data.get(key), list):
                items.extend(data[key])
    elif isinstance(data, list):
        items = data
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        prompt = item.get("prompt") or item.get("text") or item.get("content")
        image_src = item.get("primary_image_url") or item.get("image") or item.get("image_url") or item.get("imageUrl")
        if not isinstance(prompt, str) or len(prompt) < 40 or not isinstance(image_src, str):
            continue
        title = clean(item.get("reason") or item.get("title") or f"{repo} prompt {len(rows) + 1}")
        item_slug = slug(f"{file_path.stem}-{len(rows) + 1}-{title}")
        image = save_image(image_src, owner, repo, file_path, item_slug)
        if not image:
            continue
        category = category_for(title, prompt)
        rows.append(
            {
                "id": f"import-{slug(owner)}-{slug(repo)}-{len(rows) + 1}",
                "title": title,
                "model": model_for(repo),
                "category": category,
                "style": category,
                "useCase": category,
                "source": clean(item.get("author") or repo),
                "sourceUrl": item.get("x_url") or item.get("url") or source_url(owner, repo, file_path),
                "sourceRepo": f"{owner}/{repo}",
                "sourceFile": str(file_path),
                "image": image,
                "prompt": prompt,
                "language": "mixed",
                "license": "check source repository",
            }
        )
        if len(rows) >= MAX_PER_SOURCE:
            break
    return rows


def merge(imported: list[dict]) -> None:
    payload = json.loads(PROMPTS_DATA.read_text(encoding="utf-8"))
    prompts = {item["id"]: item for item in payload.get("prompts", [])}
    for item in imported:
        prompts[item["id"]] = item
    payload["prompts"] = list(prompts.values())
    payload.setdefault("meta", {})["count"] = len(payload["prompts"])
    payload["meta"]["importedCount"] = len(imported)
    PROMPTS_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    imported = []
    summary = []
    for owner, repo, file_path in SOURCES:
        if not file_path.exists():
            print(f"skip missing {owner}/{repo}: {file_path}")
            continue
        if file_path.suffix.lower() == ".json":
            rows = parse_json(owner, repo, file_path)
        else:
            rows = parse_markdown(owner, repo, file_path)
        imported.extend(rows)
        summary.append({"repo": f"{owner}/{repo}", "file": str(file_path), "items": len(rows)})
        print(f"{owner}/{repo}: {len(rows)}")
    IMPORTED_DATA.write_text(json.dumps({"meta": {"count": len(imported), "sources": summary}, "prompts": imported}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    merge(imported)
    print(f"imported total: {len(imported)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
