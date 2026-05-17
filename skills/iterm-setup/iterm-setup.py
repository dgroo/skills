#!/usr/bin/env python3
"""Generate iTerm2 Dynamic Profile JSON for per-project Automatic Profile Switching.

Writes a JSON file to ~/Library/Application Support/iTerm2/DynamicProfiles/.
iTerm2 watches that directory and loads new/changed profiles live. Each profile
inherits from "Default" so only colors and the APS rule are overridden.

Optionally adds a shell alias to ~/.zshrc for quick `cd` to the project.

Color palette: project-seeded random generation. Each project name produces a
deterministic palette of 10 dark, saturated colors with hue spread, named by
hue bucket (Crimson, Forest, Indigo, etc.). Same project always shows the same
palette across runs; different projects get different palettes. Solves the
"fixed 10 colors run out" problem while staying stable for re-runs. A `--hex`
flag bypasses the palette for one-off custom colors.

Color usage is read from existing on-disk profiles (no separate state file)
so the picker can flag candidate colors that overlap (RGB-near) with colors
already in use by neighboring projects.
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import random
import re
import sys
import tomllib
from pathlib import Path

PARENT_PROFILE = "Default"
GUID_PREFIX = "iterm-setup-"

DEFAULT_PALETTE_SIZE = 14
VIVID_PALETTE_SIZE = 4

# Tab/window title rendered by iTerm via the profile's "Custom" title slot.
# Pairs with the Claude Code Stop / Notification / UserPromptSubmit hooks,
# which set the iTerm user variable `claudeState` to a state glyph
# (🟢 working, ❓ waiting, ☑️ done). `\(session.name)` is whatever CC
# renames the session to (the topic). `\(session.profileName)` is this
# profile's Name (the project), so the title reads e.g.
#     🟢 myproject - Refactor login flow
DEFAULT_TITLE_FORMAT = r"\(user.claudeState)\(session.profileName) - \(session.name)"

# iTermTitleComponentsCustom = 1 << 4 (from iTerm's iTermTitleComponents enum
# in sources/Settings/Profiles/ITAddressBookMgr.h). Sets bit so iTerm renders
# the "Custom Tab Title" / "Custom Window Title" interpolated strings instead
# of one of the built-in components (Job / Session Name / etc).
ITERM_TITLE_COMPONENTS_CUSTOM = 16

# Hue buckets at 22.5° intervals around the wheel; each generated palette
# entry takes its name from whichever bucket is closest to its hue.
HUE_BUCKETS: list[tuple[float, str]] = [
    (0.0,   "Crimson"),
    (22.5,  "Vermillion"),
    (45.0,  "Rust"),
    (67.5,  "Amber"),
    (90.0,  "Olive"),
    (112.5, "Moss"),
    (135.0, "Forest"),
    (157.5, "Pine"),
    (180.0, "Teal"),
    (202.5, "Steel"),
    (225.0, "Indigo"),
    (247.5, "Violet"),
    (270.0, "Plum"),
    (292.5, "Magenta"),
    (315.0, "Wine"),
    (337.5, "Burgundy"),
]

# HSL constraints for generated colors: dark enough to read light text on top,
# saturated enough that colors look intentional (not muddy gray-by-accident).
# The main range spans deep (0.05–0.13) to lifted (0.13–0.22) bands so the
# stratified palette gets visible contrast between adjacent indices.
HSL_LIGHTNESS_MIN = 0.05
HSL_LIGHTNESS_MAX = 0.22
HSL_SATURATION_MIN = 0.45
HSL_SATURATION_MAX = 0.85

# Vivid palette — for highlight / special-case projects (e.g. ~/.claude itself,
# anything you want to be unmistakable at a glance). Brighter than the main
# range; white text is still readable up to ~0.32 lightness.
VIVID_LIGHTNESS_MIN = 0.22
VIVID_LIGHTNESS_MAX = 0.32
VIVID_SATURATION_MIN = 0.55
VIVID_SATURATION_MAX = 0.90

DEFAULT_FOREGROUND = (0.88, 0.86, 0.82)
DEFAULT_CURSOR = (0.88, 0.86, 0.82)

DYNAMIC_PROFILES_DIR = (
    Path.home() / "Library" / "Application Support" / "iTerm2" / "DynamicProfiles"
)
ZSHRC_PATH = Path.home() / ".zshrc"
CODE_DIR = Path.home() / "code"

# Per-project workstation-setup file, checked into git so a fresh clone on
# another machine can reproduce the iTerm profile (and, later, other
# per-project workstation conventions). See `read_groot_project_iterm` /
# `write_groot_project_iterm` for the read/write seam and SKILL.md for the
# prompting flow.
GROOT_PROJECT_TOML_NAME = ".groot-project.toml"
GROOT_PROJECT_TOML_HEADER = (
    "# .groot-project.toml — per-project workstation conventions.\n"
    "# Tracked in git so a fresh clone reproduces this project's setup on a\n"
    "# new machine. Read/written by /iterm-setup (and /groot-project).\n"
)
ITERM_TOML_FIELDS = ("color", "alias", "name")

VALID_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VALID_ALIAS_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEX_COLOR_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")

SHELL_INTEGRATION_PATHS = [
    Path.home() / ".iterm2_shell_integration.zsh",
    Path.home() / ".iterm2_shell_integration.bash",
    Path.home() / ".iterm2_shell_integration.fish",
]

# RGB distance threshold (in 0-1 float space) for considering two colors
# "the same" when detecting overlap with existing profiles. ~0.05 ≈ 13/255
# per channel — generous enough to catch visually similar but slightly
# different shades (which the seeded random can produce).
USAGE_DISTANCE_THRESHOLD = 0.05

ALIAS_LINE_RE = re.compile(
    r"^[ \t]*alias[ \t]+([A-Za-z_][A-Za-z0-9_]*)=(['\"])(.*?)\2[ \t]*(?:#.*)?$",
    re.MULTILINE,
)
ALIAS_CHAIN_RESOLVE_PASSES = 5


class ItermSetupError(RuntimeError):
    pass


class InvalidProfileNameError(ItermSetupError):
    pass


class InvalidAliasNameError(ItermSetupError):
    pass


class ProfileExistsError(ItermSetupError):
    pass


class InvalidColorIndexError(ItermSetupError):
    pass


class InvalidHexColorError(ItermSetupError):
    pass


class AliasConflictError(ItermSetupError):
    pass


class AliasTargetCollisionError(ItermSetupError):
    pass


class GrootProjectTomlError(ItermSetupError):
    pass


def stable_seed(s: str) -> int:
    """Deterministic int seed from a string. Avoids Python's randomized hash()."""
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big")


def hue_bucket_name(hue_deg: float) -> str:
    """Closest bucket name for a hue, honoring the wheel's circular distance."""
    def circ_dist(a: float, b: float) -> float:
        d = abs(a - b) % 360.0
        return min(d, 360.0 - d)
    return min(HUE_BUCKETS, key=lambda b: circ_dist(hue_deg, b[0]))[1]


def hsl_to_rgb(h_deg: float, s: float, light: float) -> tuple[float, float, float]:
    """Standard HSL → RGB. Returns floats in [0, 1]. (colorsys uses HLS arg order.)"""
    return colorsys.hls_to_rgb(h_deg / 360.0, light, s)


def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    """Parse '#RRGGBB' or 'RRGGBB' into floats in [0, 1]."""
    m = HEX_COLOR_RE.match(hex_str.strip())
    if not m:
        raise InvalidHexColorError(f"Hex color must be #RRGGBB; got {hex_str!r}")
    h = m.group(1)
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def rgb_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """Euclidean distance in float-RGB space. Cheap stand-in for perceptual distance."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def generate_palette(
    seed: str,
    count: int = DEFAULT_PALETTE_SIZE,
    light_min: float = HSL_LIGHTNESS_MIN,
    light_max: float = HSL_LIGHTNESS_MAX,
    sat_min: float = HSL_SATURATION_MIN,
    sat_max: float = HSL_SATURATION_MAX,
    stratify: bool = True,
    seed_suffix: str = "",
) -> list[tuple[str, tuple[float, float, float]]]:
    """Project-seeded palette: dark, saturated, hue-spread, deterministic per name.

    Same `seed` always produces the same palette. Hues sweep around the wheel
    in ~`360/count`° steps with small jitter, so the palette covers warm-to-cool
    rather than N reds. Names come from the closest hue bucket; duplicates
    within the same palette get a numeric suffix.

    With `stratify=True` (default), even indices draw from the lower half of
    [light_min, light_max] (deep) and odd indices from the upper half (lifted),
    so adjacent palette entries get visible lightness contrast. Set False for
    flat ranges (e.g., the vivid section, where every entry should be bright).

    `seed_suffix` lets callers derive a sibling palette from the same project
    name without re-using the same hues (e.g., `seed_suffix='::vivid'` for
    the highlight section).
    """
    rng = random.Random(stable_seed(seed + seed_suffix))
    base_hue = rng.uniform(0.0, 360.0)
    step = 360.0 / count
    jitter = step / 4.0
    mid = (light_min + light_max) / 2 if stratify and light_max - light_min > 0.05 else None
    used: dict[str, int] = {}
    palette: list[tuple[str, tuple[float, float, float]]] = []
    for i in range(count):
        hue = (base_hue + i * step + rng.uniform(-jitter, jitter)) % 360.0
        sat = rng.uniform(sat_min, sat_max)
        if mid is not None:
            band = (light_min, mid) if i % 2 == 0 else (mid, light_max)
            light = rng.uniform(*band)
        else:
            light = rng.uniform(light_min, light_max)
        rgb = hsl_to_rgb(hue, sat, light)
        name = hue_bucket_name(hue)
        used[name] = used.get(name, 0) + 1
        if used[name] > 1:
            name = f"{name} {used[name]}"
        palette.append((name, rgb))
    return palette


def generate_vivid_palette(
    seed: str,
    count: int = VIVID_PALETTE_SIZE,
) -> list[tuple[str, tuple[float, float, float]]]:
    """A small additional palette of brighter highlight-grade colors.

    Project-seeded with a different seed slice so the vivid hues don't
    necessarily duplicate the main palette's first few entries. Flat
    lightness band (no stratification) — every entry should be visibly
    bright relative to the main palette.
    """
    return generate_palette(
        seed=seed,
        count=count,
        light_min=VIVID_LIGHTNESS_MIN,
        light_max=VIVID_LIGHTNESS_MAX,
        sat_min=VIVID_SATURATION_MIN,
        sat_max=VIVID_SATURATION_MAX,
        stratify=False,
        seed_suffix="::vivid",
    )


def rgb_float_to_8bit(rgb: tuple[float, float, float]) -> tuple[int, int, int]:
    r, g, b = (max(0, min(255, round(c * 255))) for c in rgb)
    return r, g, b


def ansi_swatch(rgb: tuple[float, float, float], text: str, width: int = 36) -> str:
    r, g, b = rgb_float_to_8bit(rgb)
    fr, fg_, fb = rgb_float_to_8bit(DEFAULT_FOREGROUND)
    padded = f" {text} ".ljust(width)
    return f"\x1b[48;2;{r};{g};{b}m\x1b[38;2;{fr};{fg_};{fb}m{padded}\x1b[0m"


def all_existing_profile_colors() -> list[tuple[str, tuple[float, float, float]]]:
    """Return [(profile_name, rgb), ...] for every iterm-setup-authored profile.

    Replaces the old `color_usage_from_disk` (which was keyed by fixed-palette
    index). With per-project palettes we just collect raw RGBs and let callers
    do distance-based matching.
    """
    results: list[tuple[str, tuple[float, float, float]]] = []
    if not DYNAMIC_PROFILES_DIR.exists():
        return results
    for json_path in sorted(DYNAMIC_PROFILES_DIR.glob("*.json")):
        try:
            data = json.loads(json_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        for profile in data.get("Profiles", []):
            if not profile.get("Guid", "").startswith(GUID_PREFIX):
                continue
            bg = profile.get("Background Color") or {}
            try:
                rgb = (
                    float(bg["Red Component"]),
                    float(bg["Green Component"]),
                    float(bg["Blue Component"]),
                )
            except (KeyError, TypeError, ValueError):
                continue
            results.append((profile.get("Name", json_path.stem), rgb))
    return results


def palette_collisions(
    palette: list[tuple[str, tuple[float, float, float]]],
    existing_colors: list[tuple[str, tuple[float, float, float]]],
    exclude_name: str | None = None,
) -> dict[int, list[str]]:
    """For each palette index, profile names whose RGB falls within threshold.

    Used to render `≈ used by: <profile>` annotations in the picker.
    """
    out: dict[int, list[str]] = {}
    for i, (_, p_rgb) in enumerate(palette):
        for name, e_rgb in existing_colors:
            if exclude_name is not None and name == exclude_name:
                continue
            if rgb_distance(p_rgb, e_rgb) < USAGE_DISTANCE_THRESHOLD:
                out.setdefault(i, []).append(name)
    return out


def existing_profile_info(name: str) -> dict | None:
    """Current RGB/name for an existing profile, or None if absent.

    With generated palettes there's no canonical "color name" — we derive a
    human label from the hue bucket of the stored RGB.
    """
    path = DYNAMIC_PROFILES_DIR / f"{name}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    profiles = data.get("Profiles") or []
    if not profiles:
        return None
    profile = profiles[0]
    bg = profile.get("Background Color") or {}
    try:
        rgb = (
            float(bg["Red Component"]),
            float(bg["Green Component"]),
            float(bg["Blue Component"]),
        )
    except (KeyError, TypeError, ValueError):
        return None
    h, light, s = colorsys.rgb_to_hls(*rgb)
    color_label = hue_bucket_name(h * 360.0)
    bound = profile.get("Bound Hosts") or [None]
    return {
        "name": profile.get("Name", name),
        "rgb": rgb,
        "color_label": color_label,
        "pattern": bound[0],
        "path": path,
    }


def palette_index_near_rgb(
    palette: list[tuple[str, tuple[float, float, float]]],
    rgb: tuple[float, float, float],
) -> int | None:
    """Index into `palette` whose RGB is closest to `rgb` AND within threshold."""
    best_i: int | None = None
    best_d = USAGE_DISTANCE_THRESHOLD
    for i, (_, p_rgb) in enumerate(palette):
        d = rgb_distance(p_rgb, rgb)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def render_palette(
    label: str,
    palette: list[tuple[str, tuple[float, float, float]]],
    existing_colors: list[tuple[str, tuple[float, float, float]]] | None = None,
    existing: dict | None = None,
    vivid_section: list[tuple[str, tuple[float, float, float]]] | None = None,
) -> None:
    if existing is not None:
        r, g, b = rgb_float_to_8bit(existing["rgb"])
        print(
            f"\nExisting profile {existing['name']!r}: "
            f"{existing['color_label']} (#{r:02X}{g:02X}{b:02X}), APS={existing['pattern']}"
        )
        print("(re-run with --color N --force to change the color, or --hex #RRGGBB --force for a custom one)")

    # Combined palette feeds collision + current-marker detection so markers
    # work whether the existing color sits in the main band or the vivid section.
    combined = palette + (vivid_section or [])
    collisions = palette_collisions(
        combined,
        existing_colors or [],
        exclude_name=existing["name"] if existing else None,
    )
    current_idx = (
        palette_index_near_rgb(combined, existing["rgb"]) if existing is not None else None
    )

    def _render_row(i_one_based: int, name: str, rgb: tuple[float, float, float]) -> None:
        swatch = ansi_swatch(rgb, f"{label}  →  {name}")
        markers: list[str] = []
        if current_idx is not None and i_one_based - 1 == current_idx:
            markers.append("★ current")
        others = collisions.get(i_one_based - 1, [])
        if others:
            markers.append(f"≈ used by: {', '.join(sorted(others))}")
        suffix = f"  {' / '.join(markers)}" if markers else ""
        print(f"  {i_one_based:>2}. {swatch}{suffix}")

    print("\nPalette (project-seeded; same project always shows the same swatches):\n")
    for i, (name, rgb) in enumerate(palette, start=1):
        _render_row(i, name, rgb)
    print()

    if vivid_section:
        offset = len(palette)
        print("Vivid (highlight projects — brighter, harder to miss):\n")
        for j, (name, rgb) in enumerate(vivid_section, start=1):
            _render_row(offset + j, name, rgb)
        print()
        print("(pass --vivid for a full vivid palette instead of just these few)")
        print()

    # Existing profiles whose color isn't near anything in the combined palette:
    # show as a footer so the user still sees what's in use globally.
    if existing_colors:
        unmatched: list[tuple[str, tuple[float, float, float]]] = []
        for ex_name, ex_rgb in existing_colors:
            if existing is not None and ex_name == existing["name"]:
                continue
            if palette_index_near_rgb(combined, ex_rgb) is None:
                unmatched.append((ex_name, ex_rgb))
        if unmatched:
            print("Other existing profiles (outside this palette):")
            for ex_name, ex_rgb in sorted(unmatched):
                r, g, b = rgb_float_to_8bit(ex_rgb)
                h, _, _ = colorsys.rgb_to_hls(*ex_rgb)
                bucket = hue_bucket_name(h * 360.0)
                swatch = ansi_swatch(ex_rgb, f"{bucket}  ({ex_name})")
                print(f"     {swatch}  #{r:02X}{g:02X}{b:02X}")
            print()


def suggest_default_color_index(
    palette: list[tuple[str, tuple[float, float, float]]],
    existing_colors: list[tuple[str, tuple[float, float, float]]],
) -> int:
    """Pick a default palette index: the one furthest from any existing profile's RGB.

    Maximises visual distinctness against neighboring projects. Falls back to
    index 0 if there are no existing profiles to compare against.
    """
    if not existing_colors:
        return 0
    best_i = 0
    best_min_d = -1.0
    for i, (_, p_rgb) in enumerate(palette):
        min_d = min(rgb_distance(p_rgb, e_rgb) for _, e_rgb in existing_colors)
        if min_d > best_min_d:
            best_min_d = min_d
            best_i = i
    return best_i


def color_components(rgb: tuple[float, float, float]) -> dict[str, float]:
    r, g, b = rgb
    return {"Red Component": r, "Green Component": g, "Blue Component": b}


def build_profile(
    name: str,
    rgb: tuple[float, float, float],
    pattern: str,
    title_format: str | None = None,
) -> dict:
    profile: dict = {
        "Name": name,
        "Guid": f"{GUID_PREFIX}{name}",
        "Dynamic Profile Parent Name": PARENT_PROFILE,
        "Bound Hosts": [pattern],
        "Background Color": color_components(rgb),
        "Foreground Color": color_components(DEFAULT_FOREGROUND),
        "Cursor Color": color_components(DEFAULT_CURSOR),
    }
    if title_format is not None:
        # Set both Tab and Window title; iTerm uses each on different surfaces.
        profile["Title Components"] = ITERM_TITLE_COMPONENTS_CUSTOM
        profile["Custom Tab Title"] = title_format
        profile["Custom Window Title"] = title_format
        profile["Use Custom Window Title"] = True
    return {"Profiles": [profile]}


def validate_profile_name(name: str) -> None:
    if not VALID_PROFILE_NAME_RE.match(name):
        raise InvalidProfileNameError(
            f"Profile name {name!r} is invalid. "
            "Use letters, digits, dot, dash, underscore; start with a letter or digit."
        )


def validate_alias_name(name: str) -> None:
    if not VALID_ALIAS_NAME_RE.match(name):
        raise InvalidAliasNameError(
            f"Alias name {name!r} is invalid. "
            "Use letters, digits, underscore; start with a letter or underscore."
        )


def pick_color_interactive(
    name: str,
    palette: list[tuple[str, tuple[float, float, float]]],
    existing_colors: list[tuple[str, tuple[float, float, float]]],
    existing: dict | None = None,
    vivid_section: list[tuple[str, tuple[float, float, float]]] | None = None,
) -> int:
    """Render the palette (main + optional vivid section) and prompt for an index.

    Returns the 0-based index into the combined `palette + vivid_section`.
    """
    render_palette(name, palette, existing_colors, existing, vivid_section=vivid_section)
    combined = palette + (vivid_section or [])
    # Restrict default suggestions to the main palette — vivid is reserved for
    # opt-in special-case projects. (When --vivid is set, `palette` already IS
    # the vivid palette and `vivid_section` is empty, so this still picks from
    # what the user asked for.) The returned index is 0..len(palette)-1, which
    # is still a valid index into `combined`.
    suggested = suggest_default_color_index(palette, existing_colors)
    prompt_suffix = f" (default: {suggested + 1})"
    while True:
        try:
            raw = input(f"Pick a color for {name!r} [1-{len(combined)}]{prompt_suffix}: ").strip()
        except EOFError as e:
            raise InvalidColorIndexError("Stdin closed before a color was selected.") from e
        if not raw:
            return suggested
        try:
            idx = int(raw)
        except ValueError:
            print(f"  '{raw}' is not a number. Try again.")
            continue
        if 1 <= idx <= len(combined):
            return idx - 1
        print(f"  Out of range; try 1-{len(combined)}.")


def pick_title_format_interactive() -> str | None:
    """Default title format unless the user wants to customize/skip.

    Returns the chosen format string, or None to skip the custom-title keys
    entirely (profile inherits whatever the Default profile has). Defaults
    to DEFAULT_TITLE_FORMAT on EOF / blank input — accepting is the cheap
    path so users can ENTER through.
    """
    print(f"\nTitle format default:\n  {DEFAULT_TITLE_FORMAT}")
    print(
        "(rendered by iTerm — '\\(user.claudeState)' is set by the Claude Code\n"
        " hooks to a 🟢/❓/☑️ glyph; '\\(session.name)' is CC's auto-topic)"
    )
    while True:
        try:
            raw = input("Accept default? [Y/n=skip/c=customize]: ").strip().lower()
        except EOFError:
            return DEFAULT_TITLE_FORMAT
        if raw in ("", "y", "yes"):
            return DEFAULT_TITLE_FORMAT
        if raw in ("n", "no", "skip"):
            return None
        if raw in ("c", "customize"):
            try:
                fmt = input("Custom format (ENTER to use default): ").strip()
            except EOFError:
                return DEFAULT_TITLE_FORMAT
            return fmt or DEFAULT_TITLE_FORMAT
        print("  Please enter Y (default), n (skip), or c (customize).")


def shell_integration_installed() -> bool:
    return any(p.exists() for p in SHELL_INTEGRATION_PATHS)


CODE_ALIAS_PATTERN = re.compile(
    r"^[ \t]*alias[ \t]+code=['\"]cd[ \t]+(?:~/code|\$HOME/code)['\"][ \t]*$",
    re.MULTILINE,
)


def has_code_chain_alias(zshrc_text: str) -> bool:
    """True if `alias code='cd ~/code'` (or its $HOME variant) is present in zshrc.

    The `'code;cd X'` alias shorthand chains off this — without it, generated
    aliases like `alias myproject='code;cd myproject'` would be broken. Detecting
    this lets us fall back to plain `'cd ~/<rel>'` for users who don't have the
    chain alias set up.
    """
    return CODE_ALIAS_PATTERN.search(zshrc_text) is not None


def alias_body_for_target(target: Path, zshrc_text: str = "") -> str:
    """Right-hand side of `alias X=...` for a `cd` target.

    Prefers `'code;cd <name>'` for direct children of ~/code *when the user's
    ~/.zshrc has an `alias code='cd ~/code'` line to chain off*. Otherwise
    falls back to `'cd ~/<rel>'` for paths under $HOME and `'cd <abs>'` otherwise.

    Pass the zshrc text in to enable the shortcut; omit it (default) to skip
    detection and always use the plain form.
    """
    home = Path.home()
    if zshrc_text and has_code_chain_alias(zshrc_text):
        try:
            rel_code = target.relative_to(CODE_DIR)
            if len(rel_code.parts) == 1:
                return f"'code;cd {rel_code}'"
        except ValueError:
            pass
    try:
        rel_home = target.relative_to(home)
        return f"'cd ~/{rel_home}'"
    except ValueError:
        return f"'cd {target}'"


def parse_aliases(zshrc_text: str) -> list[tuple[str, str]]:
    """Return [(alias_name, body), ...] from ~/.zshrc.

    Catches `alias NAME='...'` / `alias NAME="..."` lines. Skips anything we
    can't parse as a single quoted body (e.g., bare-word, complex shell).
    """
    return [(m.group(1), m.group(3)) for m in ALIAS_LINE_RE.finditer(zshrc_text)]


def _unescape_shell_path(s: str) -> str:
    # Aliases like `cd ~/Mobile\ Documents/...` use shell escaping for spaces;
    # turn them into the real filesystem path so resolved targets compare correctly.
    return s.replace(r"\ ", " ")


def _resolve_one_alias_body(body: str, resolver: dict[str, Path]) -> Path | None:
    """Try to resolve an alias body to a `cd` target. None if can't tell.

    Recognized shapes:
      cd ~/path      cd $HOME/path      cd /abs/path
      <prefix>;cd <subpath>        (chained on a previously-resolved alias)
    """
    home = Path.home()
    body = body.strip()

    m = re.fullmatch(r"cd[ \t]+~/?(.*)", body)
    if m:
        sub = _unescape_shell_path(m.group(1))
        return (home / sub).resolve() if sub else home.resolve()

    m = re.fullmatch(r"cd[ \t]+\$HOME/?(.*)", body)
    if m:
        sub = _unescape_shell_path(m.group(1))
        return (home / sub).resolve() if sub else home.resolve()

    m = re.fullmatch(r"cd[ \t]+(/.+)", body)
    if m:
        return Path(_unescape_shell_path(m.group(1))).resolve()

    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)[ \t]*;[ \t]*cd[ \t]+(\S+)", body)
    if m:
        prefix_name, subpath = m.groups()
        prefix_target = resolver.get(prefix_name)
        if prefix_target is not None:
            return (prefix_target / _unescape_shell_path(subpath)).resolve()

    return None


def build_alias_resolver(zshrc_text: str) -> dict[str, Path]:
    """Map {alias_name: resolved_cd_target} for aliases we can parse.

    Multiple passes to resolve chains like `games='code;cd games'` after
    `code='cd ~/code'` is already in the map.
    """
    aliases = parse_aliases(zshrc_text)
    resolver: dict[str, Path] = {}
    for _ in range(ALIAS_CHAIN_RESOLVE_PASSES):
        progress = False
        for name, body in aliases:
            if name in resolver:
                continue
            try:
                target = _resolve_one_alias_body(body, resolver)
            except (OSError, ValueError):
                target = None
            if target is not None:
                resolver[name] = target
                progress = True
        if not progress:
            break
    return resolver


def aliases_targeting_cwd(zshrc_path: Path = ZSHRC_PATH, cwd: Path | None = None) -> list[str]:
    """Return alias names whose `cd` target equals cwd.

    Fail-soft: returns [] on missing/unreadable .zshrc.
    """
    cwd_resolved = (cwd or Path.cwd()).resolve()
    try:
        text = zshrc_path.read_text()
    except (FileNotFoundError, OSError):
        return []
    resolver = build_alias_resolver(text)
    return [name for name, target in resolver.items() if target == cwd_resolved]


def find_existing_alias(zshrc_text: str, alias_name: str) -> str | None:
    """Return the existing alias line (without trailing newline) if present."""
    pattern = re.compile(
        rf"^[ \t]*alias[ \t]+{re.escape(alias_name)}=.*$",
        re.MULTILINE,
    )
    match = pattern.search(zshrc_text)
    return match.group(0) if match else None


def insert_alias_line(zshrc_text: str, new_line: str) -> str:
    """Insert `new_line` (no trailing newline) into ~/.zshrc text.

    Anchors after `alias code='cd ~/code'` (or its $HOME variant) when
    present so the new alias clusters with the navigation block. Falls back
    to appending at end of file.
    """
    anchor = CODE_ALIAS_PATTERN.search(zshrc_text)
    if anchor:
        end = anchor.end()
        if end < len(zshrc_text) and zshrc_text[end] == "\n":
            end += 1
        return zshrc_text[:end] + new_line + "\n" + zshrc_text[end:]
    if zshrc_text and not zshrc_text.endswith("\n"):
        zshrc_text += "\n"
    return zshrc_text + new_line + "\n"


def add_alias_to_zshrc(alias_name: str, target: Path, zshrc: Path = ZSHRC_PATH) -> tuple[str, str]:
    """Add `alias <alias_name>=<body>` to ~/.zshrc.

    Returns (status, line) where status is one of:
      - "added":    line was inserted
      - "noop":     identical line already present
      - "conflict": a different `alias <alias_name>=...` exists; left untouched

    Never overwrites an existing conflicting alias.
    """
    existing_text = zshrc.read_text() if zshrc.exists() else ""
    body = alias_body_for_target(target, existing_text)
    new_line = f"alias {alias_name}={body}"
    existing = find_existing_alias(existing_text, alias_name)
    if existing is not None:
        if existing.strip() == new_line.strip():
            return ("noop", existing)
        return ("conflict", existing)
    updated = insert_alias_line(existing_text, new_line)
    zshrc.write_text(updated)
    return ("added", new_line)


def _normalize_hex_color(hex_str: str) -> str:
    """Return canonical `#RRGGBB` uppercase. Raises on malformed input."""
    m = HEX_COLOR_RE.match(hex_str.strip())
    if not m:
        raise GrootProjectTomlError(
            f"color must be #RRGGBB hex; got {hex_str!r}"
        )
    return "#" + m.group(1).upper()


def read_groot_project_iterm(path: Path) -> dict | None:
    """Return the `[iterm]` section as a dict, or None if file/section absent.

    Recognized keys: `color` (required when section present), `alias`, `name`.
    Unknown keys are silently dropped — newer writers can add fields without
    breaking older readers.

    Raises `GrootProjectTomlError` on malformed TOML or wrong-typed values.
    """
    try:
        text = path.read_text()
    except FileNotFoundError:
        return None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise GrootProjectTomlError(f"malformed TOML in {path}: {e}") from e
    iterm = data.get("iterm")
    if iterm is None:
        return None
    if not isinstance(iterm, dict):
        raise GrootProjectTomlError(
            f"[iterm] in {path} must be a table; got {type(iterm).__name__}"
        )
    out: dict = {}
    for key in ITERM_TOML_FIELDS:
        if key not in iterm:
            continue
        value = iterm[key]
        if not isinstance(value, str):
            raise GrootProjectTomlError(
                f"[iterm].{key} in {path} must be a string; got {type(value).__name__}"
            )
        out[key] = value
    return out


def _format_iterm_block(iterm: dict) -> str:
    """Render an [iterm] section. Caller has already validated/normalized values."""
    lines = ["[iterm]"]
    # Stable key order — color first (the always-present field), then optional
    # fields in the same order as ITERM_TOML_FIELDS.
    for key in ITERM_TOML_FIELDS:
        if key in iterm:
            lines.append(f'{key} = "{iterm[key]}"')
    return "\n".join(lines) + "\n"


# Matches a top-level `[section]` line and captures the section name.
_TOML_SECTION_RE = re.compile(r"^\[([^\[\]]+)\]\s*$", re.MULTILINE)


def _splice_iterm_block(existing: str, new_block: str) -> str:
    """Replace an existing [iterm] block in `existing` with `new_block`, or append.

    A "block" runs from `[iterm]` up to (but not including) the next top-level
    `[section]` header, or to end-of-file. Preserves all other sections and any
    leading content (comments, blank lines).
    """
    matches = list(_TOML_SECTION_RE.finditer(existing))
    iterm_match: re.Match | None = None
    next_match: re.Match | None = None
    for i, m in enumerate(matches):
        if m.group(1).strip() == "iterm":
            iterm_match = m
            if i + 1 < len(matches):
                next_match = matches[i + 1]
            break

    if iterm_match is None:
        # Append. Ensure exactly one blank line between previous content and the
        # new section so the file stays readable.
        prefix = existing
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        if prefix and not prefix.endswith("\n\n"):
            prefix += "\n"
        return prefix + new_block

    start = iterm_match.start()
    end = next_match.start() if next_match else len(existing)
    # Preserve a separating blank line between [iterm] and the next section,
    # if there was one.
    block = new_block
    if next_match and not block.endswith("\n\n"):
        block = block.rstrip("\n") + "\n\n"
    return existing[:start] + block + existing[end:]


def write_groot_project_iterm(path: Path, iterm: dict) -> str:
    """Write/merge the `[iterm]` section into `path`. Returns status.

    `iterm` is the *full intended state* of the section, not a patch — fields
    omitted here are dropped from the file. Always includes `color`; `alias`
    and `name` are optional. Color is normalized to canonical `#RRGGBB` upper.

    Other sections in the file are preserved untouched. If the file doesn't
    exist, it's created with a one-line header comment.

    Returns one of: `"written"` (new file), `"updated"` (file existed, content
    changed), `"unchanged"` (file existed, byte-identical after merge).
    """
    if "color" not in iterm:
        raise GrootProjectTomlError("write requires a 'color' field")
    normalized: dict = {"color": _normalize_hex_color(iterm["color"])}
    try:
        if "alias" in iterm:
            validate_alias_name(iterm["alias"])
            normalized["alias"] = iterm["alias"]
        if "name" in iterm:
            validate_profile_name(iterm["name"])
            normalized["name"] = iterm["name"]
    except (InvalidAliasNameError, InvalidProfileNameError) as e:
        raise GrootProjectTomlError(str(e)) from e

    new_block = _format_iterm_block(normalized)

    if not path.exists():
        path.write_text(GROOT_PROJECT_TOML_HEADER + "\n" + new_block)
        return "written"

    existing_text = path.read_text()
    new_text = _splice_iterm_block(existing_text, new_block)
    if new_text == existing_text:
        return "unchanged"
    path.write_text(new_text)
    return "updated"


def _print_iterm_toml(path: Path) -> int:
    """Emit `[iterm]` fields as `KEY=VALUE` lines for the SKILL.md to parse.

    Empty output if file or section absent. Exits 1 with a stderr message on
    a malformed file (so the caller can distinguish absent from corrupt).
    """
    try:
        iterm = read_groot_project_iterm(path)
    except GrootProjectTomlError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if iterm is None:
        return 0
    for key in ITERM_TOML_FIELDS:
        if key in iterm:
            print(f"{key}={iterm[key]}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="iterm-setup",
        description="Create an iTerm2 Dynamic Profile with Automatic Profile Switching for a project.",
    )
    parser.add_argument("name", nargs="?", help="Profile name (default: basename of cwd).")
    parser.add_argument("--color", type=int, metavar="N", help="Palette index (1-based); skips the picker.")
    parser.add_argument("--hex", dest="hex_color", metavar="#RRGGBB", help="Custom hex color; bypasses the palette.")
    parser.add_argument("--pattern", metavar="PAT", help="APS pattern (default: /*/<name>*).")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing profile file.")
    parser.add_argument("--alias", metavar="NAME", help="Add `alias NAME='cd <cwd>'` to ~/.zshrc (idempotent).")
    parser.add_argument("--no-alias", action="store_true", help="Skip the alias step entirely.")
    parser.add_argument("--force-alias", action="store_true", help="Add the alias even if a different alias already targets cwd.")
    parser.add_argument("--title-format", metavar="FORMAT", help=f"iTerm interpolated-string title format (default: {DEFAULT_TITLE_FORMAT!r}).")
    parser.add_argument("--no-title", action="store_true", help="Don't set a custom title format; inherit from the Default profile.")
    parser.add_argument("--list-colors", action="store_true", help="Print palette swatches and exit.")
    parser.add_argument("--vivid", action="store_true", help="Use a fully-vivid main palette (brighter colors, no separate vivid section). For highlight projects.")
    parser.add_argument("--cwd-aliases", action="store_true", help="Print alias names already targeting cwd (one per line) and exit.")
    parser.add_argument(
        "--groot-toml-read",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "Read [iterm] from <DIR>/.groot-project.toml (default cwd) and print "
            "KEY=VALUE lines. Empty output if file/section absent. Exits 0."
        ),
    )
    parser.add_argument(
        "--groot-toml-write",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "Write [iterm] to <DIR>/.groot-project.toml (default cwd) using "
            "--hex (required), --alias (optional), and the positional name "
            "as the iterm.name field if explicitly passed. Standalone — does "
            "not create a profile. Exits 0."
        ),
    )
    parser.add_argument(
        "--groot-toml-write-name",
        action="store_true",
        help=(
            "Used with --groot-toml-write: include the positional `name` arg "
            "as `iterm.name` in the file. Default is to omit it (so the file "
            "stays portable across worktrees with different basenames)."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Print JSON to stdout; do not write profile or .zshrc.")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    if args.cwd_aliases:
        for name in aliases_targeting_cwd():
            print(name)
        return 0

    if args.groot_toml_read is not None:
        return _print_iterm_toml(
            Path(args.groot_toml_read) / GROOT_PROJECT_TOML_NAME
        )

    if args.groot_toml_write is not None:
        if args.hex_color is None:
            raise ItermSetupError(
                "--groot-toml-write requires --hex #RRGGBB (the color to record)."
            )
        # Validate via the existing hex parser; store the canonical form.
        hex_to_rgb(args.hex_color)
        iterm: dict = {"color": args.hex_color}
        if args.alias:
            validate_alias_name(args.alias)
            iterm["alias"] = args.alias
        if args.groot_toml_write_name:
            if not args.name:
                raise ItermSetupError(
                    "--groot-toml-write-name requires the positional name argument."
                )
            iterm["name"] = args.name
        toml_path = Path(args.groot_toml_write) / GROOT_PROJECT_TOML_NAME
        status = write_groot_project_iterm(toml_path, iterm)
        print(f"{status} {toml_path}")
        return 0

    name = args.name or Path.cwd().name
    # In --vivid mode the entire main palette is generated at vivid lightness
    # (no separate section beneath). Otherwise the user gets the stratified
    # main palette plus a small vivid section as bonus picks.
    if args.vivid:
        palette = generate_palette(
            name,
            light_min=VIVID_LIGHTNESS_MIN,
            light_max=VIVID_LIGHTNESS_MAX,
            sat_min=VIVID_SATURATION_MIN,
            sat_max=VIVID_SATURATION_MAX,
            stratify=False,
        )
        vivid_section: list[tuple[str, tuple[float, float, float]]] = []
    else:
        palette = generate_palette(name)
        vivid_section = generate_vivid_palette(name)
    combined_palette = palette + vivid_section
    existing_colors = all_existing_profile_colors()
    existing = existing_profile_info(name)

    if args.list_colors:
        render_palette(name, palette, existing_colors, existing, vivid_section=vivid_section or None)
        return 0

    validate_profile_name(name)
    if args.alias:
        validate_alias_name(args.alias)
    if args.alias and args.no_alias:
        raise ItermSetupError("Pass either --alias NAME or --no-alias, not both.")
    if args.color is not None and args.hex_color is not None:
        raise ItermSetupError("Pass either --color N or --hex #RRGGBB, not both.")
    if args.title_format is not None and args.no_title:
        raise ItermSetupError("Pass either --title-format FORMAT or --no-title, not both.")

    chosen_rgb: tuple[float, float, float]
    chosen_label: str
    if args.hex_color is not None:
        chosen_rgb = hex_to_rgb(args.hex_color)
        h, _, _ = colorsys.rgb_to_hls(*chosen_rgb)
        chosen_label = f"{hue_bucket_name(h * 360.0)} (custom #{args.hex_color.lstrip('#').upper()})"
    elif args.color is not None:
        if not (1 <= args.color <= len(combined_palette)):
            raise InvalidColorIndexError(f"--color must be 1-{len(combined_palette)}; got {args.color}")
        idx = args.color - 1
        chosen_label, chosen_rgb = combined_palette[idx]
    else:
        idx = pick_color_interactive(name, palette, existing_colors, existing, vivid_section=vivid_section or None)
        chosen_label, chosen_rgb = combined_palette[idx]

    # Title format: explicit flag wins; --no-title opts out; otherwise prompt
    # interactively when the color picker was also interactive (so non-interactive
    # invocations like `--color 3 --alias foo` stay quiet and just use the default).
    title_format: str | None
    if args.title_format is not None:
        title_format = args.title_format
    elif args.no_title:
        title_format = None
    elif args.color is None and args.hex_color is None:
        title_format = pick_title_format_interactive()
    else:
        title_format = DEFAULT_TITLE_FORMAT

    if args.pattern:
        pattern = args.pattern
    elif existing is not None and existing.get("pattern"):
        pattern = existing["pattern"]
    else:
        pattern = f"/*/{name}*"
    profile = build_profile(name, chosen_rgb, pattern, title_format)
    rendered = json.dumps(profile, indent=2)

    if args.dry_run:
        print(rendered)
        if args.alias:
            zshrc_text = ZSHRC_PATH.read_text() if ZSHRC_PATH.exists() else ""
            body = alias_body_for_target(Path.cwd(), zshrc_text)
            existing_for_cwd = [a for a in aliases_targeting_cwd() if a != args.alias]
            print(f"\nWould add to ~/.zshrc: alias {args.alias}={body}")
            if existing_for_cwd and not args.force_alias:
                print(
                    f"  ⚠ existing alias(es) already target this cwd: "
                    f"{', '.join(existing_for_cwd)}. Would skip without --force-alias."
                )
        return 0

    DYNAMIC_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DYNAMIC_PROFILES_DIR / f"{name}.json"
    if out_path.exists() and not args.force:
        current = (
            f" (current color: {existing['color_label']})"
            if existing is not None
            else ""
        )
        raise ProfileExistsError(
            f"Profile {name!r} already exists{current}. "
            f"Re-run with --force to change it."
        )

    out_path.write_text(rendered + "\n")
    r, g, b = rgb_float_to_8bit(chosen_rgb)
    print(f"Wrote {out_path}")
    print(f"  Name:    {name}")
    print(f"  Color:   {chosen_label}  #{r:02X}{g:02X}{b:02X}")
    print(f"  APS:     {pattern}")
    if title_format is not None:
        print(f"  Title:   {title_format}")
    else:
        print("  Title:   (inheriting from Default profile)")

    if args.alias:
        existing_for_cwd = [a for a in aliases_targeting_cwd() if a != args.alias]
        if existing_for_cwd and not args.force_alias:
            print(
                f"  Alias:   ⚠ skipped — alias(es) already target this cwd: "
                f"{', '.join(existing_for_cwd)}.\n"
                f"             use one of those, or pass --force-alias to add '{args.alias}' anyway."
            )
        else:
            status, line = add_alias_to_zshrc(args.alias, Path.cwd())
            if status == "added":
                print(f"  Alias:   added to ~/.zshrc → {line}")
                print("           run `source ~/.zshrc` (or open a new shell) to use it.")
            elif status == "noop":
                print(f"  Alias:   already present in ~/.zshrc → {line}")
            elif status == "conflict":
                print(
                    f"  Alias:   ⚠ '{args.alias}' already in ~/.zshrc with a different target:\n"
                    f"             existing: {line}\n"
                    f"             not overwriting. Edit ~/.zshrc by hand to reconcile."
                )

    if not shell_integration_installed():
        print(
            "\nNote: iTerm2 shell integration not detected. APS rules need shell "
            "integration to fire. Install via iTerm2 menu → Install Shell Integration."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        return run(args)
    except ItermSetupError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
