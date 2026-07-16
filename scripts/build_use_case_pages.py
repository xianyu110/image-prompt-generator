#!/usr/bin/env python3
import json
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://image-prompt-generator.com"
RAW_ASSET_BASE = "https://raw.githubusercontent.com/xianyu110/image-prompt-generator/main/"
MIN_PROMPTS_PER_PAGE = 12
MIN_IMAGES_PER_PAGE = 6


USE_CASE_PAGES = [
    {
        "slug": "portrait-prompts",
        "label": "Portrait",
        "title": "Portrait Prompts | Image Prompt Generator",
        "description": "Browse portrait prompts for AI headshots, cinematic character images, editorial fashion portraits, avatars, and profile visuals.",
        "h1": "Portrait Prompts",
        "intro": "Portrait prompts for creators who need expressive faces, controlled lighting, strong composition, and model-ready details for headshots, avatars, fashion portraits, and character images.",
        "matches": ["Portrait", "Profile / Avatar"],
        "tips": [
            "Specify age range, expression, pose, lens, lighting, and background before style terms.",
            "Keep identity, clothing, and mood constraints clear so the face stays consistent.",
            "Use aspect ratios such as 1:1, 4:5, or 9:16 depending on avatar, poster, or social output.",
        ],
    },
    {
        "slug": "product-marketing-prompts",
        "label": "Product Marketing",
        "title": "Product Marketing Prompts | Image Prompt Generator",
        "description": "Copy product marketing prompts for ecommerce visuals, hero images, ad creatives, packaging concepts, and commercial AI product shots.",
        "h1": "Product Marketing Prompts",
        "intro": "Product marketing prompts for ecommerce images, launch visuals, ad creatives, packaging concepts, and polished commercial scenes that make a product easy to understand at a glance.",
        "matches": ["Product Marketing", "Product", "Ecommerce Main Image"],
        "tips": [
            "Name the product, material, audience, scene, and commercial goal first.",
            "Add lighting, camera angle, surface, reflections, packaging, and background constraints.",
            "Keep text instructions short and define exact label or headline placement when needed.",
        ],
    },
    {
        "slug": "infographic-prompts",
        "label": "Infographic",
        "title": "Infographic Prompts | Image Prompt Generator",
        "description": "Explore infographic prompts for educational visuals, diagrams, charts, explainers, structured layouts, and visual knowledge cards.",
        "h1": "Infographic Prompts",
        "intro": "Infographic prompts for structured information design, educational cards, diagrams, comparison layouts, flowcharts, and AI visuals that need readable hierarchy.",
        "matches": ["Infographic", "Infographic / Education"],
        "tips": [
            "Break the visual into title, sections, labels, chart type, icons, and hierarchy.",
            "Use simple text and ask for clean spacing when the image includes typography.",
            "Define the audience and the takeaway so the layout prioritizes the right information.",
        ],
    },
    {
        "slug": "game-asset-prompts",
        "label": "Game Asset",
        "title": "Game Asset Prompts | Image Prompt Generator",
        "description": "Find game asset prompts for characters, props, icons, environments, collectible items, UI elements, and concept art.",
        "h1": "Game Asset Prompts",
        "intro": "Game asset prompts for character sheets, props, icons, environments, collectible items, UI elements, and production-ready concept art directions.",
        "matches": ["Game Asset"],
        "tips": [
            "State the asset type, game genre, perspective, material, and usage context.",
            "Ask for clean silhouettes when the output must work as an icon or inventory item.",
            "Include style guide constraints such as palette, outline weight, render style, and background.",
        ],
    },
    {
        "slug": "comic-storyboard-prompts",
        "label": "Comic / Storyboard",
        "title": "Comic Storyboard Prompts | Image Prompt Generator",
        "description": "Browse comic and storyboard prompts for panels, story beats, cinematic scenes, manga pages, and sequential AI image concepts.",
        "h1": "Comic Storyboard Prompts",
        "intro": "Comic and storyboard prompts for sequential scenes, cinematic panels, manga-inspired layouts, character beats, and visual storytelling drafts.",
        "matches": ["Comic / Storyboard"],
        "tips": [
            "Define the scene beat, character action, emotion, camera angle, and panel composition.",
            "Use continuity notes for character clothing, props, and setting across panels.",
            "Keep dialogue short or use empty speech bubbles when text rendering is unreliable.",
        ],
    },
    {
        "slug": "social-media-post-prompts",
        "label": "Social Media Post",
        "title": "Social Media Post Prompts | Image Prompt Generator",
        "description": "Use social media post prompts for scroll-stopping visuals, creator graphics, launch posts, meme concepts, and thumbnail-friendly AI images.",
        "h1": "Social Media Post Prompts",
        "intro": "Social media post prompts for fast-readable visuals, creator posts, launch graphics, trend-aware hooks, meme concepts, and images that still work at thumbnail size.",
        "matches": ["Social Media Post"],
        "tips": [
            "Start with the one-second hook before adding details.",
            "Use high contrast, simple composition, and a single clear visual idea.",
            "Avoid cluttered text; if text is needed, specify one short phrase and exact placement.",
        ],
    },
    {
        "slug": "poster-flyer-prompts",
        "label": "Poster / Flyer",
        "title": "Poster Flyer Prompts | Image Prompt Generator",
        "description": "Copy poster and flyer prompts for events, film posters, campaign graphics, typography layouts, and promotional AI designs.",
        "h1": "Poster Flyer Prompts",
        "intro": "Poster and flyer prompts for event graphics, film posters, campaign layouts, promotional designs, and image concepts with strong hierarchy.",
        "matches": ["Poster / Flyer", "Poster"],
        "tips": [
            "Define the event, audience, layout structure, visual hierarchy, and typography mood.",
            "Specify where the title, subtitle, date, and call to action should appear.",
            "Use a limited palette and clear focal point so the poster remains readable.",
        ],
    },
    {
        "slug": "youtube-thumbnail-prompts",
        "label": "YouTube Thumbnail",
        "title": "YouTube Thumbnail Prompts | Image Prompt Generator",
        "description": "Browse YouTube thumbnail prompts for bold facial reactions, visual hooks, creator concepts, and clickable video covers.",
        "h1": "YouTube Thumbnail Prompts",
        "intro": "YouTube thumbnail prompts for bold hooks, readable compositions, creator concepts, facial reactions, and video covers designed for quick scanning.",
        "matches": ["YouTube Thumbnail"],
        "tips": [
            "Use one subject, one emotion, and one visual contrast rather than many small details.",
            "Leave negative space for a short title if the thumbnail needs text.",
            "Specify 16:9 composition, high contrast, sharp focus, and strong foreground/background separation.",
        ],
    },
    {
        "slug": "app-web-design-prompts",
        "label": "App / Web Design",
        "title": "App Web Design Prompts | Image Prompt Generator",
        "description": "Explore app and web design prompts for landing pages, UI concepts, dashboards, mobile screens, and visual product prototypes.",
        "h1": "App Web Design Prompts",
        "intro": "App and web design prompts for landing pages, UI concepts, dashboards, mobile screens, product prototypes, and structured visual interface directions.",
        "matches": ["App / Web Design"],
        "tips": [
            "State the product type, core workflow, layout density, component set, and visual tone.",
            "Use explicit sections such as navigation, hero, cards, forms, tables, and empty states.",
            "Ask for realistic UI hierarchy instead of purely decorative mockups.",
        ],
    },
    {
        "slug": "video-prompts",
        "label": "Video",
        "title": "Video Prompts | Image Prompt Generator",
        "description": "Find video prompts for AI keyframes, motion scenes, camera direction, short film concepts, and storyboard-ready image prompts.",
        "h1": "Video Prompts",
        "intro": "Video prompts for AI keyframes, motion scenes, camera direction, short film ideas, and storyboard-ready prompts that describe action over time.",
        "matches": ["Video"],
        "tips": [
            "Write the strongest keyframe, then add motion direction and camera language.",
            "Specify duration, shot count, subject continuity, lens movement, and action beats.",
            "Use 9:16 for vertical social video and 16:9 for cinematic or desktop scenes.",
        ],
    },
    {
        "slug": "3d-prompts",
        "label": "3D",
        "title": "3D Prompts | Image Prompt Generator",
        "description": "Browse 3D prompts for isometric icons, clay renders, product sculptures, stylized objects, and dimensional AI image concepts.",
        "h1": "3D Prompts",
        "intro": "3D prompts for isometric icons, clay renders, product sculptures, stylized objects, dimensional UI assets, and tactile visual concepts.",
        "matches": ["3D"],
        "tips": [
            "Define material, lighting, perspective, scale, and background surface.",
            "Use terms such as isometric, clay render, miniature diorama, or studio product render when relevant.",
            "Ask for a clean silhouette when the output will be used as an icon or asset.",
        ],
    },
    {
        "slug": "creative-prompts",
        "label": "Creative",
        "title": "Creative Image Prompts | Image Prompt Generator",
        "description": "Discover creative image prompts for surreal visuals, experimental concepts, stylized scenes, and unusual AI image ideas.",
        "h1": "Creative Image Prompts",
        "intro": "Creative image prompts for surreal visuals, experimental concepts, stylized scenes, unusual combinations, and idea-first AI images.",
        "matches": ["Creative"],
        "tips": [
            "Anchor the prompt with one clear subject before adding surreal or experimental details.",
            "Use contrast between familiar objects and unexpected setting, material, or scale.",
            "Keep the composition understandable even when the concept is unusual.",
        ],
    },
]


MODEL_PAGES = [
    ("GPT Image 2 Prompts", "gpt-image-2-prompts"),
    ("Seedream 5 Pro Prompts", "seedream-5-pro-prompts"),
    ("Seedance 2.0 Prompts", "seedance-2-prompts"),
    ("Grok Imagine Prompts", "grok-imagine-prompts"),
    ("Gemini 3 Pro Prompts", "gemini-3-pro-prompts"),
]


def load_prompts():
    data = json.loads((ROOT / "data" / "prompts.json").read_text())
    return data.get("prompts", [])


def safe(value):
    return escape(str(value or ""), quote=True)


def prompt_excerpt(value, limit=340):
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def match_text(item):
    fields = [
        item.get("category"),
        item.get("style"),
        item.get("useCase"),
    ]
    return " ".join(str(value or "") for value in fields).lower()


def page_prompts(prompts, page):
    matches = {match.lower() for match in page["matches"]}
    selected = []
    seen = set()
    for item in prompts:
        values = {
            str(item.get("category") or "").lower(),
            str(item.get("style") or "").lower(),
            str(item.get("useCase") or "").lower(),
        }
        if not values.intersection(matches):
            continue
        item_id = item.get("id")
        if item_id in seen:
            continue
        seen.add(item_id)
        selected.append(item)
    selected.sort(
        key=lambda item: (
            not bool(published_image_path(item)),
            not str(item.get("image") or "").startswith("assets/thumbs/"),
            item.get("model") or "",
            item.get("id") or "",
        )
    )
    return selected[:24]


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


def related_use_case_links(active_slug, generated_pages):
    links = []
    for page in generated_pages:
        if page["slug"] == active_slug:
            continue
        links.append(f'<a class="model-link" href="../{safe(page["slug"])}/">{safe(page["h1"])}</a>')
    return "\n".join(links[:8])


def related_model_links():
    return "\n".join(
        f'<a class="model-link" href="../{safe(slug)}/">{safe(label)}</a>'
        for label, slug in MODEL_PAGES
    )


def faq_html(page):
    label = page["label"].lower()
    faqs = [
        (
            f"What makes a good {page['label']} prompt?",
            f"A good {page['label']} prompt names the subject, use case, visual style, composition, model constraints, and output goal clearly.",
        ),
        (
            f"Which image model should I use for {label} prompts?",
            "Start with the model examples on each card. GPT Image is useful for polished image generation, Seedream is useful for controlled design output, Gemini can handle structured visual instructions, and Seedance-style prompts help when motion or keyframes matter.",
        ),
        (
            "Can I copy these prompts commercially?",
            "Check the source link and license context for each prompt before commercial use. Treat attributed social posts as references unless the source clearly allows reuse.",
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
      const fallbackCopy = (text) => {
        if (!text) return false;
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.top = "0";
        textarea.style.left = "0";
        textarea.style.width = "1px";
        textarea.style.height = "1px";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        let copied = false;
        try {
          copied = document.execCommand("copy");
        } finally {
          textarea.remove();
        }
        return copied;
      };

      const copyText = async (text) => {
        if (!text) return false;
        if (fallbackCopy(text)) return true;
        if (navigator.clipboard && window.isSecureContext) {
          try {
            await navigator.clipboard.writeText(text);
            return true;
          } catch {
            return false;
          }
        }
        return false;
      };

      const showManualCopy = (text) => {
        let panel = document.querySelector("[data-manual-copy-panel]");
        if (!panel) {
          panel = document.createElement("div");
          panel.setAttribute("data-manual-copy-panel", "");
          panel.style.position = "fixed";
          panel.style.left = "50%";
          panel.style.bottom = "18px";
          panel.style.transform = "translateX(-50%)";
          panel.style.zIndex = "1000";
          panel.style.width = "min(720px, calc(100vw - 28px))";
          panel.style.padding = "12px";
          panel.style.border = "4px solid #000";
          panel.style.background = "#fff";
          panel.style.boxShadow = "6px 6px 0 #000";
          panel.innerHTML = '<strong style="display:block;margin-bottom:8px">Copy prompt manually</strong><textarea rows="5" readonly style="width:100%;border:3px solid #000;padding:10px;font:inherit"></textarea>';
          document.body.appendChild(panel);
        }
        const textarea = panel.querySelector("textarea");
        textarea.value = text;
        textarea.focus();
        textarea.select();
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
          const copied = await copyText(prompt);
          if (copied) {
            button.textContent = "Copied";
          } else {
            showManualCopy(prompt);
            button.textContent = "Select prompt";
          }
        } catch {
          showManualCopy(prompt);
          button.textContent = "Select prompt";
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
            "name": f"{page['label']} prompt examples",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "name": item.get("title") or f"{page['label']} prompt",
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
                    "name": f"What makes a good {page['label']} prompt?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"A good {page['label']} prompt names the subject, use case, visual style, composition, model constraints, and output goal clearly.",
                    },
                }
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_page(page, prompts, generated_pages):
    cards = "\n".join(card_html(item) for item in prompts)
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
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1500176085727924"
     crossorigin="anonymous"></script>
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
        <h2>{safe(page["label"])} prompt writing tips</h2>
        <ul>{tips}</ul>
      </div>
      <div>
        <h2>Related model pages</h2>
        <div class="model-link-list">
          {related_model_links()}
        </div>
      </div>
    </section>

    <section class="hot-prompts model-prompts">
      <div class="section-header">
        <h2>{safe(page["label"])} prompt examples</h2>
        <span class="outline-button">{len(prompts)} prompt examples</span>
      </div>
      <div class="prompt-grid" data-use-case-prompt-grid>
        {cards}
      </div>
    </section>

    <section class="model-links use-case-related" aria-label="Related image prompt use cases">
      <div class="section-header">
        <h2>Related prompt use cases</h2>
        <a class="outline-button" href="../#use-cases">Explore</a>
      </div>
      <div class="model-link-grid use-case-link-grid">
        {related_use_case_links(page["slug"], generated_pages)}
      </div>
    </section>

    <section class="faq">
      <h2>{safe(page["label"])} prompt FAQ</h2>
      <div class="faq-grid">
        {faq_html(page)}
      </div>
    </section>
  </main>

  <footer class="footer">
    <p>Image Prompt Generator · AI image and video prompts with images, authors, and source links.</p>
    <nav class="footer-links" aria-label="Site information">
      <a href="../">Home</a>
      <a href="../about/">About</a>
      <a href="../privacy-policy/">Privacy</a>
      <a href="../contact/">Contact</a>
      <a href="../terms/">Terms</a>
    </nav>
  </footer>
{copy_prompts_script()}
</body>
</html>
"""


def clean_html(value):
    return "\n".join(line.rstrip() for line in value.splitlines()) + "\n"


def load_existing_sitemap_urls():
    urls = []
    sitemap = ROOT / "pages-sitemap.xml"
    if not sitemap.exists():
        return urls
    text = sitemap.read_text()
    for loc in re.findall(r"<loc>(.*?)</loc>", text):
        if loc not in urls:
            urls.append(loc)
    return urls


def write_sitemap(generated_pages):
    urls = load_existing_sitemap_urls()
    for page in generated_pages:
        url = f"{SITE_URL}/{page['slug']}/"
        if url not in urls:
            urls.append(url)
    body = "\n".join(f"""  <url>
    <loc>{safe(loc)}</loc>
    <priority>{'0.75' if loc.count('/') > 3 else '0.8'}</priority>
  </url>""" for loc in urls)
    (ROOT / "pages-sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
""")


def page_has_enough_value(prompts):
    image_count = sum(1 for item in prompts if published_image_path(item))
    return len(prompts) >= MIN_PROMPTS_PER_PAGE and image_count >= MIN_IMAGES_PER_PAGE


def main():
    prompts = load_prompts()
    selected = {}
    generated_pages = []
    skipped = []
    for page in USE_CASE_PAGES:
        page_selected = page_prompts(prompts, page)
        selected[page["slug"]] = page_selected
        if page_has_enough_value(page_selected):
            generated_pages.append(page)
        else:
            skipped.append((page["slug"], len(page_selected), sum(1 for item in page_selected if published_image_path(item))))

    for page in generated_pages:
        page_dir = ROOT / page["slug"]
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(clean_html(render_page(page, selected[page["slug"]], generated_pages)))
        print(f"wrote {page['slug']}/index.html with {len(selected[page['slug']])} prompts")

    write_sitemap(generated_pages)
    print(f"updated pages-sitemap.xml with {len(generated_pages)} use-case pages")
    for slug, prompt_count, image_count in skipped:
        print(f"skipped {slug}: {prompt_count} prompts, {image_count} images")


if __name__ == "__main__":
    main()
