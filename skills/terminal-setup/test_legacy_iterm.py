"""Tests for read_legacy_iterm_profile — the one-time iTerm Dynamic Profile
JSON import path used when /terminal-setup first runs on a project that
has an iTerm-era profile but no .groot-project.toml yet.

Run from the terminal-setup directory:

    python3 -m pytest test_legacy_iterm.py -v
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location(
    "terminal_setup", HERE / "terminal-setup.py"
)
assert SPEC is not None and SPEC.loader is not None
terminal_setup = importlib.util.module_from_spec(SPEC)
sys.modules["terminal_setup"] = terminal_setup
SPEC.loader.exec_module(terminal_setup)

read_legacy_iterm_profile = terminal_setup.read_legacy_iterm_profile


def _write_profile(dir_: Path, name: str, rgb: tuple[float, float, float]) -> Path:
    """Helper: write a Dynamic Profile JSON in the shape iTerm2 expects."""
    r, g, b = rgb
    profile = {
        "Profiles": [
            {
                "Name": name,
                "Guid": f"iterm-setup-{name}",
                "Background Color": {
                    "Red Component": r,
                    "Green Component": g,
                    "Blue Component": b,
                },
            }
        ]
    }
    path = dir_ / f"{name}.json"
    path.write_text(json.dumps(profile))
    return path


def test_returns_none_when_file_absent(tmp_path: Path) -> None:
    assert read_legacy_iterm_profile("anything", profiles_dir=tmp_path) is None


def test_reads_background_as_canonical_hex(tmp_path: Path) -> None:
    _write_profile(tmp_path, "myproj", (0.08, 0.06, 0.20))
    info = read_legacy_iterm_profile("myproj", profiles_dir=tmp_path)
    assert info == {"background": "#140F33"}


def test_handles_pure_black(tmp_path: Path) -> None:
    _write_profile(tmp_path, "myproj", (0.0, 0.0, 0.0))
    info = read_legacy_iterm_profile("myproj", profiles_dir=tmp_path)
    assert info == {"background": "#000000"}


def test_handles_pure_white(tmp_path: Path) -> None:
    _write_profile(tmp_path, "myproj", (1.0, 1.0, 1.0))
    info = read_legacy_iterm_profile("myproj", profiles_dir=tmp_path)
    assert info == {"background": "#FFFFFF"}


def test_returns_none_on_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{not valid json")
    assert read_legacy_iterm_profile("broken", profiles_dir=tmp_path) is None


def test_returns_none_when_profiles_array_missing(tmp_path: Path) -> None:
    (tmp_path / "empty.json").write_text("{}")
    assert read_legacy_iterm_profile("empty", profiles_dir=tmp_path) is None


def test_returns_none_when_profiles_array_empty(tmp_path: Path) -> None:
    (tmp_path / "empty.json").write_text('{"Profiles": []}')
    assert read_legacy_iterm_profile("empty", profiles_dir=tmp_path) is None


def test_returns_none_when_background_components_missing(tmp_path: Path) -> None:
    """Malformed profile (no Background Color or partial) → None, not crash."""
    (tmp_path / "weird.json").write_text(
        '{"Profiles": [{"Name": "weird", "Background Color": {"Red Component": 0.5}}]}'
    )
    assert read_legacy_iterm_profile("weird", profiles_dir=tmp_path) is None


def test_default_profiles_dir_is_iterm2_application_support() -> None:
    """The default path should point at iTerm2's DynamicProfiles directory."""
    expected = (
        Path.home() / "Library" / "Application Support" / "iTerm2" / "DynamicProfiles"
    )
    assert terminal_setup.ITERM_DYNAMIC_PROFILES_DIR == expected


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
