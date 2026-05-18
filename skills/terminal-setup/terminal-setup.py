#!/usr/bin/env python3
"""Per-project terminal background colors + shell alias, terminal-agnostic.

Writes a `[terminal]` section to `<project>/.groot-project.toml` recording the
chosen background color (always) and shell alias (optional). The color takes
effect on `cd` into the project, via the OSC 11 emit in ~/.shrc's chpwd hook
(see hook block "Claude terminal state" in ~/.shrc). Works in iTerm2, Ghostty,
Alacritty, Kitty, WezTerm — anything that honors OSC 11.

The shell alias goes to ~/.shrc when it exists and is sourced by ~/.zshrc or
~/.bashrc (the "shared shell config" convention — aliases that work across
zsh and bash); otherwise falls back to ~/.zshrc.

Color palette: project-seeded random generation. Each project name produces a
deterministic palette of 14 dark, saturated colors with hue spread, named by
hue bucket (Crimson, Forest, Indigo, etc.). Same project always shows the same
palette across runs; different projects get different palettes. A `--hex` flag
bypasses the palette for one-off custom colors.

"In-use" awareness for the picker comes from scanning sibling
`~/code/*/.groot-project.toml` files — the same source of truth that drives
the per-project color, so there's no separate state to drift.
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import random
import re
import sys
import tomllib
from pathlib import Path

DEFAULT_PALETTE_SIZE = 14
VIVID_PALETTE_SIZE = 4

# Hue buckets at 22.5° intervals around the wheel; each generated palette
# entry takes its name from whichever bucket is closest to its hue.
HUE_BUCKETS: list[tuple[float, str]] = [
    (0.0, "Crimson"),
    (22.5, "Vermillion"),
    (45.0, "Rust"),
    (67.5, "Amber"),
    (90.0, "Olive"),
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

ZSHRC_PATH = Path.home() / ".zshrc"
SHRC_PATH = Path.home() / ".shrc"
BASHRC_PATH = Path.home() / ".bashrc"
CODE_DIR = Path.home() / "code"

# Matches `source ~/.shrc` or `. ~/.shrc` (with optional $HOME variant)
# anywhere on a line, ignoring commented-out lines. Permissive on what
# precedes the source statement so we catch common guarded patterns like
# `[ -f ~/.shrc ] && source ~/.shrc` and `if [ -f X ]; then source X; fi`.
# Whole-line comments (`# source ~/.shrc`) are filtered before this regex
# runs; mid-line comments containing a false positive are vanishingly rare
# and we accept the risk.
_SHRC_SOURCE_RE = re.compile(
    r"(?:^|[ \t;&|])(?:source|\.)[ \t]+(?:~/|\$HOME/)\.shrc(?:[ \t]|$|#|;|&|\|)",
    re.MULTILINE,
)

# Per-project workstation-setup file, checked into git so a fresh clone on
# another machine reproduces this project's terminal setup. See
# `read_groot_project_terminal` / `write_groot_project_terminal` for the
# read/write seam and SKILL.md for the prompting flow.
GROOT_PROJECT_TOML_NAME = ".groot-project.toml"
GROOT_PROJECT_TOML_HEADER = (
    "# .groot-project.toml — per-project workstation conventions.\n"
    "# Tracked in git so a fresh clone reproduces this project's setup on a\n"
    "# new machine. Read/written by /terminal-setup (and /groot-project).\n"
)
# Modern key names. Legacy [iterm] with `color` key is still readable; the
# writer always emits [terminal] with `background` and removes any leftover
# [iterm] block.
TERMINAL_TOML_FIELDS = ("background", "alias", "name")
TERMINAL_TOML_SECTION = "terminal"
LEGACY_TOML_SECTION = "iterm"
LEGACY_COLOR_KEY = "color"  # legacy synonym for `background`

VALID_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VALID_ALIAS_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEX_COLOR_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")

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


class TerminalSetupError(RuntimeError):
    pass


# Back-compat alias — anything that still imports the old name keeps working.
ItermSetupError = TerminalSetupError


class InvalidProfileNameError(TerminalSetupError):
    pass


class InvalidAliasNameError(TerminalSetupError):
    pass


class InvalidColorIndexError(TerminalSetupError):
    pass


class InvalidHexColorError(TerminalSetupError):
    pass


class AliasConflictError(TerminalSetupError):
    pass


class AliasTargetCollisionError(TerminalSetupError):
    pass


class GrootProjectTomlError(TerminalSetupError):
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
    mid = (
        (light_min + light_max) / 2
        if stratify and light_max - light_min > 0.05
        else None
    )
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


def all_existing_profile_colors(
    code_dir: Path | None = None,
) -> list[tuple[str, tuple[float, float, float]]]:
    """Return [(project_name, rgb), ...] for every project under ~/code/ that has
    a `.groot-project.toml` recording a background color.

    Source of truth: the git-tracked `.groot-project.toml` at each project root.
    Replaces the old DynamicProfiles-dir scan — same shape of data, but pulled
    from the file the user actually maintains rather than an iTerm side-effect.
    """
    results: list[tuple[str, tuple[float, float, float]]] = []
    root = code_dir or CODE_DIR
    if not root.exists():
        return results
    for toml_path in sorted(root.glob("*/.groot-project.toml")):
        try:
            recorded = read_groot_project_terminal(toml_path)
        except GrootProjectTomlError:
            continue
        if not recorded or "background" not in recorded:
            continue
        try:
            rgb = hex_to_rgb(recorded["background"])
        except InvalidHexColorError:
            continue
        project = toml_path.parent.name
        results.append((project, rgb))
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


def existing_profile_info(name: str, cwd: Path | None = None) -> dict | None:
    """Current RGB/name for this project's recorded background, or None.

    Reads `<cwd>/.groot-project.toml`. If the file is present and its [terminal]
    (or legacy [iterm]) section has a `background` (or `color`), returns a dict
    with the RGB, a human label derived from the hue bucket, and the project name.
    `name` is the proposed name (typically basename of cwd); the returned `name`
    is whatever the TOML recorded if it set one, else `name`.
    """
    project_dir = cwd or Path.cwd()
    path = project_dir / GROOT_PROJECT_TOML_NAME
    try:
        recorded = read_groot_project_terminal(path)
    except GrootProjectTomlError:
        return None
    if not recorded or "background" not in recorded:
        return None
    try:
        rgb = hex_to_rgb(recorded["background"])
    except InvalidHexColorError:
        return None
    h, _, _ = colorsys.rgb_to_hls(*rgb)
    return {
        "name": recorded.get("name", name),
        "rgb": rgb,
        "color_label": hue_bucket_name(h * 360.0),
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
        print(
            "(re-run with --color N --force to change the color, or --hex #RRGGBB --force for a custom one)"
        )

    # Combined palette feeds collision + current-marker detection so markers
    # work whether the existing color sits in the main band or the vivid section.
    combined = palette + (vivid_section or [])
    collisions = palette_collisions(
        combined,
        existing_colors or [],
        exclude_name=existing["name"] if existing else None,
    )
    current_idx = (
        palette_index_near_rgb(combined, existing["rgb"])
        if existing is not None
        else None
    )

    def _render_row(
        i_one_based: int, name: str, rgb: tuple[float, float, float]
    ) -> None:
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
    render_palette(
        name, palette, existing_colors, existing, vivid_section=vivid_section
    )
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
            raw = input(
                f"Pick a color for {name!r} [1-{len(combined)}]{prompt_suffix}: "
            ).strip()
        except EOFError as e:
            raise InvalidColorIndexError(
                "Stdin closed before a color was selected."
            ) from e
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


def _shrc_is_sourced(home: Path) -> bool:
    """True if ~/.zshrc or ~/.bashrc has a live `source ~/.shrc` / `. ~/.shrc` line.

    Commented-out lines don't count. Detection is intentionally conservative —
    if neither rc file sources shrc, treat shrc as inactive even if it exists.
    """
    for rc in (home / ".zshrc", home / ".bashrc"):
        try:
            text = rc.read_text()
        except (FileNotFoundError, OSError):
            continue
        # Strip comment lines before searching so `# source ~/.shrc` doesn't count.
        live_lines = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("#")
        )
        if _SHRC_SOURCE_RE.search(live_lines):
            return True
    return False


def shell_config_files(home: Path | None = None) -> list[Path]:
    """Files where the user's shell aliases live, in read order.

    Includes ~/.shrc first when it exists and is sourced by ~/.zshrc or
    ~/.bashrc (the "shared shell config" convention — aliases that work
    across zsh and bash). Then ~/.zshrc. Filtered to files that actually
    exist. The combined contents form the user's effective alias set.
    """
    home = home or Path.home()
    out: list[Path] = []
    shrc = home / ".shrc"
    if shrc.exists() and _shrc_is_sourced(home):
        out.append(shrc)
    zshrc = home / ".zshrc"
    if zshrc.exists():
        out.append(zshrc)
    return out


def primary_shell_config_file(home: Path | None = None) -> Path:
    """Where new aliases should be written.

    Returns ~/.shrc when it exists and is sourced by ~/.zshrc or ~/.bashrc
    (so the alias is visible across shells). Otherwise ~/.zshrc, even if
    it doesn't exist yet — the caller writes to it.
    """
    home = home or Path.home()
    shrc = home / ".shrc"
    if shrc.exists() and _shrc_is_sourced(home):
        return shrc
    return home / ".zshrc"


def _combined_shell_config_text(home: Path | None = None) -> str:
    """Concatenate all shell_config_files contents in read order (shrc, then zshrc).

    A single newline between files ensures regex-based parsers don't run a
    last-line of one file into the first line of the next.
    """
    chunks: list[str] = []
    for p in shell_config_files(home=home):
        try:
            chunks.append(p.read_text())
        except (FileNotFoundError, OSError):
            continue
    return "\n".join(chunks)


def parse_aliases(zshrc_text: str) -> list[tuple[str, str]]:
    """Return [(alias_name, body), ...] from raw shell-config text.

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


def aliases_targeting_cwd(
    cwd: Path | None = None,
    home: Path | None = None,
) -> list[str]:
    """Return alias names whose `cd` target equals cwd.

    Reads the combined text of all shell_config_files (~/.shrc when sourced,
    plus ~/.zshrc). Fail-soft: returns [] when no shell config exists.
    """
    cwd_resolved = (cwd or Path.cwd()).resolve()
    text = _combined_shell_config_text(home=home)
    if not text:
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


def add_alias_to_shell_config(
    alias_name: str,
    target: Path,
    home: Path | None = None,
) -> tuple[str, str]:
    """Add `alias <alias_name>=<body>` to the primary shell config file.

    The write target is `primary_shell_config_file()` — ~/.shrc when sourced,
    ~/.zshrc otherwise. The conflict check scans the *combined* shell config
    text (both files when shrc is active) so an existing alias in either file
    is detected — we never duplicate.

    Returns (status, line) where status is one of:
      - "added":    line was inserted into the primary file
      - "noop":     identical line already present in some shell config file
      - "conflict": a different `alias <alias_name>=...` exists; left untouched

    Never overwrites an existing conflicting alias.
    """
    primary = primary_shell_config_file(home=home)
    combined_text = _combined_shell_config_text(home=home)
    primary_text = primary.read_text() if primary.exists() else ""

    body = alias_body_for_target(target, combined_text)
    new_line = f"alias {alias_name}={body}"

    existing = find_existing_alias(combined_text, alias_name)
    if existing is not None:
        if existing.strip() == new_line.strip():
            return ("noop", existing)
        return ("conflict", existing)

    updated = insert_alias_line(primary_text, new_line)
    primary.write_text(updated)
    return ("added", new_line)


def _normalize_hex_color(hex_str: str) -> str:
    """Return canonical `#RRGGBB` uppercase. Raises on malformed input."""
    m = HEX_COLOR_RE.match(hex_str.strip())
    if not m:
        raise GrootProjectTomlError(f"color must be #RRGGBB hex; got {hex_str!r}")
    return "#" + m.group(1).upper()


def read_groot_project_terminal(path: Path) -> dict | None:
    """Return the recorded terminal section as a dict, or None if absent.

    Prefers the modern `[terminal]` section. If only the legacy `[iterm]`
    section exists, returns its data with the `color` key translated to
    `background` so callers see a single shape. Unknown keys are silently
    dropped (forward compatibility).

    Returned keys: `background` (when section present), `alias`, `name`.

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

    section_name = TERMINAL_TOML_SECTION
    section = data.get(TERMINAL_TOML_SECTION)
    if section is None:
        section = data.get(LEGACY_TOML_SECTION)
        if section is None:
            return None
        section_name = LEGACY_TOML_SECTION
    if not isinstance(section, dict):
        raise GrootProjectTomlError(
            f"[{section_name}] in {path} must be a table; got {type(section).__name__}"
        )

    out: dict = {}
    if section_name == LEGACY_TOML_SECTION:
        # Translate legacy `color` key to canonical `background` so callers
        # don't need to know which section was used.
        legacy_keys = (LEGACY_COLOR_KEY, "alias", "name")
        for key in legacy_keys:
            if key not in section:
                continue
            value = section[key]
            if not isinstance(value, str):
                raise GrootProjectTomlError(
                    f"[{section_name}].{key} in {path} must be a string; "
                    f"got {type(value).__name__}"
                )
            canonical = "background" if key == LEGACY_COLOR_KEY else key
            out[canonical] = value
        return out

    for key in TERMINAL_TOML_FIELDS:
        if key not in section:
            continue
        value = section[key]
        if not isinstance(value, str):
            raise GrootProjectTomlError(
                f"[{section_name}].{key} in {path} must be a string; "
                f"got {type(value).__name__}"
            )
        out[key] = value
    return out


def _format_terminal_block(terminal: dict) -> str:
    """Render a [terminal] section. Caller has already validated/normalized values."""
    lines = [f"[{TERMINAL_TOML_SECTION}]"]
    for key in TERMINAL_TOML_FIELDS:
        if key in terminal:
            lines.append(f'{key} = "{terminal[key]}"')
    return "\n".join(lines) + "\n"


# Matches a top-level `[section]` line and captures the section name.
_TOML_SECTION_RE = re.compile(r"^\[([^\[\]]+)\]\s*$", re.MULTILINE)


def _splice_terminal_block(existing: str, new_block: str) -> str:
    """Replace the [terminal] block, append if missing, and drop any [iterm] block.

    Migrating away from [iterm] is part of the write contract — if we leave the
    legacy section in place, the next read could find conflicting state. Always
    consolidate to [terminal].

    A "block" runs from its section header up to (but not including) the next
    top-level `[section]` header, or to end-of-file. Other sections are
    preserved verbatim.
    """
    # Drop the legacy [iterm] block first so subsequent edits operate on a
    # consolidated file. Idempotent if [iterm] isn't present.
    existing = _remove_section_block(existing, LEGACY_TOML_SECTION)

    matches = list(_TOML_SECTION_RE.finditer(existing))
    terminal_match: re.Match | None = None
    next_match: re.Match | None = None
    for i, m in enumerate(matches):
        if m.group(1).strip() == TERMINAL_TOML_SECTION:
            terminal_match = m
            if i + 1 < len(matches):
                next_match = matches[i + 1]
            break

    if terminal_match is None:
        # Append. Ensure exactly one blank line between previous content and the
        # new section so the file stays readable.
        prefix = existing
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        if prefix and not prefix.endswith("\n\n"):
            prefix += "\n"
        return prefix + new_block

    start = terminal_match.start()
    end = next_match.start() if next_match else len(existing)
    block = new_block
    if next_match and not block.endswith("\n\n"):
        block = block.rstrip("\n") + "\n\n"
    return existing[:start] + block + existing[end:]


def _remove_section_block(existing: str, section: str) -> str:
    """Remove a `[section]` block (header + body) from the file, if present.

    Used during write to consolidate away the legacy [iterm] block. If the
    section isn't there, returns `existing` unchanged.
    """
    matches = list(_TOML_SECTION_RE.finditer(existing))
    target: re.Match | None = None
    next_match: re.Match | None = None
    for i, m in enumerate(matches):
        if m.group(1).strip() == section:
            target = m
            if i + 1 < len(matches):
                next_match = matches[i + 1]
            break
    if target is None:
        return existing
    start = target.start()
    end = next_match.start() if next_match else len(existing)
    # Also consume any trailing blank line(s) so we don't accumulate them.
    return (
        (existing[:start].rstrip("\n") + "\n\n" + existing[end:]).lstrip("\n")
        if existing[:start].strip()
        else existing[end:].lstrip("\n")
    )


def write_groot_project_terminal(path: Path, terminal: dict) -> str:
    """Write/merge the `[terminal]` section into `path`. Returns status.

    `terminal` is the *full intended state* of the section, not a patch — fields
    omitted here are dropped from the file. Always includes `background`;
    `alias` and `name` are optional. Color is normalized to canonical `#RRGGBB`
    upper. If the file has a legacy `[iterm]` section, the writer removes it
    (silent in-place migration).

    Returns one of: `"written"` (new file), `"updated"` (file existed, content
    changed), `"unchanged"` (file existed, byte-identical after merge).
    """
    if "background" not in terminal:
        raise GrootProjectTomlError("write requires a 'background' field")
    normalized: dict = {"background": _normalize_hex_color(terminal["background"])}
    try:
        if "alias" in terminal:
            validate_alias_name(terminal["alias"])
            normalized["alias"] = terminal["alias"]
        if "name" in terminal:
            validate_profile_name(terminal["name"])
            normalized["name"] = terminal["name"]
    except (InvalidAliasNameError, InvalidProfileNameError) as e:
        raise GrootProjectTomlError(str(e)) from e

    new_block = _format_terminal_block(normalized)

    if not path.exists():
        path.write_text(GROOT_PROJECT_TOML_HEADER + "\n" + new_block)
        return "written"

    existing_text = path.read_text()
    new_text = _splice_terminal_block(existing_text, new_block)
    if new_text == existing_text:
        return "unchanged"
    path.write_text(new_text)
    return "updated"


def migrate_groot_project_toml(path: Path) -> str:
    """Standalone migration: rewrite legacy `[iterm]` as `[terminal]` in place.

    Returns one of:
      - `"migrated"`  — file had [iterm] (no [terminal]) and was rewritten
      - `"already-current"` — file already has [terminal] (or no relevant section)
      - `"no-file"`   — file doesn't exist

    Lossless: every key in [iterm] is preserved under [terminal] with `color`
    renamed to `background`. Other sections in the file are left alone.
    """
    if not path.exists():
        return "no-file"
    try:
        recorded = read_groot_project_terminal(path)
    except GrootProjectTomlError as e:
        raise GrootProjectTomlError(f"{path}: {e}") from e
    # If reader returned nothing, there's no relevant section — nothing to migrate.
    if not recorded:
        return "already-current"
    text = path.read_text()
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise GrootProjectTomlError(f"malformed TOML in {path}: {e}") from e
    if TERMINAL_TOML_SECTION in data:
        # New section already present; the writer would just drop [iterm].
        # Only migrate if [iterm] is actually still present.
        if LEGACY_TOML_SECTION not in data:
            return "already-current"
    # Use the writer to rewrite the file in canonical form. It strips [iterm]
    # and writes [terminal] from the in-memory dict.
    write_groot_project_terminal(path, recorded)
    return "migrated"


# Back-compat aliases for any caller still using the legacy names.
read_groot_project_iterm = read_groot_project_terminal
write_groot_project_iterm = write_groot_project_terminal


def _print_terminal_toml(path: Path) -> int:
    """Emit recorded fields as `KEY=VALUE` lines for the SKILL.md to parse.

    Reads via `read_groot_project_terminal` so legacy `[iterm]` files print
    with the canonical `background` key. Empty output if file or section
    absent. Exits 1 with a stderr message on a malformed file (so the caller
    can distinguish absent from corrupt).
    """
    try:
        terminal = read_groot_project_terminal(path)
    except GrootProjectTomlError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if terminal is None:
        return 0
    for key in TERMINAL_TOML_FIELDS:
        if key in terminal:
            print(f"{key}={terminal[key]}")
    return 0


# Back-compat alias.
_print_iterm_toml = _print_terminal_toml


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="terminal-setup",
        description=(
            "Record a per-project terminal background color (and optional shell "
            "alias) into .groot-project.toml. The shell applies the color via "
            "OSC 11 on cd — terminal-agnostic, no Dynamic Profile JSON."
        ),
    )
    parser.add_argument(
        "name", nargs="?", help="Project name (default: basename of cwd)."
    )
    parser.add_argument(
        "--color",
        type=int,
        metavar="N",
        help="Palette index (1-based); skips the picker.",
    )
    parser.add_argument(
        "--hex",
        dest="hex_color",
        metavar="#RRGGBB",
        help="Custom hex color; bypasses the palette.",
    )
    parser.add_argument(
        "--alias",
        metavar="NAME",
        help="Add `alias NAME='cd <cwd>'` to ~/.shrc (or ~/.zshrc as fallback). Idempotent.",
    )
    parser.add_argument(
        "--no-alias", action="store_true", help="Skip the alias step entirely."
    )
    parser.add_argument(
        "--force-alias",
        action="store_true",
        help="Add the alias even if a different alias already targets cwd.",
    )
    parser.add_argument(
        "--list-colors", action="store_true", help="Print palette swatches and exit."
    )
    parser.add_argument(
        "--vivid",
        action="store_true",
        help="Use a fully-vivid main palette (brighter colors, no separate vivid section). For highlight projects.",
    )
    parser.add_argument(
        "--cwd-aliases",
        action="store_true",
        help="Print alias names already targeting cwd (one per line) and exit.",
    )
    parser.add_argument(
        "--groot-toml-read",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "Read [terminal] from <DIR>/.groot-project.toml (default cwd) and "
            "print KEY=VALUE lines (legacy [iterm] sections are read transparently "
            "with `color` printed as `background`). Empty output if file/section "
            "absent. Exits 0."
        ),
    )
    parser.add_argument(
        "--groot-toml-write",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "Write [terminal] to <DIR>/.groot-project.toml (default cwd) using "
            "--hex (required), --alias (optional), and the positional name as "
            "the terminal.name field if explicitly passed. Removes any legacy "
            "[iterm] block. Standalone — does not run the picker. Exits 0."
        ),
    )
    parser.add_argument(
        "--groot-toml-write-name",
        action="store_true",
        help=(
            "Used with --groot-toml-write: include the positional `name` arg "
            "as `terminal.name` in the file. Default is to omit it (so the file "
            "stays portable across worktrees with different basenames)."
        ),
    )
    parser.add_argument(
        "--migrate-toml",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "Standalone: rewrite a legacy [iterm] section as [terminal] in "
            "<DIR>/.groot-project.toml. Lossless (`color` becomes `background`). "
            "Prints `migrated <path>` / `already-current <path>` / `no-file <path>`. "
            "Useful in a find -exec batch over ~/code."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change; do not write the TOML or shell config.",
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    if args.cwd_aliases:
        for name in aliases_targeting_cwd():
            print(name)
        return 0

    if args.groot_toml_read is not None:
        return _print_terminal_toml(
            Path(args.groot_toml_read) / GROOT_PROJECT_TOML_NAME
        )

    if args.migrate_toml is not None:
        toml_path = Path(args.migrate_toml)
        # Accept either a directory (default: cwd) or a direct path to a TOML.
        if toml_path.is_dir() or not toml_path.name.endswith(".toml"):
            toml_path = toml_path / GROOT_PROJECT_TOML_NAME
        status = migrate_groot_project_toml(toml_path)
        print(f"{status} {toml_path}")
        return 0

    if args.groot_toml_write is not None:
        if args.hex_color is None:
            raise TerminalSetupError(
                "--groot-toml-write requires --hex #RRGGBB (the color to record)."
            )
        # Validate via the existing hex parser; store the canonical form.
        hex_to_rgb(args.hex_color)
        terminal: dict = {"background": args.hex_color}
        if args.alias:
            validate_alias_name(args.alias)
            terminal["alias"] = args.alias
        if args.groot_toml_write_name:
            if not args.name:
                raise TerminalSetupError(
                    "--groot-toml-write-name requires the positional name argument."
                )
            terminal["name"] = args.name
        toml_path = Path(args.groot_toml_write) / GROOT_PROJECT_TOML_NAME
        status = write_groot_project_terminal(toml_path, terminal)
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
        render_palette(
            name,
            palette,
            existing_colors,
            existing,
            vivid_section=vivid_section or None,
        )
        return 0

    validate_profile_name(name)
    if args.alias:
        validate_alias_name(args.alias)
    if args.alias and args.no_alias:
        raise TerminalSetupError("Pass either --alias NAME or --no-alias, not both.")
    if args.color is not None and args.hex_color is not None:
        raise TerminalSetupError("Pass either --color N or --hex #RRGGBB, not both.")

    chosen_rgb: tuple[float, float, float]
    chosen_label: str
    if args.hex_color is not None:
        chosen_rgb = hex_to_rgb(args.hex_color)
        h, _, _ = colorsys.rgb_to_hls(*chosen_rgb)
        chosen_label = f"{hue_bucket_name(h * 360.0)} (custom #{args.hex_color.lstrip('#').upper()})"
    elif args.color is not None:
        if not (1 <= args.color <= len(combined_palette)):
            raise InvalidColorIndexError(
                f"--color must be 1-{len(combined_palette)}; got {args.color}"
            )
        idx = args.color - 1
        chosen_label, chosen_rgb = combined_palette[idx]
    else:
        idx = pick_color_interactive(
            name,
            palette,
            existing_colors,
            existing,
            vivid_section=vivid_section or None,
        )
        chosen_label, chosen_rgb = combined_palette[idx]

    r, g, b = rgb_float_to_8bit(chosen_rgb)
    chosen_hex = f"#{r:02X}{g:02X}{b:02X}"
    toml_path = Path.cwd() / GROOT_PROJECT_TOML_NAME

    if args.dry_run:
        print(f"Would write {toml_path}")
        print(f"  Name:        {name}")
        print(f"  Background:  {chosen_label}  {chosen_hex}")
        if args.alias:
            combined_text = _combined_shell_config_text()
            body = alias_body_for_target(Path.cwd(), combined_text)
            primary = primary_shell_config_file()
            existing_for_cwd = [a for a in aliases_targeting_cwd() if a != args.alias]
            print(f"  Would add to {primary}: alias {args.alias}={body}")
            if existing_for_cwd and not args.force_alias:
                print(
                    f"  ⚠ existing alias(es) already target this cwd: "
                    f"{', '.join(existing_for_cwd)}. Would skip without --force-alias."
                )
        return 0

    # Write .groot-project.toml — this is the single source of truth. The
    # shell's chpwd hook reads it on `cd` and emits OSC 11 to apply the color.
    terminal_data: dict = {"background": chosen_hex}
    if args.alias and not args.no_alias:
        terminal_data["alias"] = args.alias
    toml_status = write_groot_project_terminal(toml_path, terminal_data)
    print(f"{toml_status} {toml_path}")
    print(f"  Name:        {name}")
    print(f"  Background:  {chosen_label}  {chosen_hex}")

    if args.alias and not args.no_alias:
        existing_for_cwd = [a for a in aliases_targeting_cwd() if a != args.alias]
        if existing_for_cwd and not args.force_alias:
            print(
                f"  Alias:       ⚠ skipped — alias(es) already target this cwd: "
                f"{', '.join(existing_for_cwd)}.\n"
                f"               use one of those, or pass --force-alias to add '{args.alias}' anyway."
            )
        else:
            primary = primary_shell_config_file()
            status, line = add_alias_to_shell_config(args.alias, Path.cwd())
            if status == "added":
                print(f"  Alias:       added to {primary} → {line}")
                print(
                    f"               run `source {primary}` (or open a new shell) to use it."
                )
            elif status == "noop":
                print(f"  Alias:       already present in shell config → {line}")
            elif status == "conflict":
                print(
                    f"  Alias:       ⚠ '{args.alias}' already in shell config with a different target:\n"
                    f"               existing: {line}\n"
                    f"               not overwriting. Edit the shell config by hand to reconcile."
                )

    print(
        "\nOpen a new tab in this directory, or `cd .` from a current shell, "
        "to apply the background color."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        return run(args)
    except TerminalSetupError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
