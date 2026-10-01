#!/usr/bin/env python3
"""Generate the same prompt across the top-3 ranked image models in parallel.

Usage:
  image-panel.py "<prompt>" <output-dir>
"""

import concurrent.futures
import os
import subprocess
import sys

MODELS = [
    ("flash", "google/gemini-3.1-flash-image"),
    ("nano-banana", "google/gemini-2.5-flash-image"),
    ("pro", "google/gemini-3-pro-image"),
]


def run_one(script, prompt, outdir, suffix, model):
    out = os.path.join(outdir, f"{suffix}.png")
    result = subprocess.run(
        [sys.executable, script, prompt, "-m", model, "-o", out],
        capture_output=True, text=True,
    )
    status = result.returncode
    text = (result.stdout + result.stderr).strip().replace("\n", " ")
    return f"[{suffix}] model={model} status={status} {text}"


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: image-panel.py \"<prompt>\" [output-dir]")
    prompt = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate-image.py")
    manifest_path = os.path.join(outdir, "panel-manifest.txt")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run_one, script, prompt, outdir, suffix, model) for suffix, model in MODELS]
        lines = [f.result() for f in futures]

    with open(manifest_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
