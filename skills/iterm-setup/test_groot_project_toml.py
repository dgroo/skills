"""Tests for .groot-project.toml read/write helpers in iterm-setup.py.

Run from the iterm-setup directory:

    python3 -m pytest test_groot_project_toml.py -v

or directly:

    python3 test_groot_project_toml.py
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("iterm_setup", HERE / "iterm-setup.py")
assert SPEC is not None and SPEC.loader is not None
iterm_setup = importlib.util.module_from_spec(SPEC)
sys.modules["iterm_setup"] = iterm_setup
SPEC.loader.exec_module(iterm_setup)

read_groot_project_iterm = iterm_setup.read_groot_project_iterm
write_groot_project_iterm = iterm_setup.write_groot_project_iterm
GrootProjectTomlError = iterm_setup.GrootProjectTomlError


def test_read_returns_none_when_file_absent(tmp_path: Path) -> None:
    assert read_groot_project_iterm(tmp_path / ".groot-project.toml") is None


def test_read_returns_none_when_file_lacks_iterm_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[other]\nkey = "value"\n')
    assert read_groot_project_iterm(path) is None


def test_read_parses_minimal_iterm_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[iterm]\ncolor = "#3a5f2c"\n')
    assert read_groot_project_iterm(path) == {"color": "#3a5f2c"}


def test_read_parses_all_iterm_fields(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#3a5f2c"
            alias = "mp"
            name = "myproject"
        """).lstrip()
    )
    assert read_groot_project_iterm(path) == {
        "color": "#3a5f2c",
        "alias": "mp",
        "name": "myproject",
    }


def test_read_ignores_unrelated_sections(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [other]
            stuff = "ignored"

            [iterm]
            color = "#abcdef"

            [editor]
            theme = "dark"
        """).lstrip()
    )
    assert read_groot_project_iterm(path) == {"color": "#abcdef"}


def test_read_raises_on_malformed_toml(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text("[iterm\ncolor = bogus\n")
    with pytest.raises(GrootProjectTomlError):
        read_groot_project_iterm(path)


def test_read_raises_when_color_not_string(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text("[iterm]\ncolor = 42\n")
    with pytest.raises(GrootProjectTomlError):
        read_groot_project_iterm(path)


def test_read_ignores_unknown_iterm_keys(tmp_path: Path) -> None:
    """Forward compatibility: unknown keys in [iterm] are silently dropped."""
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        '[iterm]\ncolor = "#3a5f2c"\nfuture_key = "from a newer version"\n'
    )
    assert read_groot_project_iterm(path) == {"color": "#3a5f2c"}


def test_write_creates_new_file_color_only(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    status = write_groot_project_iterm(path, {"color": "#3a5f2c"})
    assert status == "written"
    assert path.exists()
    content = path.read_text()
    assert "[iterm]" in content
    assert 'color = "#3A5F2C"' in content  # normalized to uppercase
    assert read_groot_project_iterm(path) == {"color": "#3A5F2C"}


def test_write_creates_new_file_all_fields(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(
        path, {"color": "#3a5f2c", "alias": "mp", "name": "myproject"}
    )
    assert read_groot_project_iterm(path) == {
        "color": "#3A5F2C",  # normalized to uppercase
        "alias": "mp",
        "name": "myproject",
    }


def test_write_includes_header_comment_on_create(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#3a5f2c"})
    content = path.read_text()
    assert content.startswith("#"), (
        "New file should lead with a header comment explaining purpose"
    )


def test_write_unchanged_returns_unchanged_status(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#3a5f2c"})
    before = path.read_text()
    status = write_groot_project_iterm(path, {"color": "#3a5f2c"})
    assert status == "unchanged"
    assert path.read_text() == before


def test_write_updates_existing_color(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#111111"})
    status = write_groot_project_iterm(path, {"color": "#222222"})
    assert status == "updated"
    assert read_groot_project_iterm(path) == {"color": "#222222"}


def test_write_adds_alias_to_existing_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#111111"})
    status = write_groot_project_iterm(path, {"color": "#111111", "alias": "mp"})
    assert status == "updated"
    assert read_groot_project_iterm(path) == {"color": "#111111", "alias": "mp"}


def test_write_preserves_other_sections(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            # Hand-written file with multiple sections.

            [editor]
            theme = "dark"
            tab_width = 4

            [direnv]
            allowed = true
        """).lstrip()
    )
    write_groot_project_iterm(path, {"color": "#3a5f2c"})
    content = path.read_text()
    assert "[editor]" in content
    assert 'theme = "dark"' in content
    assert "tab_width = 4" in content
    assert "[direnv]" in content
    assert "allowed = true" in content
    assert 'color = "#3A5F2C"' in content


def test_write_merges_into_existing_iterm_section_preserving_other_sections(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#111111"
            alias = "old"

            [editor]
            theme = "dark"
        """).lstrip()
    )
    write_groot_project_iterm(path, {"color": "#222222", "alias": "new"})
    assert read_groot_project_iterm(path) == {"color": "#222222", "alias": "new"}
    content = path.read_text()
    assert "[editor]" in content
    assert 'theme = "dark"' in content


def test_write_removes_optional_field_when_omitted(tmp_path: Path) -> None:
    """Writing without `alias` removes a previously-stored alias.

    Rationale: the write function reflects the intended state, not a partial
    patch. Callers that want to preserve fields must include them.
    """
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#111111", "alias": "mp"})
    write_groot_project_iterm(path, {"color": "#111111"})
    assert read_groot_project_iterm(path) == {"color": "#111111"}


def test_write_rejects_missing_color(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_iterm(path, {"alias": "mp"})


def test_write_rejects_invalid_color(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_iterm(path, {"color": "not-a-hex"})


def test_write_normalizes_color_to_uppercase_hex(tmp_path: Path) -> None:
    """Stored as `#RRGGBB` with uppercase digits for consistency."""
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "#3a5f2c"})
    assert read_groot_project_iterm(path) == {"color": "#3A5F2C"}


def test_write_accepts_color_without_leading_hash(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_iterm(path, {"color": "3a5f2c"})
    assert read_groot_project_iterm(path) == {"color": "#3A5F2C"}


def test_write_rejects_invalid_alias(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_iterm(path, {"color": "#3a5f2c", "alias": "bad alias"})


def test_write_rejects_invalid_name(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_iterm(path, {"color": "#3a5f2c", "name": "bad name"})


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
