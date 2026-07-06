#!/usr/bin/env python3
"""Fast importer for selected image prompt sources."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CACHE = ROOT / ".cache/source-repos"
ASSET_ROOT = ROOT / "assets/imported"
IMPORTED_DATA = ROOT / "data/imported-prompts.json"
PROMPTS_DATA = ROOT / "data/prompts.json"
MAX_PER_SOURCE = int(os.environ.get("MAX_PER_SOURCE", "80"))
MAX_BYTES = 5 * 1024 * 1024
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
SOURCE_LIMIT_OVERRIDES = {
    ("YouMind-OpenLab", "awesome-seedream-4.5"): None,
}


SOURCES = [
    ("xianyu110", "awesome-nanobananapro-prompts", CACHE / "xianyu110/awesome-nanobananapro-prompts/gpt4o-image-prompts-master/100.md"),
    ("xianyu110", "awesome-gptimage2", CACHE / "xianyu110/awesome-gptimage2/data/latest-prompts.json"),
    ("xianyu110", "awesome-gemini-3-prompts", CACHE / "xianyu110/awesome-gemini-3-prompts/README.md"),
    ("xianyu110", "awesome-seedream-4.5", CACHE / "xianyu110/awesome-seedream-4.5/README.md"),
    ("YouMind-OpenLab", "awesome-gpt-image-2", CACHE / "YouMind-OpenLab/awesome-gpt-image-2/README.md"),
    ("YouMind-OpenLab", "awesome-nano-banana-pro-prompts", CACHE / "YouMind-OpenLab/awesome-nano-banana-pro-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-gpt-image-1.5", CACHE / "YouMind-OpenLab/awesome-gpt-image-1.5/README.md"),
    ("YouMind-OpenLab", "awesome-seedream-4.5", CACHE / "YouMind-OpenLab/awesome-seedream-4.5/README.md"),
    ("YouMind-OpenLab", "awesome-gemini-3-prompts", CACHE / "YouMind-OpenLab/awesome-gemini-3-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-christmas-card-prompts", CACHE / "YouMind-OpenLab/awesome-christmas-card-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-grok-imagine-prompts", CACHE / "YouMind-OpenLab/awesome-grok-imagine-prompts/README.md"),
    ("YouMind-OpenLab", "awesome-seedance-2-prompts", CACHE / "YouMind-OpenLab/awesome-seedance-2-prompts/README.md"),
]
KNOWN_SOURCE_REPOS = {f"{owner}/{repo}" for owner, repo, _ in SOURCES}
LOCAL_SOURCE_FALLBACKS = {
    ("xianyu110", "awesome-nanobananapro-prompts"): WORKSPACE / "awesome-nanobananapro-prompts/gpt4o-image-prompts-master/100.md",
    ("xianyu110", "awesome-gptimage2"): WORKSPACE / "awesome-gptimage2/data/latest-prompts.json",
}


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:100] or "item"


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def title_and_source(title: str, block: str, fallback_source: str, fallback_url: str) -> tuple[str, str, str]:
    source = fallback_source
    url = fallback_url
    title_match = re.search(r"^(.*?)\s*\(来源\s+\[([^\]]+)\]\(([^)]+)\)\)\s*$", title)
    if title_match:
        title = clean(title_match.group(1))
        source = clean(title_match.group(2))
        url = title_match.group(3)
    author_match = re.search(
        r"\*\*Author:\*\*\s*\[?([^\]\n]+)|作者\s*[:：]\s*([^\n]+)|来源\s+\[([^\]]+)\]\(([^)]+)\)",
        block,
    )
    if author_match:
        groups = author_match.groups()
        source = clean(groups[0] or groups[1] or groups[2] or source)
        url = groups[3] or url
    title = re.sub(r"^案例\s+\d+\s*[：:]\s*", "", title).strip()
    return title, source, url


def model_for(repo: str) -> str:
    text = repo.lower()
    if "gpt-image-2" in text or "gptimage2" in text:
        return "GPT Image 2"
    if "gpt-image-1.5" in text:
        return "GPT Image 1.5"
    if "seedream" in text:
        return "Seedream 5 Pro"
    if "gemini-3" in text:
        return "Gemini 3 Pro"
    if "grok" in text:
        return "Grok Imagine"
    if "seedance" in text:
        return "Seedance 2.0"
    if "nano" in text or "banana" in text or "gemini" in text:
        return "Nano Banana Pro"
    return "AI Image Model"


def source_limit(owner: str, repo: str) -> int | None:
    return SOURCE_LIMIT_OVERRIDES.get((owner, repo), MAX_PER_SOURCE)


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
    matches = [
        match
        for match in re.finditer(r"^###\s+(.+)$", text, re.M)
        if "Prompt" in text[match.end() : match.end() + 2500]
    ]
    blocks = []
    for index, match in enumerate(matches):
        title = clean(match.group(1))
        title = re.sub(r"^No\.\s*\d+\s*:\s*", "", title).strip()
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
            tmp = dest.with_suffix(dest.suffix + ".tmp")
            result = subprocess.run(
                ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "12", "--output", str(tmp), src],
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0 or tmp.stat().st_size > MAX_BYTES:
                if tmp.exists():
                    tmp.unlink()
                return None
            tmp.replace(dest)
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


def parse_markdown(owner: str, repo: str, file_path: Path, limit: int | None) -> list[dict]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    rows = []
    for title, block in parse_blocks(text):
        prompt = prompt_from(block)
        image_candidates = images_from(block)
        if not prompt or not image_candidates:
            continue
        fallback_url = source_url(owner, repo, file_path)
        clean_title, author, item_source_url = title_and_source(title, block, repo, fallback_url)
        item_slug = slug(f"{file_path.stem}-{len(rows) + 1}-{title}")
        image = None
        for candidate in image_candidates:
            image = save_image(candidate, owner, repo, file_path, item_slug)
            if image:
                break
        if not image:
            continue
        category = category_for(clean_title, prompt)
        rows.append(
            {
                "id": f"import-{slug(owner)}-{slug(repo)}-{len(rows) + 1}",
                "title": clean_title,
                "model": model_for(repo),
                "category": category,
                "style": category,
                "useCase": category,
                "source": author,
                "sourceUrl": item_source_url,
                "sourceRepo": f"{owner}/{repo}",
                "sourceFile": str(file_path),
                "image": image,
                "prompt": prompt,
                "language": "mixed",
                "license": "check source repository",
            }
        )
        if limit is not None and len(rows) >= limit:
            break
    return rows


def parse_json(owner: str, repo: str, file_path: Path, limit: int | None) -> list[dict]:
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
        if limit is not None and len(rows) >= limit:
            break
    return rows


def merge(imported: list[dict], selected_repos: set[str]) -> None:
    payload = json.loads(PROMPTS_DATA.read_text(encoding="utf-8"))
    existing = [
        item
        for item in payload.get("prompts", [])
        if item.get("sourceRepo") not in selected_repos
    ]
    prompts = {item["id"]: item for item in existing}
    for item in imported:
        prompts[item["id"]] = item
    payload["prompts"] = list(prompts.values())
    payload.setdefault("meta", {})["count"] = len(payload["prompts"])
    payload["meta"]["importedCount"] = sum(1 for item in payload["prompts"] if item.get("sourceRepo"))
    PROMPTS_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_imported(imported: list[dict], summary: list[dict], selected_repos: set[str]) -> None:
    if IMPORTED_DATA.exists():
        payload = json.loads(IMPORTED_DATA.read_text(encoding="utf-8"))
        existing_prompts = payload.get("prompts", [])
        existing_sources = payload.get("meta", {}).get("sources", [])
    else:
        existing_prompts = []
        existing_sources = []

    prompts = [
        item
        for item in existing_prompts
        if item.get("sourceRepo") not in selected_repos
    ]
    prompts.extend(imported)
    sources = [
        item
        for item in existing_sources
        if item.get("repo") not in selected_repos
    ]
    sources.extend(summary)
    IMPORTED_DATA.write_text(
        json.dumps({"meta": {"count": len(prompts), "sources": sources}, "prompts": prompts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def selected_sources(args: list[str]) -> list[tuple[str, str, Path]]:
    if not args:
        return SOURCES
    wanted = set(args)
    selected = [
        source
        for source in SOURCES
        if f"{source[0]}/{source[1]}" in wanted or source[1] in wanted
    ]
    missing = wanted - {f"{owner}/{repo}" for owner, repo, _ in selected} - {repo for _, repo, _ in selected}
    if missing:
        print(f"unknown source filter: {', '.join(sorted(missing))}", file=sys.stderr)
    return selected


def resolve_source_path(owner: str, repo: str, file_path: Path) -> Path:
    if file_path.exists():
        return file_path
    fallback = LOCAL_SOURCE_FALLBACKS.get((owner, repo))
    if fallback and fallback.exists():
        return fallback
    return file_path


def main() -> int:
    sources = selected_sources(sys.argv[1:])
    if not sources:
        return 2
    selected_repos = {f"{owner}/{repo}" for owner, repo, _ in sources}
    imported = []
    summary = []
    for owner, repo, file_path in sources:
        file_path = resolve_source_path(owner, repo, file_path)
        if not file_path.exists():
            print(f"skip missing {owner}/{repo}: {file_path}")
            continue
        limit = source_limit(owner, repo)
        if file_path.suffix.lower() == ".json":
            rows = parse_json(owner, repo, file_path, limit)
        else:
            rows = parse_markdown(owner, repo, file_path, limit)
        imported.extend(rows)
        summary.append({"repo": f"{owner}/{repo}", "file": str(file_path), "items": len(rows)})
        print(f"{owner}/{repo}: {len(rows)}")
    write_imported(imported, summary, selected_repos)
    merge(imported, selected_repos)
    print(f"imported total: {len(imported)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
