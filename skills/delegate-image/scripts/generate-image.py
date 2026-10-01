#!/usr/bin/env python3
"""Generate (or edit) an image via an OpenRouter image-output model.

The OpenRouter API key is fetched from pi's credential store
(`pi auth print-api-key --provider openrouter`) so no key is stored here.

Usage:
  generate-image.py "a minimal fox logo, flat vector" -o fox.png
  generate-image.py "same person wearing a red jacket" -i person.png -o out.png
"""

import argparse
import base64
import json
import re
import subprocess
import sys
import urllib.request

DEFAULT_MODEL = "google/gemini-3-pro-image"


def get_api_key():
    result = subprocess.run(
        ["pi", "auth", "print-api-key", "--provider", "openrouter"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def file_to_data_url(path):
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}.get(ext, "png")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL)
    parser.add_argument("-o", "--out", default="generated.png")
    parser.add_argument("-i", "--input", action="append", default=[],
                        help="input image file to edit/reference (repeatable)")
    args = parser.parse_args()

    content = [{"type": "text", "text": args.prompt}]
    for path in args.input:
        content.append({"type": "image_url", "image_url": {"url": file_to_data_url(path)}})

    body = {
        "model": args.model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
        "usage": {"include": True},
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:1000]}")

    if "error" in data:
        sys.exit(f"API error: {data['error']}")

    message = data["choices"][0]["message"]
    images = message.get("images") or []
    if not images:
        sys.exit(f"No image in response. Model said: {message.get('content', '')[:500]}")

    url = images[0]["image_url"]["url"]
    match = re.match(r"data:image/(\w+);base64,(.*)", url, re.DOTALL)
    if not match:
        sys.exit(f"Unexpected image format: {url[:100]}")

    out = args.out
    with open(out, "wb") as f:
        f.write(base64.b64decode(match.group(2)))
    text = (message.get("content") or "").strip()
    cost = data.get("usage", {}).get("cost")
    print(f"saved: {out}" + (f" cost=${cost}" if cost is not None else "") + (f"\nmodel note: {text}" if text else ""))


if __name__ == "__main__":
    main()
