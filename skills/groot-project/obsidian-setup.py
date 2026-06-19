#!/usr/bin/env python3
"""Configure a project's Obsidian vault to the federation baseline.

A project's color is its identity: `.groot-project.toml [terminal].background`
already paints the terminal on `cd`. This makes the project's Obsidian vault a
second view onto that same color — and gives every vault a consistent, readable
theme + a curated plugin set — so a wall of stacked Obsidian windows stops
looking identical.

Design (the package.json / node_modules split):
  - COMMITTED config under .obsidian/ declares the baseline:
      appearance.json        theme (Minimal) + accent (derived from project color)
      app.json               excluded files (node_modules, .next, build, ...)
      community-plugins.json the curated plugin id list
      core-plugins.json      sensible core plugins on (merge, never clobber)
      snippets/project-color.css   chrome-only color paint (titlebar/ribbon)
  - FETCHED, gitignored artifacts are pulled from upstream on demand:
      themes/Minimal/        the theme CSS
      plugins/<id>/          the plugin bundles
  A fresh clone re-runs this (like `npm install`) to repopulate the fetched bits.

Readability principle: color lives in the window CHROME only (titlebar, ribbon,
status bar). The note/editor surface is never tinted — distinguishable AND
readable are not in tension.

Usage:
  obsidian-setup.py [PROJECT_DIR] [--no-fetch] [--dry-run]

  PROJECT_DIR   project root (default: cwd). Must contain .groot-project.toml.
  --no-fetch    write/merge config only; skip downloading theme + plugins.
  --dry-run     print what would change; write nothing.
"""

from __future__ import annotations

import argparse
import colorsys
import json
import subprocess
import sys
import tomllib
from pathlib import Path

# The curated baseline. Each plugin maps a real Derek workflow (see SKILL.md
# Phase 7A). dir name == manifest `id` (Obsidian requires the match).
#
# Versions are PINNED, not "latest" — the package-lock principle, and a hard-won
# one: Templater 2.21+ sets minAppVersion 1.13.0 (an Obsidian *insider* build),
# so "latest" silently installs a plugin that won't enable on stable Obsidian.
# Each pin below is the newest release that runs on current stable Obsidian.
# Bump deliberately, and re-check minAppVersion against stable when you do.
#   id: (repo, version)  ->  assets at releases/download/<version>/<asset>
PLUGINS = {
    "dataview": ("blacksmithgu/obsidian-dataview", "0.5.68"),  # minApp 0.13.11
    "templater-obsidian": ("SilentVoid13/Templater", "2.20.5"),  # minApp 1.12.2
    "obsidian-style-settings": ("mgmeyers/obsidian-style-settings", "1.0.9"),  # 0.11.5
    "obsidian-minimal-settings": (
        "kepano/obsidian-minimal-settings",
        "8.2.3",
    ),  # 1.11.1
}
PLUGIN_ASSETS = ("main.js", "manifest.json", "styles.css")  # styles.css optional

THEME_NAME = "Minimal"
THEME_REPO = "kepano/obsidian-minimal"
THEME_VERSION = "8.2.1"  # minApp 1.9.0
THEME_FILES = ("theme.css", "manifest.json")

# Core plugins we ensure are ON for the design/story workflow. Merged into
# whatever Obsidian already recorded; never disables anything.
CORE_PLUGINS_ON = [
    "file-explorer",
    "global-search",
    "switcher",
    "backlink",
    "outgoing-link",
    "tag-pane",
    "properties",
    "outline",
    "templates",
]

# Hidden from search / graph / quick-switcher. Repo-root docs (DIARY.md,
# TODO.md, CLAUDE.md, ...) deliberately stay visible — only build/vendor noise
# is excluded. Obsidian stores these as `userIgnoreFilters` in app.json.
EXCLUDED_FILTERS = [
    "node_modules/",
    ".next/",
    ".git/",
    "dist/",
    "build/",
    "coverage/",
    "test-results/",
    "playwright-report/",
    ".turbo/",
    ".cache/",
    "public/",
    "static/",
]

SNIPPET_NAME = "project-color"

# Lines appended to .gitignore: commit the declared config, ignore the
# per-machine layout + the fetched (reproducible) artifacts.
GITIGNORE_LINES = [
    ".obsidian/workspace.json",
    ".obsidian/workspace-mobile.json",
    ".obsidian/plugins/",
    ".obsidian/themes/",
]

RAW = "https://raw.githubusercontent.com"
REL = "https://github.com"


def project_color(project_dir: Path) -> str:
    """The project's `[terminal].background` hex, or raise if absent."""
    toml_path = project_dir / ".groot-project.toml"
    if not toml_path.exists():
        raise SystemExit(
            f"no .groot-project.toml in {project_dir} — run /terminal-setup first "
            "so the project has a color to mirror."
        )
    with toml_path.open("rb") as fh:
        data = tomllib.load(fh)
    # Legacy [iterm].color reads transparently, same as terminal-setup.
    term = data.get("terminal") or data.get("iterm") or {}
    color = term.get("background") or term.get("color")
    if not color:
        raise SystemExit(
            f"{toml_path} has no [terminal].background — run /terminal-setup first."
        )
    return color.strip()


def derive_accent(bg_hex: str) -> str:
    """A vivid, readable accent sharing the background's hue.

    Terminal backgrounds are deliberately dark (they fill the whole screen);
    as Obsidian chrome that would barely register against an already-dark UI.
    So we keep the hue but lift saturation/lightness into a vivid band that
    pops as an accent and carries readable text.
    """
    h, _l, _s = rgb_to_hls(bg_hex)
    r, g, b = colorsys.hls_to_rgb(h, 0.62, 0.65)
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def rgb_to_hls(hex_str: str) -> tuple[float, float, float]:
    s = hex_str.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    r, g, b = (int(s[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        text = path.read_text().strip()
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data, dry_run: bool) -> None:
    rendered = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"  would write {path.name}:\n{indent(rendered)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered)
    print(f"  wrote {path.relative_to(path.parents[1])}")


def indent(text: str, n: int = 4) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.splitlines())


def merge_core_plugins(existing, wanted: list[str]):
    """Ensure `wanted` are enabled without disabling anything Obsidian set.

    core-plugins.json is an array of enabled ids in current Obsidian; older
    vaults used an object map. Preserve whichever shape is present.
    """
    if isinstance(existing, dict):
        for pid in wanted:
            existing.setdefault(pid, True)
        return existing
    enabled = list(existing) if isinstance(existing, list) else []
    for pid in wanted:
        if pid not in enabled:
            enabled.append(pid)
    return enabled


def snippet_css(accent: str) -> str:
    return f"""/* project-color.css — written by /groot-project (obsidian-setup.py).
   Paints the WINDOW CHROME with this project's accent so stacked Obsidian
   windows are distinguishable at a glance. Chrome only — the note/editor
   surface is left on the theme's readable defaults on purpose.

   Frame-independent: the active TAB is the always-present signal (it shows
   regardless of "Window frame style"); the --titlebar-* variables add color
   on top when Obsidian draws its own frame. The earlier `.titlebar` rule was
   invisible under a native macOS frame, which is why this looked "minimal". */

body {{
  --titlebar-background: {accent};
  --titlebar-background-focused: {accent};
  --titlebar-text-color: var(--text-on-accent);
  /* Drive the active tab through the theme's own tab variables so the inner
     pill, radius, and connectors all key off the accent — painting only the
     outer header left Minimal's narrower inner pill showing through as a
     mismatched chunk at the tab's bottom edge. */
  --tab-background-active: {accent};
  --tab-text-color-active: var(--text-on-accent);
  --tab-text-color-focused-active: var(--text-on-accent);
  --tab-text-color-focused-active-current: var(--text-on-accent);
}}

/* Primary signal: the active tab, filled the project color. The outer fill
   gives full coverage; the inner pill is flattened to transparent so the fill
   reads as one uniform block (no narrower bottom chunk). */
.workspace .workspace-tab-header.is-active {{
  background-color: {accent} !important;
}}
.workspace .workspace-tab-header.is-active .workspace-tab-header-inner {{
  background-color: transparent !important;
}}
.workspace .workspace-tab-header.is-active .workspace-tab-header-inner-title,
.workspace .workspace-tab-header.is-active .workspace-tab-header-inner-icon {{
  color: var(--text-on-accent) !important;
}}

/* Secondary accents — always-present edges. */
.workspace-ribbon.side-dock-ribbon {{
  border-right: 3px solid {accent};
}}
.status-bar {{
  border-top: 2px solid {accent};
}}
"""


def write_config(vault: Path, accent: str, dry_run: bool) -> None:
    print("config:")

    appearance = load_json(vault / "appearance.json")
    appearance["cssTheme"] = THEME_NAME
    appearance["accentColor"] = accent
    snippets = appearance.get("enabledCssSnippets", [])
    if SNIPPET_NAME not in snippets:
        snippets.append(SNIPPET_NAME)
    appearance["enabledCssSnippets"] = snippets
    write_json(vault / "appearance.json", appearance, dry_run)

    app = load_json(vault / "app.json")
    filters = app.get("userIgnoreFilters", [])
    for f in EXCLUDED_FILTERS:
        if f not in filters:
            filters.append(f)
    app["userIgnoreFilters"] = filters
    write_json(vault / "app.json", app, dry_run)

    community = load_json(vault / "community-plugins.json")
    community = community if isinstance(community, list) else []
    for pid in PLUGINS:
        if pid not in community:
            community.append(pid)
    write_json(vault / "community-plugins.json", community, dry_run)

    core = load_json(vault / "core-plugins.json")
    core = merge_core_plugins(core if core else [], CORE_PLUGINS_ON)
    write_json(vault / "core-plugins.json", core, dry_run)

    snippet_path = vault / "snippets" / f"{SNIPPET_NAME}.css"
    css = snippet_css(accent)
    if dry_run:
        print(f"  would write snippets/{SNIPPET_NAME}.css")
    else:
        snippet_path.parent.mkdir(parents=True, exist_ok=True)
        snippet_path.write_text(css)
        print(f"  wrote snippets/{SNIPPET_NAME}.css")


def fetch(url: str, dest: Path, dry_run: bool, optional: bool = False) -> bool:
    """Download via `curl` — it uses the system cert store, unlike macOS's
    bundled Python (whose urllib trips CERTIFICATE_VERIFY_FAILED)."""
    if dry_run:
        print(f"  would fetch {dest.parent.name}/{dest.name}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    # -f: fail (nonzero) on HTTP >=400 so an optional-asset 404 is detectable.
    result = subprocess.run(
        ["curl", "-fsSL", "--retry", "2", "-o", str(dest), url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        dest.unlink(missing_ok=True)
        if optional and result.returncode == 22:  # curl's HTTP-error code (404 here)
            return False
        print(
            f"  ! failed {dest.parent.name}/{dest.name} "
            f"(curl {result.returncode}: {result.stderr.strip()})",
            file=sys.stderr,
        )
        return False
    print(f"  fetched {dest.parent.name}/{dest.name}")
    return True


def fetch_artifacts(vault: Path, dry_run: bool) -> None:
    print("fetch:")
    theme_dir = vault / "themes" / THEME_NAME
    for f in THEME_FILES:
        fetch(f"{RAW}/{THEME_REPO}/{THEME_VERSION}/{f}", theme_dir / f, dry_run)
    for pid, (repo, version) in PLUGINS.items():
        plugin_dir = vault / "plugins" / pid
        for asset in PLUGIN_ASSETS:
            optional = asset == "styles.css"
            fetch(
                f"{REL}/{repo}/releases/download/{version}/{asset}",
                plugin_dir / asset,
                dry_run,
                optional=optional,
            )


GITIGNORE_HEADER = (
    "# Obsidian: commit declared config, ignore layout + fetched artifacts"
)
# A bare ignore of the whole vault dir — hides the committed config too.
BARE_OBSIDIAN = {".obsidian", ".obsidian/", "/.obsidian", "/.obsidian/"}

# todo: when adopting the baseline in a project with a lint/format pre-commit
# hook, the fetched plugin JS under .obsidian/plugins/ breaks it — tools that
# don't read .gitignore (eslint flat-config globalIgnores, prettier) scan the
# minified bundles and fail. Hand-fixed two adopting projects (one's eslint
# config, another's prettierignore) on first adoption; this script should
# detect a project's lint/format config and add `.obsidian/**` to its ignores
# as part of setup.


def update_gitignore(project_dir: Path, dry_run: bool) -> None:
    print("gitignore:")
    path = project_dir / ".gitignore"
    existing = path.read_text().splitlines() if path.exists() else []

    # A bare `.obsidian/` defeats the declare-in-git half: it ignores the
    # config we want tracked. Refine it in place to the selective form
    # (config tracked; only layout + fetched artifacts ignored), consolidating
    # any stray selective dupes into one block where the bare line was.
    if any(ln.strip() in BARE_OBSIDIAN for ln in existing):
        if dry_run:
            print("  would refine bare '.obsidian/' -> selective block")
            return
        out, placed = [], False
        drop = BARE_OBSIDIAN | set(GITIGNORE_LINES) | {GITIGNORE_HEADER}
        for ln in existing:
            if ln.strip() not in drop:
                out.append(ln)
                continue
            if ln.strip() in BARE_OBSIDIAN and not placed:
                out.extend([GITIGNORE_HEADER, *GITIGNORE_LINES])
                placed = True
        path.write_text("\n".join(out).rstrip("\n") + "\n")
        print("  refined bare '.obsidian/' -> selective (config now tracked)")
        return

    missing = [ln for ln in GITIGNORE_LINES if ln not in existing]
    if not missing:
        print("  already covered")
        return
    if dry_run:
        for ln in missing:
            print(f"  would add {ln}")
        return
    block = "\n" if existing and existing[-1].strip() else ""
    block += GITIGNORE_HEADER + "\n" + "\n".join(missing) + "\n"
    with path.open("a") as fh:
        fh.write(block)
    for ln in missing:
        print(f"  added {ln}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "project_dir", nargs="?", default=".", help="project root (default: cwd)"
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="write/merge config only; skip downloads",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show changes; write nothing"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"not a directory: {project_dir}")

    bg = project_color(project_dir)
    accent = derive_accent(bg)
    vault = project_dir / ".obsidian"

    print(f"vault:  {vault}")
    print(f"color:  {bg} (terminal) -> {accent} (obsidian accent + chrome)\n")

    write_config(vault, accent, args.dry_run)
    print()
    if args.no_fetch:
        print("fetch:  skipped (--no-fetch)")
    else:
        fetch_artifacts(vault, args.dry_run)
    print()
    update_gitignore(project_dir, args.dry_run)

    if not args.dry_run:
        print("\ndone. Restart Obsidian (or reload the vault) to apply.")
        print("First open may prompt once to enable community plugins.")


if __name__ == "__main__":
    main()
