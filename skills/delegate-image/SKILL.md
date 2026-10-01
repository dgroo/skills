---
name: delegate-image
description: Generate a visual — SVG via text models (Astra) for logos and diagrams, a raster panel for photos — judged by two independent models. Use for any image ask.
argument-hint: <what the visual should be>
---

# Delegate: visuals — pick the output type, then the panel

Claude can't generate raster images, but it can write SVG, and so can any capable text model. So the first decision is not which model — it's **which kind of file the user actually wants.** Get that wrong and a photorealistic model produces a blurry logo, or a vector model is asked for a sunset.

## 1. Choose the output type

| The ask | Output | Why |
|---|---|---|
| Logo, mark, icon, badge, diagram, chart, schematic, pictogram — anything with flat shapes, text, or that must scale, be edited, or **animate** | **SVG** | Resolution-independent, editable, tiny, animatable with CSS or SMIL, and reviewable as source. The user will want to change a colour or a word later; with a PNG they can't. |
| Photo, scene, person, product shot, texture, illustration with lighting and depth — anything photorealistic or painterly | **Raster** (PNG) | This is what image-generation models are for; no text model can do it. |
| "Animated logo", "loading spinner", "hero animation" | **SVG with animation** | CSS `@keyframes` inside `<style>` (broadest support) or SMIL; the static first frame must stand on its own. |

When in doubt: *if the user would ever want to edit it, it's SVG.* Say which type you chose and why in one line; if the ask genuinely straddles (a logo *and* a photo of it on a mug), do both.

## 2a. SVG panel — text models

```bash
python3 <skill-dir>/scripts/svg-panel.py "<prompt>" <output-dir> [--models openai/gpt-6-astra,z-ai/glm-5.3]
python3 <skill-dir>/scripts/svg-panel.py --render-only <output-dir>/claude.svg
```

- **Models:** `openai/gpt-6-astra` (ZDR on OpenRouter, ~$0.10 per graphic at $10/$50 per Mtok — the strongest text model available for this) and `z-ai/glm-5.3`. Astra is used **only here** — it has no image output, so it never appears in the raster panel.
- **Claude's own entry.** The Agent running this also writes one itself as `<output-dir>/claude.svg`, then renders it with `--render-only`. Three entries, three lineages.
- The script asks each model for *only* an SVG, extracts the first `<svg>…</svg>`, rejects anything that doesn't parse as XML, saves `<model>.svg`, and renders `<model>.png` with `rsvg-convert` so the judges can *see* it. Animated SVGs render as their first frame.
- **Write the prompt for a vector artist**: shapes and their relationship, palette as hex, "no text" unless wanted, target sizes ("works at 32px"), and for animation: what moves, how long, and that the first frame must be presentable.

## 2b. Raster panel — image models

```bash
python3 <skill-dir>/scripts/image-panel.py "<detailed prompt>" <output-dir>
```

Runs three Gemini image tiers in parallel (the only ZDR-clean image generators on OpenRouter — OpenAI's image models have no ZDR endpoint), saves `flash.png`, `nano-banana.png`, `pro.png`, and writes per-model cost. Benchmarked 2026-09-01 on 4 prompts, blind-judged:

| Rank | Model | Notes |
|---|---|---|
| 1 | `google/gemini-3.1-flash-image` | Won 3 of 4; best all-rounder |
| 2 | `google/gemini-2.5-flash-image` ("nano banana") | Won the photorealistic nature shot |
| 3 | `google/gemini-3-pro-image` | Won the logo test; priciest (~$0.14/img) — but logos are SVG now |

The user generates images rarely, so the 3-model panel (~$0.24) is the default; don't downgrade to one model to save money unless asked. To edit an existing raster, call `scripts/generate-image.py` directly with `-i input.png`.

## 3. Two independent judges — same for both panels

Sequentially (concurrent calls can trip OpenRouter's credit hold), two vision models from lineages other than the generators':

```bash
cd <output-dir> && pi -p --no-tools --no-session --provider openrouter --model moonshotai/kimi-k2.5 -- @a.png @b.png @c.png "<judge prompt>"
cd <output-dir> && pi -p --no-tools --no-session --provider openrouter --model z-ai/glm-4.6v      -- @a.png @b.png @c.png "<judge prompt>"
```

For **raster**: "These N images were generated from the prompt '<prompt>'. For each, a one-sentence critique; then your favourite with a one-sentence reason."

For **SVG**, attach the PNGs *and* paste the SVG sources, and ask additionally: does it read as the concept at 32px and at 256px; is the source clean (a `viewBox`, no embedded rasters, no scripts, sane path count); for animation, does the described motion serve the mark or decorate it. A judge that can't see images will still produce a plausible critique from filenames — confirm `pi --list-models <name>` shows `images: yes`, and that the critique cites visual specifics.

## 4. Execution — one Agent call, one clean response

The user invokes this and expects **the files plus two quick critiques in a single response**, not a play-by-play. All of it — the type decision, the panel, Claude's own SVG, rendering, judging — happens inside **one Agent tool call** (general-purpose). It runs asynchronously; after dispatching, say nothing and wait for the completion notification. Brief the agent with the ask, the type you chose, both command lines, the judge prompts, and: send every output with SendUserFile (`display: render`; for SVG send both the `.svg` and its `.png`), then return **only** each judge's pick and one-sentence reason, your own one-sentence recommendation, and cost.

If any raster is a photorealistic depiction of a real, identifiable person, say so in one line and keep it out of anything published.

## 5. After the Agent returns

Relay in one short message: which entry each judge picked and why, your own take, the cost. Nothing about mechanics.
