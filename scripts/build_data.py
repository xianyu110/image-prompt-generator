#!/usr/bin/env python3
"""Build the static prompt dataset from local prompt repositories."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
NANO_MD = WORKSPACE / "awesome-nanobananapro-prompts/gpt4o-image-prompts-master/100.md"
NANO_IMAGES = WORKSPACE / "awesome-nanobananapro-prompts/gpt4o-image-prompts-master/images"
GPT_JSON = WORKSPACE / "awesome-gptimage2/data/latest-prompts.json"
GPT_README = WORKSPACE / "awesome-gptimage2/README.md"
THUMBS = ROOT / "assets/thumbs"
DATA_FILE = ROOT / "data/prompts.json"


CATEGORY_KEYWORDS = [
    ("Product", ["产品", "商品", "品牌", "广告", "包装", "logo", "Logo", "AirBnB", "Airbnb"]),
    ("Poster", ["海报", "字体", "文本", "标志", "typography", "poster"]),
    ("Portrait", ["肖像", "人物", "角色", "portrait", "character", "face"]),
    ("Illustration", ["插图", "手绘", "漫画", "manga", "卡通", "刺绣", "illustration"]),
    ("3D", ["3D", "立体", "微型", "雕塑", "clay", "isometric", "diorama"]),
    ("Infographic", ["信息图", "卡片", "图表", "ASCII", "science", "diagram"]),
    ("Photography", ["写实", "摄影", "photograph", "photorealistic", "cinematic"]),
]


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def category_for(title: str, prompt: str) -> str:
    haystack = f"{title} {prompt}"
    for category, words in CATEGORY_KEYWORDS:
        if any(word in haystack for word in words):
            return category
    return "Creative"


def source_for(heading: str) -> tuple[str, str]:
    match = re.search(r"来源\s+\[([^\]]+)\]\(([^)]+)\)", heading)
    if match:
        return match.group(1), match.group(2)
    return "awesome-nano-banana", "https://github.com/xianyu110/awesome-nano-banana"


def find_case_images(block: str) -> list[str]:
    images = re.findall(r'<img\s+[^>]*src="([^"]+)"', block, flags=re.I)
    return [img.replace("./images/", "") for img in images if img]


def copy_thumb(image_name: str, item_id: str) -> str | None:
    src = NANO_IMAGES / image_name
    if not src.exists() or not src.is_file():
        return None
    suffix = src.suffix.lower() or ".jpg"
    dest = THUMBS / f"{item_id}{suffix}"
    shutil.copy2(src, dest)
    return f"assets/thumbs/{dest.name}"


def download_thumb(url: str | None, item_id: str) -> str | None:
    if not url:
        return None
    suffix = Path(url.split("?", 1)[0]).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    dest = THUMBS / f"{item_id}{suffix}"
    if dest.exists() and dest.stat().st_size > 0:
        return f"assets/thumbs/{dest.name}"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            dest.write_bytes(response.read())
        if dest.stat().st_size > 0:
            return f"assets/thumbs/{dest.name}"
    except (urllib.error.URLError, TimeoutError, OSError):
        pass
    try:
        subprocess.run(
            ["curl", "-k", "-L", "--max-time", "35", "-A", "Mozilla/5.0", "-o", str(dest), url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if dest.exists() and dest.stat().st_size > 0:
            return f"assets/thumbs/{dest.name}"
    except (subprocess.CalledProcessError, OSError):
        pass
    return url


def parse_nano(limit: int = 48) -> list[dict]:
    text = NANO_MD.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r'(?P<anchor><a id="prompt-(?P<num>\d+)"></a>\s*)?'
        r'##\s+案例\s+(?P<num2>\d+)：(?P<title>.+?)\n(?P<body>.*?)(?=\n<a id="prompt-\d+"></a>\n##\s+案例|\Z)',
        re.S,
    )
    items = []
    for match in pattern.finditer(text):
        num = match.group("num") or match.group("num2")
        raw_title = clean_text(match.group("title"))
        title = re.sub(r"\s*\(来源.*$", "", raw_title).strip()
        body = match.group("body")
        prompt_match = re.search(r"\*\*提示词：\*\*\s*```(?:[a-zA-Z]+)?\s*(.*?)```", body, re.S)
        if not prompt_match:
            continue
        prompt = prompt_match.group(1).strip()
        if len(prompt) < 24:
            continue
        item_id = f"nano-{num}"
        images = find_case_images(body)
        thumb = copy_thumb(images[0], item_id) if images else None
        source_name, source_url = source_for(raw_title)
        category = category_for(title, prompt)
        items.append(
            {
                "id": item_id,
                "title": title,
                "model": "Nano Banana Pro",
                "category": category,
                "style": category,
                "useCase": category,
                "source": source_name,
                "sourceUrl": source_url,
                "image": thumb,
                "prompt": prompt,
                "language": "zh/en",
                "license": "MIT source repository",
            }
        )
        if len(items) >= limit:
            break
    return items


def parse_gpt(limit: int = 12) -> list[dict]:
    data = json.loads(GPT_JSON.read_text(encoding="utf-8"))
    readme_images = []
    if GPT_README.exists():
        readme_text = GPT_README.read_text(encoding="utf-8", errors="ignore")
        readme_images = [
            url
            for _, url in re.findall(
                r'(?:src=|!\[[^\]]*\]\()(["\']?)([^"\')\s>]+\.(?:png|jpg|jpeg|webp))(?:\1)',
                readme_text,
                flags=re.I,
            )
            if "upload.maynor1024.live" in url
        ]
    rows = []
    for date_group in data.get("dates", []):
        for item in date_group.get("items", []):
            prompt = (item.get("prompt") or "").strip()
            if len(prompt) < 24 or prompt.startswith("["):
                continue
            title = clean_text(item.get("reason") or "GPT Image 2 prompt")
            item_id = f"gpt-{len(rows) + 1:02d}"
            category = category_for(title, prompt)
            image_url = readme_images[len(rows) % len(readme_images)] if readme_images else item.get("primary_image_url")
            rows.append(
                {
                    "id": item_id,
                    "title": title,
                    "model": "GPT Image 2",
                    "category": category,
                    "style": category,
                    "useCase": category,
                    "source": item.get("author") or "X prompt",
                    "sourceUrl": item.get("x_url") or item.get("url") or "https://github.com/xianyu110/awesome-gptimage2",
                    "image": download_thumb(image_url, item_id),
                    "prompt": prompt,
                    "language": "en",
                    "license": "source attribution required",
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def seedream_examples() -> list[dict]:
    rows = [
        {
            "title": "Seedream product landing page visual",
            "category": "Product",
            "style": "Commercial",
            "prompt": "Create a clean commercial product landing page hero image for [PRODUCT]. Use a premium studio setup, realistic lighting, crisp product edges, tasteful typography space, and a balanced layout suitable for an ecommerce homepage. Keep the product accurate, avoid clutter, and leave enough negative space for headline text.",
        },
        {
            "title": "Seedream information card with Chinese text",
            "category": "Infographic",
            "style": "Editorial",
            "prompt": "Create a vertical Chinese information card about [TOPIC]. Use a clear editorial grid, strong title hierarchy, readable Chinese typography, small supporting illustrations, and concise section labels. Make it suitable for social sharing, with clean margins and high text legibility.",
        },
        {
            "title": "Seedream multi-panel visual explanation",
            "category": "Infographic",
            "style": "Storyboard",
            "prompt": "Create a five-panel visual explanation of [PROCESS]. Each panel should show one step with consistent characters, clean composition, short readable labels, and a coherent color system. The final image should feel like a polished educational storyboard.",
        },
        {
            "title": "Seedream precise image editing brief",
            "category": "Photography",
            "style": "Edit",
            "prompt": "Edit the uploaded image while preserving the main subject, face, pose, and original perspective. Change only [TARGET AREA] into [NEW DETAIL]. Match lighting, shadows, material texture, and camera grain so the edit looks natural and production-ready.",
        },
    ]
    for index, row in enumerate(rows, start=1):
        row.update(
            {
                "id": f"seedream-{index:02d}",
                "model": "Seedream 5 Pro",
                "useCase": row["category"],
                "source": "Image Prompt Generator original",
                "sourceUrl": "https://image-prompt-generator.com/",
                "image": None,
                "language": "en/zh",
                "license": "original site content",
            }
        )
    return rows


def main() -> None:
    THUMBS.mkdir(parents=True, exist_ok=True)
    prompts = parse_nano() + parse_gpt() + seedream_examples()
    payload = {
        "meta": {
            "site": "Image Prompt Generator",
            "domain": "image-prompt-generator.com",
            "generatedFrom": [
                "awesome-nanobananapro-prompts/gpt4o-image-prompts-master/100.md",
                "awesome-gptimage2/data/latest-prompts.json",
                "original Seedream prompt templates",
            ],
            "count": len(prompts),
        },
        "prompts": prompts,
    }
    DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(prompts)} prompts to {DATA_FILE}")


if __name__ == "__main__":
    main()
