# Image Prompt Generator

GPT Image 2 prompt generator and image prompt gallery.

Site target: <https://image-prompt-generator.com/>

## What is included

- Top prompt composer inspired by prompt-generator workflows.
- Prompt cards with image preview, author/source, model, category, and copy action.
- Imported prompt data from local prompt collections with source attribution.
- Static GitHub Pages deployment, no build step required.

## Local Preview

```bash
python3 -m http.server 8787
```

Then open <http://localhost:8787/>.

## Rebuild Data

```bash
python3 scripts/build_data.py
```

The script reads local source repositories from the parent workspace and writes `data/prompts.json`.
