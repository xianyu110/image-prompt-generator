#!/usr/bin/env python3
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://image-prompt-generator.com"
RAW_ASSET_BASE = "https://raw.githubusercontent.com/xianyu110/image-prompt-generator/main/"


MODEL_PAGES = [
    {
        "model": "GPT Image 2",
        "slug": "gpt-image-2-prompts",
        "title": "GPT Image 2 Prompts | Image Prompt Generator",
        "description": "Browse GPT Image 2 prompts for portraits, posters, product visuals, text rendering, and cinematic AI image generation.",
        "h1": "GPT Image 2 Prompts",
        "intro": "A focused collection of GPT Image 2 prompts for realistic portraits, editorial images, poster concepts, readable text, and polished image generation workflows.",
        "tips": [
            "Describe the subject and scene before adding style terms.",
            "Keep any text short and specify where it appears in the image.",
            "Use composition words such as foreground, midground, background, lens, lighting, and negative space.",
        ],
    },
    {
        "model": "Seedream 5 Pro",
        "aliases": ["Seedream 5 Pro", "Seedream"],
        "slug": "seedream-5-pro-prompts",
        "title": "Seedream 5 Pro Prompts | Image Prompt Generator",
        "description": "Explore Seedream 5 Pro prompts for controllable editing, Chinese text, product design, commercial images, and local refinements.",
        "h1": "Seedream 5 Pro Prompts",
        "intro": "Seedream 5 Pro prompt examples for controllable edits, commercial design output, readable typography, local refinements, and iteration-friendly image workflows.",
        "dataFile": "../data/prompts/seedream-5-pro.json",
        "tips": [
            "State what should stay unchanged before describing the edit.",
            "Separate layout, typography, material, and lighting instructions.",
            "Use short readable copy when asking for text inside the image.",
        ],
    },
    {
        "model": "Seedance 2.0",
        "slug": "seedance-2-prompts",
        "title": "Seedance 2.0 Prompts | Image Prompt Generator",
        "description": "Use Seedance 2.0 prompts for image keyframes, video storyboards, motion direction, camera language, and cinematic scenes.",
        "h1": "Seedance 2.0 Prompts",
        "intro": "Seedance 2.0 prompt templates that treat images as video keyframes, with motion direction, action beats, camera language, and storyboard-ready composition.",
        "tips": [
            "Write a still image as the strongest keyframe from a short video.",
            "Specify subject identity, action moment, camera movement, and motion direction.",
            "For video, expand one image prompt into 3-5 clear shots.",
        ],
    },
    {
        "model": "Grok Imagine",
        "slug": "grok-imagine-prompts",
        "title": "Grok Imagine Prompts | Image Prompt Generator",
        "description": "Find Grok Imagine prompts for social hooks, trend-aware concepts, bold visual metaphors, and fast-readable AI images.",
        "h1": "Grok Imagine Prompts",
        "intro": "Grok Imagine prompt ideas for bold social visuals, trend-aware concepts, meme-like image hooks, and high-contrast compositions that are easy to understand quickly.",
        "tips": [
            "Start with the one-second visual hook before adding details.",
            "Use strong contrast, expressive subjects, and clear visual metaphors.",
            "Avoid cluttered text and keep the image readable at thumbnail size.",
        ],
    },
    {
        "model": "Gemini 3 Pro",
        "slug": "gemini-3-pro-prompts",
        "title": "Gemini 3 Pro Prompts | Image Prompt Generator",
        "description": "Browse Gemini 3 Pro prompts for structured visual instructions, multimodal reasoning, diagrams, layouts, and long-context image generation.",
        "h1": "Gemini 3 Pro Prompts",
        "intro": "Gemini 3 Pro prompt examples for structured image generation, visual reasoning, information layouts, diagrams, and complex instructions with clear constraints.",
        "tips": [
            "Use fields for subject, layout, hierarchy, style, palette, and constraints.",
            "Make information structure explicit when generating diagrams or UI-like visuals.",
            "List what to avoid so details stay consistent across the image.",
        ],
    },
]


def load_prompts():
    data = json.loads((ROOT / "data" / "prompts.json").read_text())
    prompts = data.get("prompts", [])
    built_in = [
        {
            "id": "model-template-seedance-keyframe",
            "title": "Seedance image keyframe prompt",
            "model": "Seedance 2.0",
            "category": "Video / Keyframe",
            "source": "Image Prompt Generator",
            "sourceUrl": "https://github.com/xianyu110/image-prompt-generator",
            "image": "",
            "prompt": "Create a cinematic keyframe as if it were the strongest still from a short video: [subject] moving through [scene], clear motion direction, consistent character identity, dynamic lens perspective, natural motion blur, realistic lighting, high-resolution details, no watermark.",
        },
        {
            "id": "model-template-grok-social",
            "title": "Grok Imagine social hook prompt",
            "model": "Grok Imagine",
            "category": "Social Creative",
            "source": "Image Prompt Generator",
            "sourceUrl": "https://github.com/xianyu110/image-prompt-generator",
            "image": "",
            "prompt": "Generate a bold social-first image about [topic]: instantly readable visual metaphor, strong contrast, expressive subject, sharp meme-like composition without text clutter, cinematic lighting, high detail, designed to be understood in one second.",
        },
        {
            "id": "model-template-gemini-structured",
            "title": "Gemini structured visual prompt",
            "model": "Gemini 3 Pro",
            "category": "Structured Prompt",
            "source": "Image Prompt Generator",
            "sourceUrl": "https://github.com/xianyu110/image-prompt-generator",
            "image": "",
            "prompt": "Create a highly structured image following these constraints: subject [subject], scene [scene], composition [layout], visual hierarchy [priority], style [style], color palette [palette], readable text only if necessary, consistent details across all objects, no extra limbs, no watermark.",
        },
    ]
    return prompts + built_in


def safe(value):
    return escape(str(value or ""), quote=True)


def prompt_excerpt(value, limit=340):
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def author_label(item):
    source = item.get("source") or "Image Prompt Generator"
    if source == "Image Prompt Generator" or "@" in source:
        return source
    return source if source.startswith("@") else f"@{source}"


def published_image_path(item):
    image = item.get("image") or ""
    if not image.startswith(("assets/thumbs/", "assets/imported/")):
        return ""
    if image.startswith("assets/thumbs/"):
        stem = Path(image).stem
        optimized = f"assets/thumbs-optimized/{stem}.webp"
        if (ROOT / optimized).is_file():
            return optimized
    if not (ROOT / image).is_file():
        return ""
    return image


def image_url(image, prefix="../"):
    if image.startswith("assets/imported/"):
        return RAW_ASSET_BASE + image
    return prefix + image


def image_html(item, prefix="../"):
    image = published_image_path(item)
    if image:
        return f'<div class="card-image"><img src="{safe(image_url(image, prefix))}" alt="{safe(item.get("title"))}" loading="lazy"></div>'
    return f'<div class="card-image"><div class="image-fallback">{safe(item.get("model"))}<br>{safe(item.get("category"))}</div></div>'


def card_html(item):
    return f"""
        <article class="prompt-card" data-prompt-id="{safe(item.get("id"))}" data-prompt-text="{safe(item.get("prompt"))}">
          <div class="card-top">
            <span class="author">Author {safe(author_label(item))}</span>
            <span class="date">{safe(item.get("model"))}</span>
          </div>
          {image_html(item)}
          <div class="prompt-preview">
            <div class="preview-bar">Prompt example</div>
            <p>{safe(prompt_excerpt(item.get("prompt")))}</p>
          </div>
          <div class="tag-row">
            <span class="tag model">{safe(item.get("model"))}</span>
            <span class="tag">{safe(item.get("category"))}</span>
          </div>
          <div class="card-actions model-card-actions">
            <a class="try-button" href="{safe(item.get("sourceUrl") or "../")}" target="_blank" rel="noreferrer">View source</a>
            <button class="copy-prompt-button" type="button" data-copy-prompt>Copy prompt</button>
          </div>
        </article>
    """


def page_prompts(all_prompts, page):
    aliases = set(page.get("aliases") or [page["model"]])
    selected = [item for item in all_prompts if item.get("model") in aliases]
    selected.sort(key=lambda item: (not bool(item.get("image")), item.get("id") or ""))
    return selected[:12]


def related_links(active_slug):
    links = []
    for page in MODEL_PAGES:
        if page["slug"] == active_slug:
            continue
        links.append(f'<a class="model-link" href="../{safe(page["slug"])}/">{safe(page["h1"])}</a>')
    return "\n".join(links)


def faq_html(page):
    model = page["model"]
    faqs = [
        (
            f"What makes a good {model} prompt?",
            f"A good {model} prompt names the subject, scene, composition, style, constraints, and quality requirements in clear language.",
        ),
        (
            f"Can I copy these {model} prompts?",
            "Yes. Use them as examples, keep attribution when a source is provided, and adapt the subject, brand, scene, or text to your project.",
        ),
        (
            f"How should I adapt a prompt for {model}?",
            "Keep the core structure, then replace the subject, scene, aspect ratio, style, and text rules with your own requirements.",
        ),
    ]
    return "\n".join(f"""
        <details>
          <summary>{safe(q)}</summary>
          <p>{safe(a)}</p>
        </details>
    """ for q, a in faqs)


def copy_prompts_script():
    return """
  <script>
    (() => {
      const copyText = async (text) => {
        if (!text) return false;
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text);
          return true;
        }
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.top = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        const copied = document.execCommand("copy");
        textarea.remove();
        return copied;
      };

      document.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-copy-prompt]");
        if (!button) return;
        event.preventDefault();
        event.stopPropagation();

        const card = button.closest("[data-prompt-text]");
        const prompt = card ? card.dataset.promptText : "";
        const label = button.dataset.label || button.textContent || "Copy prompt";
        button.dataset.label = label;
        button.disabled = true;

        try {
          button.textContent = await copyText(prompt) ? "Copied" : "Copy failed";
        } catch {
          button.textContent = "Copy failed";
        } finally {
          window.setTimeout(() => {
            button.textContent = button.dataset.label || "Copy prompt";
            button.disabled = false;
          }, 1600);
        }
      });
    })();
  </script>
"""


def dynamic_prompts_script(page):
    data_file = page.get("dataFile")
    if not data_file:
        return ""
    return f"""
  <script>
    (() => {{
      const grid = document.querySelector("[data-model-prompt-grid]");
      const status = document.querySelector("[data-model-prompt-status]");
      const initialIds = new Set(
        Array.from(document.querySelectorAll("[data-prompt-id]")).map((card) => card.dataset.promptId)
      );
      const escapeHtml = (value) => String(value || "").replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\\"": "&quot;",
        "'": "&#39;",
      }}[char]));
      const excerpt = (value) => {{
        const text = String(value || "").replace(/\\s+/g, " ").trim();
        return text.length > 340 ? `${{text.slice(0, 340).trim()}}...` : text;
      }};
      const imageUrl = (image) => {{
        if (!image) return "";
        if (image.startsWith("assets/imported/")) {{
          return "https://raw.githubusercontent.com/xianyu110/image-prompt-generator/main/" + image;
        }}
        if (image.startsWith("assets/")) return "../" + image;
        return image;
      }};
      const authorLabel = (source) => {{
        if (!source) return "Image Prompt Generator";
        if (source === "Image Prompt Generator" || source.includes("@")) return source;
        return source.startsWith("@") ? source : `@${{source}}`;
      }};
      const cardHtml = (item) => {{
        const image = imageUrl(item.image);
        const imageMarkup = image
          ? `<div class="card-image"><img src="${{escapeHtml(image)}}" alt="${{escapeHtml(item.title)}}" loading="lazy"></div>`
          : `<div class="card-image"><div class="image-fallback">${{escapeHtml(item.model)}}<br>${{escapeHtml(item.category)}}</div></div>`;
        return `
        <article class="prompt-card" data-prompt-id="${{escapeHtml(item.id)}}" data-prompt-text="${{escapeHtml(item.prompt)}}">
          <div class="card-top">
            <span class="author">Author ${{escapeHtml(authorLabel(item.source))}}</span>
            <span class="date">${{escapeHtml(item.model)}}</span>
          </div>
          ${{imageMarkup}}
          <div class="prompt-preview">
            <div class="preview-bar">Prompt example</div>
            <p>${{escapeHtml(excerpt(item.prompt))}}</p>
          </div>
          <div class="tag-row">
            <span class="tag model">${{escapeHtml(item.model)}}</span>
            <span class="tag">${{escapeHtml(item.category)}}</span>
          </div>
          <div class="card-actions model-card-actions">
            <a class="try-button" href="${{escapeHtml(item.sourceUrl || "../")}}" target="_blank" rel="noreferrer">View source</a>
            <button class="copy-prompt-button" type="button" data-copy-prompt>Copy prompt</button>
          </div>
        </article>`;
      }};

      fetch("{safe(data_file)}")
        .then((response) => response.ok ? response.json() : Promise.reject(new Error("Prompt data failed to load")))
        .then((data) => {{
          const prompts = (data.prompts || []).filter((item) => !initialIds.has(item.id));
          grid.insertAdjacentHTML("beforeend", prompts.map(cardHtml).join(""));
          if (status) status.textContent = `${{data.count || prompts.length + initialIds.size}} prompt examples`;
        }})
        .catch(() => {{
          if (status) status.textContent = "Prompt data failed to load.";
        }});
    }})();
  </script>
"""


def page_json_ld(page, prompts):
    url = f"{SITE_URL}/{page['slug']}/"
    data = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": page["h1"],
            "url": url,
            "description": page["description"],
            "isPartOf": {
                "@type": "WebSite",
                "name": "Image Prompt Generator",
                "url": SITE_URL + "/",
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{page['model']} prompt examples",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "name": item.get("title") or f"{page['model']} prompt",
                    "description": prompt_excerpt(item.get("prompt"), 180),
                }
                for index, item in enumerate(prompts[:10])
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"What makes a good {page['model']} prompt?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"A good {page['model']} prompt names the subject, scene, composition, style, constraints, and quality requirements in clear language.",
                    },
                }
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_page(page, prompts):
    cards = "\n".join(card_html(item) for item in prompts)
    section_action = (
        f'<span class="outline-button" data-model-prompt-status>{len(prompts)} prompt examples</span>'
        if page.get("dataFile")
        else '<a class="outline-button" href="../#generator">Generate</a>'
    )
    empty_note = "" if cards else f"""
        <article class="prompt-card">
          <div class="prompt-preview">
            <div class="preview-bar">Prompt examples coming soon</div>
            <p>We are curating more high-quality {safe(page["model"])} prompt examples. Use the writing tips above and open the generator to draft a model-aware prompt now.</p>
          </div>
        </article>
    """
    tips = "\n".join(f"<li>{safe(tip)}</li>" for tip in page["tips"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe(page["title"])}</title>
  <meta name="description" content="{safe(page["description"])}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{SITE_URL}/{safe(page["slug"])}/">
  <meta property="og:title" content="{safe(page["h1"])}">
  <meta property="og:description" content="{safe(page["description"])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}/{safe(page["slug"])}/">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/svg+xml" href="../assets/site-icon.svg">
  <link rel="apple-touch-icon" href="../assets/site-icon.svg">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-4JVL9RKKMF"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "G-4JVL9RKKMF");
  </script>
  <script type="application/ld+json">
{page_json_ld(page, prompts)}
  </script>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="../#top" aria-label="Image Prompt Generator">
      <img class="brand-mark" src="../assets/site-icon.svg" alt="" aria-hidden="true">
      <span>Image Prompt Generator</span>
    </a>
    <nav class="nav-links" aria-label="Primary navigation">
      <a href="../#generator">Generator</a>
      <a href="../#hot">Trending Prompts</a>
      <a href="../#library">Prompt Library</a>
      <a href="../#faq">FAQ</a>
    </nav>
  </header>

  <main>
    <section class="model-hero">
      <p class="breadcrumb"><a href="../">Home</a> / {safe(page["h1"])}</p>
      <h1>{safe(page["h1"])}</h1>
      <p>{safe(page["intro"])}</p>
      <div class="model-cta-row">
        <a class="model-cta" href="../#generator">Open Image Prompt Generator</a>
        <a class="model-cta secondary" href="../#library">Browse all prompts</a>
      </div>
    </section>

    <section class="model-guide">
      <div>
        <h2>{safe(page["model"])} prompt writing tips</h2>
        <ul>{tips}</ul>
      </div>
      <div>
        <h2>Related model pages</h2>
        <div class="model-link-list">
          {related_links(page["slug"])}
        </div>
      </div>
    </section>

    <section class="hot-prompts model-prompts">
      <div class="section-header">
        <h2>{safe(page["model"])} prompt examples</h2>
        {section_action}
      </div>
      <div class="prompt-grid" data-model-prompt-grid>
        {cards}
        {empty_note}
      </div>
    </section>

    <section class="faq">
      <h2>{safe(page["model"])} prompt FAQ</h2>
      <div class="faq-grid">
        {faq_html(page)}
      </div>
    </section>
  </main>

  <footer class="footer">
    <p>Image Prompt Generator · AI image and video prompts with images, authors, and source links.</p>
    <a href="../">Back to generator</a>
  </footer>
{copy_prompts_script()}
{dynamic_prompts_script(page)}
</body>
</html>
"""


def write_sitemap():
    urls = [
        ("https://image-prompt-generator.com/", "1.0"),
        *[(f"https://image-prompt-generator.com/{page['slug']}/", "0.8") for page in MODEL_PAGES],
    ]
    body = "\n".join(f"""  <url>
    <loc>{loc}</loc>
    <priority>{priority}</priority>
  </url>""" for loc, priority in urls)
    (ROOT / "sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://image-prompt-generator.com/pages-sitemap.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://image-prompt-generator.com/image-sitemap.xml</loc>
  </sitemap>
</sitemapindex>
""")
    (ROOT / "pages-sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
""")


def write_model_page_assets(selected_by_slug):
    assets = sorted({
        image
        for prompts in selected_by_slug.values()
        for prompt in prompts
        for image in [published_image_path(prompt)]
        if image.startswith("assets/imported/")
    })
    (ROOT / "data" / "model-page-assets.json").write_text(
        json.dumps(assets, ensure_ascii=False, indent=2) + "\n"
    )


def clean_html(value):
    return "\n".join(line.rstrip() for line in value.splitlines()) + "\n"


def main():
    prompts = load_prompts()
    selected_by_slug = {}
    for page in MODEL_PAGES:
        page_dir = ROOT / page["slug"]
        page_dir.mkdir(exist_ok=True)
        selected = page_prompts(prompts, page)
        selected_by_slug[page["slug"]] = selected
        (page_dir / "index.html").write_text(clean_html(render_page(page, selected)))
        print(f"wrote {page['slug']}/index.html with {len(selected)} prompts")
    write_model_page_assets(selected_by_slug)
    print("updated data/model-page-assets.json")
    write_sitemap()
    print("updated sitemap.xml")


if __name__ == "__main__":
    main()
