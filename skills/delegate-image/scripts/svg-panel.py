#!/usr/bin/env python3
"""SVG panel: ask several TEXT models for the same vector graphic, validate, render to PNG for the judges.

  svg-panel.py "<prompt>" <outdir> [--models m1,m2] [--size 1024]
  svg-panel.py --render-only file.svg [--size 1024]      # e.g. the SVG Claude authored itself

Models are called through pi (OpenRouter). Each reply is scanned for the first <svg>...</svg>,
parsed as XML (a reply that doesn't parse is recorded as a failure, not saved), saved as
<outdir>/<tag>.svg, and rendered with rsvg-convert (fallback: magick) to <outdir>/<tag>.png.
Animated SVGs render as their first frame; judges get the PNG plus the source.
"""
import argparse, os, re, shutil, subprocess, sys, xml.etree.ElementTree as ET

DEFAULT_MODELS = ["openai/gpt-6-astra", "z-ai/glm-5.3"]
SVG_RE = re.compile(r"<svg\b.*?</svg>", re.S | re.I)

def render(svg_path, png_path, size):
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-a", "-o", png_path, svg_path], check=True)
    elif shutil.which("magick"):
        subprocess.run(["magick", "-background", "none", "-density", "300", svg_path, "-resize", f"{size}x{size}", png_path], check=True)
    else:
        sys.exit("no SVG rasterizer found (need rsvg-convert or ImageMagick)")

RULES = ("Reply with ONLY an SVG document: no prose, no code fences, no explanation. Use a viewBox; no external "
         "references, scripts, or raster images. If animation is requested, use CSS @keyframes inside a <style> element "
         "(or SMIL) and keep the static first frame presentable. Do NOT animate unless the brief asks for it.")

def ask(model, prompt, timeout=180):
    """Instructions ride in the user prompt (a --system-prompt made one model hang); thinking off — SVG doesn't need it."""
    try:
        # stdin=DEVNULL matters: pi reads a non-TTY stdin as more prompt and waits for EOF — from Python that never comes.
        r = subprocess.run(["pi", "-p", "--no-tools", "--no-session", "--provider", "openrouter",
                            "--model", model, RULES + "\n\n" + prompt],
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?"); ap.add_argument("outdir", nargs="?")
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS)); ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--render-only")
    a = ap.parse_args()
    if a.render_only:
        png = os.path.splitext(a.render_only)[0] + ".png"; render(a.render_only, png, a.size); print(f"rendered: {png}"); return
    if not (a.prompt and a.outdir): ap.error("prompt and outdir required (or --render-only)")
    os.makedirs(a.outdir, exist_ok=True); manifest = []
    models = a.models.split(",")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        replies = dict(zip(models, pool.map(lambda m: ask(m, a.prompt), models)))   # models in parallel
    for model in models:
        tag = model.split("/")[-1].replace(":", "-")
        reply = replies[model]
        m = SVG_RE.search(reply)
        if reply == "TIMEOUT":
            manifest.append(f"[{tag}] model={model} status=timeout"); continue
        if not m:
            manifest.append(f"[{tag}] model={model} status=no-svg reply={reply.strip()[:120]!r}"); continue
        svg = m.group(0)
        try: ET.fromstring(svg)
        except ET.ParseError as e:
            manifest.append(f"[{tag}] model={model} status=invalid-xml error={e}"); continue
        svg_path = os.path.join(a.outdir, f"{tag}.svg"); open(svg_path, "w").write(svg)
        png_path = os.path.join(a.outdir, f"{tag}.png"); render(svg_path, png_path, a.size)
        animated = bool(re.search(r"@keyframes|<animate", svg, re.I))
        manifest.append(f"[{tag}] model={model} status=0 saved={svg_path} png={png_path} bytes={len(svg)} animated={animated}")
    open(os.path.join(a.outdir, "panel-manifest.txt"), "w").write("\n".join(manifest) + "\n")
    print("\n".join(manifest))

if __name__ == "__main__":
    main()
