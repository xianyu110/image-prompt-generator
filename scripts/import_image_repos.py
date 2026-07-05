#!/usr/bin/env python3
"""Import image prompt repositories into this static site.

The script clones selected public repositories from YouMind-OpenLab and xianyu110,
extracts prompt/image pairs from Markdown and JSON files, copies image files into
assets/imported, and merges records into data/prompts.json.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/source-repos"
IMPORTED_ASSETS = ROOT / "assets/imported"
IMPORTED_DATA = ROOT / "data/imported-prompts.json"
PROMPTS_DATA = ROOT / "data/prompts.json"

OWNERS = ["YouMind-OpenLab", "xianyu110"]
MAX_REPOS_PER_OWNER = 30
MAX_ITEMS_PER_REPO = int(os.environ.get("MAX_ITEMS_PER_REPO", "120"))
MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", str(4 * 1024 * 1024)))
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TEXT_SUFFIXES = {".md", ".mdx", ".json"}
REPO_KEYWORDS = [
    "image",
    "prompt",
    "prompts",
    "banana",
    "seedream",
    "gpt-image",
    "gptimage",
    "gemini",
    "gallery",
]


@dataclass
class Repo:
    owner: str
    name: str
    url: str
    description: str


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90] or "item"


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("\u200b", "")
    return re.sub(r"\s+", " ", value).strip()


def list_repos(owner: str) -> list[Repo]:
    result = run(
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            str(MAX_REPOS_PER_OWNER),
            "--json",
            "name,description,url,isArchived,isFork",
        ]
    )
    rows = json.loads(result.stdout)
    repos: list[Repo] = []
    for row in rows:
        haystack = f"{row.get('name') or ''} {row.get('description') or ''}".lower()
        if row.get("isArchived"):
            continue
        if any(keyword in haystack for keyword in REPO_KEYWORDS):
            repos.append(
                Repo(
                    owner=owner,
                    name=row["name"],
                    url=row["url"],
                    description=row.get("description") or "",
                )
            )
    return repos


def clone_or_update(repo: Repo) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / repo.owner / repo.name
    if (dest / ".git").exists():
        run(["git", "pull", "--ff-only"], cwd=dest, check=False)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", repo.url, str(dest)], check=False)
    return dest


def local_image_path(repo_path: Path, src: str) -> Path | None:
    src = src.split("#", 1)[0].split("?", 1)[0]
    if not src or src.startswith(("http://", "https://", "data:")):
        return None
    candidate = (repo_path / src).resolve()
    try:
        candidate.relative_to(repo_path.resolve())
    except ValueError:
        return None
    if candidate.exists() and candidate.suffix.lower() in IMAGE_SUFFIXES:
        return candidate
    return None


def copy_local_image(src: Path, owner: str, repo: str, item_slug: str) -> str | None:
    if not src.exists() or src.stat().st_size > MAX_IMAGE_BYTES:
        return None
    dest_dir = IMPORTED_ASSETS / slug(owner) / slug(repo)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{item_slug}{src.suffix.lower()}"
    counter = 2
    while dest.exists() and dest.stat().st_size != src.stat().st_size:
        dest = dest_dir / f"{item_slug}-{counter}{src.suffix.lower()}"
        counter += 1
    shutil.copy2(src, dest)
    return str(dest.relative_to(ROOT))


def download_remote_image(url: str, owner: str, repo: str, item_slug: str) -> str | None:
    if not url.startswith(("http://", "https://")):
        return None
    suffix = Path(url.split("?", 1)[0]).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        suffix = ".jpg"
    dest_dir = IMPORTED_ASSETS / slug(owner) / slug(repo)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{item_slug}{suffix}"
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest.relative_to(ROOT))
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES:
            return None
        dest.write_bytes(data)
        return str(dest.relative_to(ROOT))
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def resolve_image(repo_path: Path, src: str, owner: str, repo: str, item_slug: str) -> str | None:
    local = local_image_path(repo_path, src)
    if local:
        return copy_local_image(local, owner, repo, item_slug)
    return download_remote_image(src, owner, repo, item_slug)


def markdown_blocks(text: str) -> list[tuple[str, str]]:
    heading_pattern = re.compile(r"^(#{2,4})\s+(.+)$", re.M)
    matches = list(heading_pattern.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = clean_text(match.group(2))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((title, text[start:end]))
    return blocks


def extract_code_prompt(block: str) -> str | None:
    labels = ["提示词", "Prompt", "prompt", "PROMPT"]
    if not any(label in block for label in labels):
        return None
    code = re.search(r"```(?:text|txt|prompt|json)?\s*(.*?)```", block, re.S | re.I)
    if code:
        prompt = code.group(1).strip()
        if len(prompt) >= 24:
            return prompt
    quoted = re.search(r"(?:提示词|Prompt|prompt)[:：]\s*(.+)", block)
    if quoted:
        prompt = clean_text(quoted.group(1))
        if len(prompt) >= 24:
            return prompt
    return None


def extract_images(block: str) -> list[str]:
    html = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)["\']', block, flags=re.I)
    md = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", block)
    return [src.strip() for src in html + md if src.strip()]


def category_for(title: str, prompt: str) -> str:
    haystack = f"{title} {prompt}".lower()
    if any(word in haystack for word in ["product", "brand", "logo", "广告", "商品", "品牌", "包装"]):
        return "Product"
    if any(word in haystack for word in ["portrait", "character", "人物", "肖像", "角色"]):
        return "Portrait"
    if any(word in haystack for word in ["3d", "diorama", "clay", "miniature", "立体", "微型", "雕塑"]):
        return "3D"
    if any(word in haystack for word in ["poster", "typography", "海报", "字体", "文字"]):
        return "Poster"
    if any(word in haystack for word in ["infographic", "diagram", "card", "信息图", "卡片"]):
        return "Infographic"
    if any(word in haystack for word in ["video", "cinematic", "film", "视频", "电影"]):
        return "Video"
    return "Creative"


def model_for(repo_name: str, title: str, prompt: str) -> str:
    haystack = f"{repo_name} {title} {prompt}".lower()
    if "gpt-image-2" in haystack or "gpt image 2" in haystack or "gptimage2" in haystack:
        return "GPT Image 2"
    if "gpt-image-1.5" in haystack or "gpt image 1.5" in haystack:
        return "GPT Image 1.5"
    if "seedream" in haystack:
        return "Seedream"
    if "nano" in haystack or "banana" in haystack or "gemini" in haystack:
        return "Nano Banana Pro"
    if "grok" in haystack:
        return "Grok Imagine"
    if "seedance" in haystack:
        return "Seedance"
    return "AI Image Model"


def parse_markdown_file(path: Path, repo_path: Path, repo: Repo) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rows: list[dict] = []
    for title, block in markdown_blocks(text):
        prompt = extract_code_prompt(block)
        images = extract_images(block)
        if not prompt or not images:
            continue
        item_slug = slug(f"{path.stem}-{len(rows) + 1}-{title}")
        image = resolve_image(repo_path, images[0], repo.owner, repo.name, item_slug)
        if not image:
            continue
        source_author = "unknown"
        author_match = re.search(r"来源\s+\[([^\]]+)\]\(([^)]+)\)|作者\s*[:：]\s*([^\n]+)", block)
        if author_match:
            source_author = clean_text(author_match.group(1) or author_match.group(3) or "unknown")
        source_file = str(path.relative_to(repo_path))
        rows.append(
            {
                "id": f"import-{slug(repo.owner)}-{slug(repo.name)}-{slug(source_file)}-{len(rows) + 1}",
                "title": title,
                "model": model_for(repo.name, title, prompt),
                "category": category_for(title, prompt),
                "style": category_for(title, prompt),
                "useCase": category_for(title, prompt),
                "source": source_author if source_author != "unknown" else repo.name,
                "sourceUrl": f"{repo.url}/blob/main/{source_file}",
                "sourceRepo": f"{repo.owner}/{repo.name}",
                "sourceFile": source_file,
                "image": image,
                "prompt": prompt,
                "language": "mixed",
                "license": "check source repository",
            }
        )
        if len(rows) >= MAX_ITEMS_PER_REPO:
            break
    return rows


def parse_json_file(path: Path, repo_path: Path, repo: Repo) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return []
    candidates: list[dict] = []
    if isinstance(data, list):
        candidates = [row for row in data if isinstance(row, dict)]
    elif isinstance(data, dict):
        for key in ["prompts", "items", "data", "examples", "cases"]:
            value = data.get(key)
            if isinstance(value, list):
                candidates = [row for row in value if isinstance(row, dict)]
                break
    rows: list[dict] = []
    for item in candidates:
        prompt = item.get("prompt") or item.get("content") or item.get("text")
        image_src = item.get("image") or item.get("imageUrl") or item.get("image_url") or item.get("thumbnail")
        if not isinstance(prompt, str) or len(prompt.strip()) < 24 or not isinstance(image_src, str):
            continue
        title = clean_text(str(item.get("title") or item.get("name") or f"{repo.name} prompt {len(rows) + 1}"))
        item_slug = slug(f"{path.stem}-{len(rows) + 1}-{title}")
        image = resolve_image(repo_path, image_src, repo.owner, repo.name, item_slug)
        if not image:
            continue
        source_file = str(path.relative_to(repo_path))
        rows.append(
            {
                "id": f"import-{slug(repo.owner)}-{slug(repo.name)}-{slug(source_file)}-{len(rows) + 1}",
                "title": title,
                "model": model_for(repo.name, title, prompt),
                "category": category_for(title, prompt),
                "style": category_for(title, prompt),
                "useCase": category_for(title, prompt),
                "source": clean_text(str(item.get("author") or repo.name)),
                "sourceUrl": str(item.get("url") or f"{repo.url}/blob/main/{source_file}"),
                "sourceRepo": f"{repo.owner}/{repo.name}",
                "sourceFile": source_file,
                "image": image,
                "prompt": prompt.strip(),
                "language": "mixed",
                "license": "check source repository",
            }
        )
        if len(rows) >= MAX_ITEMS_PER_REPO:
            break
    return rows


def parse_repo(repo_path: Path, repo: Repo) -> list[dict]:
    rows: list[dict] = []
    files = [
        p
        for p in repo_path.rglob("*")
        if p.is_file()
        and p.suffix.lower() in TEXT_SUFFIXES
        and ".git" not in p.parts
        and "node_modules" not in p.parts
        and p.stat().st_size < 2_000_000
    ]
    priority = sorted(files, key=lambda p: (0 if p.name.lower().startswith("readme") else 1, len(p.parts), str(p)))
    for path in priority:
        if len(rows) >= MAX_ITEMS_PER_REPO:
            break
        if path.suffix.lower() in {".md", ".mdx"}:
            rows.extend(parse_markdown_file(path, repo_path, repo))
        elif path.suffix.lower() == ".json":
            rows.extend(parse_json_file(path, repo_path, repo))
    deduped: list[dict] = []
    seen = set()
    for row in rows:
        key = (row["prompt"][:180], row["image"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
        if len(deduped) >= MAX_ITEMS_PER_REPO:
            break
    return deduped


def merge_into_prompts(imported: list[dict]) -> None:
    payload = json.loads(PROMPTS_DATA.read_text(encoding="utf-8"))
    existing = payload.get("prompts", [])
    existing_by_id = {item["id"]: item for item in existing}
    for item in imported:
        existing_by_id[item["id"]] = item
    merged = list(existing_by_id.values())
    payload["prompts"] = merged
    payload.setdefault("meta", {})["count"] = len(merged)
    payload["meta"]["importedCount"] = len(imported)
    PROMPTS_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    repos: list[Repo] = []
    for owner in OWNERS:
        repos.extend(list_repos(owner))
    imported: list[dict] = []
    summary = []
    for repo in repos:
        repo_path = clone_or_update(repo)
        if not repo_path.exists():
            summary.append({"repo": f"{repo.owner}/{repo.name}", "items": 0, "error": "clone failed"})
            continue
        rows = parse_repo(repo_path, repo)
        imported.extend(rows)
        summary.append({"repo": f"{repo.owner}/{repo.name}", "items": len(rows), "url": repo.url})
        print(f"{repo.owner}/{repo.name}: {len(rows)} items")
    IMPORTED_DATA.parent.mkdir(parents=True, exist_ok=True)
    IMPORTED_DATA.write_text(
        json.dumps({"meta": {"count": len(imported), "repos": summary}, "prompts": imported}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    merge_into_prompts(imported)
    print(f"Imported {len(imported)} prompt/image pairs from {len(repos)} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
