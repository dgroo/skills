"""Tests for .groot-project.toml read/write helpers in terminal-setup.py.

Run from the terminal-setup directory:

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
SPEC = importlib.util.spec_from_file_location(
    "terminal_setup", HERE / "terminal-setup.py"
)
assert SPEC is not None and SPEC.loader is not None
terminal_setup = importlib.util.module_from_spec(SPEC)
sys.modules["terminal_setup"] = terminal_setup
SPEC.loader.exec_module(terminal_setup)

read_groot_project_terminal = terminal_setup.read_groot_project_terminal
write_groot_project_terminal = terminal_setup.write_groot_project_terminal
migrate_groot_project_toml = terminal_setup.migrate_groot_project_toml
GrootProjectTomlError = terminal_setup.GrootProjectTomlError


# --- Read: modern [terminal] section ----------------------------------------


def test_read_returns_none_when_file_absent(tmp_path: Path) -> None:
    assert read_groot_project_terminal(tmp_path / ".groot-project.toml") is None


def test_read_returns_none_when_file_lacks_known_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[other]\nkey = "value"\n')
    assert read_groot_project_terminal(path) is None


def test_read_parses_minimal_terminal_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[terminal]\nbackground = "#3a5f2c"\n')
    assert read_groot_project_terminal(path) == {"background": "#3a5f2c"}


def test_read_parses_all_terminal_fields(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [terminal]
            background = "#3a5f2c"
            alias = "mp"
            name = "myproject"
        """).lstrip()
    )
    assert read_groot_project_terminal(path) == {
        "background": "#3a5f2c",
        "alias": "mp",
        "name": "myproject",
    }


def test_read_ignores_unrelated_sections(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [editor]
            theme = "dark"

            [terminal]
            background = "#abcdef"
        """).lstrip()
    )
    assert read_groot_project_terminal(path) == {"background": "#abcdef"}


def test_read_raises_on_malformed_toml(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text("not = valid = toml\n")
    with pytest.raises(GrootProjectTomlError):
        read_groot_project_terminal(path)


def test_read_raises_when_background_not_string(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text("[terminal]\nbackground = 42\n")
    with pytest.raises(GrootProjectTomlError):
        read_groot_project_terminal(path)


def test_read_ignores_unknown_keys(tmp_path: Path) -> None:
    """Forward compatibility: unknown keys in [terminal] are silently dropped."""
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        '[terminal]\nbackground = "#3a5f2c"\nfuture_key = "from a newer version"\n'
    )
    assert read_groot_project_terminal(path) == {"background": "#3a5f2c"}


# --- Read: legacy [iterm] back-compat ---------------------------------------


def test_read_falls_back_to_legacy_iterm_section(tmp_path: Path) -> None:
    """Old TOMLs with [iterm].color should read as [terminal].background."""
    path = tmp_path / ".groot-project.toml"
    path.write_text('[iterm]\ncolor = "#280f8c"\n')
    assert read_groot_project_terminal(path) == {"background": "#280f8c"}


def test_read_translates_all_legacy_keys(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#280f8c"
            alias = "skills"
            name = "myproject"
        """).lstrip()
    )
    assert read_groot_project_terminal(path) == {
        "background": "#280f8c",
        "alias": "skills",
        "name": "myproject",
    }


def test_read_terminal_wins_over_legacy_iterm_when_both_present(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#111111"

            [terminal]
            background = "#222222"
        """).lstrip()
    )
    assert read_groot_project_terminal(path) == {"background": "#222222"}


# --- Write: new file --------------------------------------------------------


def test_write_creates_new_file_background_only(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    status = write_groot_project_terminal(path, {"background": "#3a5f2c"})
    assert status == "written"
    content = path.read_text()
    assert "[terminal]" in content
    assert 'background = "#3A5F2C"' in content
    assert read_groot_project_terminal(path) == {"background": "#3A5F2C"}


def test_write_creates_new_file_all_fields(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(
        path, {"background": "#3a5f2c", "alias": "mp", "name": "myproject"}
    )
    assert read_groot_project_terminal(path) == {
        "background": "#3A5F2C",  # normalized to uppercase
        "alias": "mp",
        "name": "myproject",
    }


def test_write_includes_header_comment_on_create(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#3a5f2c"})
    content = path.read_text()
    assert content.startswith("# .groot-project.toml")


# --- Write: idempotency + updates -------------------------------------------


def test_write_unchanged_returns_unchanged_status(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#3a5f2c"})
    status = write_groot_project_terminal(path, {"background": "#3a5f2c"})
    assert status == "unchanged"


def test_write_updates_existing_background(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#111111"})
    status = write_groot_project_terminal(path, {"background": "#222222"})
    assert status == "updated"
    assert read_groot_project_terminal(path) == {"background": "#222222"}


def test_write_adds_alias_to_existing_section(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#111111"})
    status = write_groot_project_terminal(
        path, {"background": "#111111", "alias": "mp"}
    )
    assert status == "updated"
    assert read_groot_project_terminal(path) == {"background": "#111111", "alias": "mp"}


def test_write_preserves_other_sections(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [editor]
            theme = "dark"

            [build]
            target = "release"
        """).lstrip()
    )
    write_groot_project_terminal(path, {"background": "#3a5f2c"})
    content = path.read_text()
    assert "[editor]" in content
    assert 'theme = "dark"' in content
    assert "[build]" in content


def test_write_merges_into_existing_terminal_section_preserving_others(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [terminal]
            background = "#111111"
            alias = "old"

            [editor]
            theme = "dark"
        """).lstrip()
    )
    write_groot_project_terminal(path, {"background": "#222222", "alias": "new"})
    assert read_groot_project_terminal(path) == {
        "background": "#222222",
        "alias": "new",
    }
    content = path.read_text()
    assert "[editor]" in content
    assert 'theme = "dark"' in content


def test_write_removes_optional_field_when_omitted(tmp_path: Path) -> None:
    """Writing without `alias` removes a previously-stored alias.

    Rationale: the write function reflects the intended state, not a partial
    patch. Callers that want to preserve fields must include them.
    """
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#111111", "alias": "mp"})
    write_groot_project_terminal(path, {"background": "#111111"})
    assert read_groot_project_terminal(path) == {"background": "#111111"}


# --- Write: migration away from [iterm] -------------------------------------


def test_write_drops_legacy_iterm_block(tmp_path: Path) -> None:
    """Old [iterm] should be removed when writing the new [terminal]."""
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#111111"
            alias = "old"
        """).lstrip()
    )
    write_groot_project_terminal(path, {"background": "#222222"})
    content = path.read_text()
    assert "[iterm]" not in content
    assert "[terminal]" in content
    assert read_groot_project_terminal(path) == {"background": "#222222"}


def test_write_drops_legacy_iterm_block_preserving_other_sections(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#111111"

            [editor]
            theme = "dark"
        """).lstrip()
    )
    write_groot_project_terminal(path, {"background": "#222222"})
    content = path.read_text()
    assert "[iterm]" not in content
    assert "[editor]" in content
    assert 'theme = "dark"' in content


# --- Write: validation ------------------------------------------------------


def test_write_rejects_missing_background(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_terminal(path, {"alias": "mp"})


def test_write_rejects_invalid_background(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_terminal(path, {"background": "not-a-hex"})


def test_write_normalizes_color_to_uppercase_hex(tmp_path: Path) -> None:
    """Stored as `#RRGGBB` with uppercase digits for consistency."""
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#3a5f2c"})
    assert read_groot_project_terminal(path) == {"background": "#3A5F2C"}


def test_write_accepts_color_without_leading_hash(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "3a5f2c"})
    assert read_groot_project_terminal(path) == {"background": "#3A5F2C"}


def test_write_rejects_invalid_alias(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_terminal(
            path, {"background": "#3a5f2c", "alias": "bad alias"}
        )


def test_write_rejects_invalid_name(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    with pytest.raises(GrootProjectTomlError):
        write_groot_project_terminal(
            path, {"background": "#3a5f2c", "name": "bad name"}
        )


# --- migrate_groot_project_toml --------------------------------------------


def test_migrate_no_file_returns_no_file(tmp_path: Path) -> None:
    assert migrate_groot_project_toml(tmp_path / ".groot-project.toml") == "no-file"


def test_migrate_legacy_iterm_file_returns_migrated(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[iterm]\ncolor = "#3a5f2c"\nalias = "mp"\n')
    assert migrate_groot_project_toml(path) == "migrated"
    content = path.read_text()
    assert "[terminal]" in content
    assert "[iterm]" not in content
    assert read_groot_project_terminal(path) == {
        "background": "#3A5F2C",
        "alias": "mp",
    }


def test_migrate_modern_file_returns_already_current(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    write_groot_project_terminal(path, {"background": "#3a5f2c"})
    assert migrate_groot_project_toml(path) == "already-current"


def test_migrate_file_with_no_relevant_section_returns_already_current(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text('[other]\nkey = "value"\n')
    assert migrate_groot_project_toml(path) == "already-current"


def test_migrate_is_lossless_for_all_keys(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#3a5f2c"
            alias = "mp"
            name = "myproject"
        """).lstrip()
    )
    migrate_groot_project_toml(path)
    assert read_groot_project_terminal(path) == {
        "background": "#3A5F2C",
        "alias": "mp",
        "name": "myproject",
    }


def test_migrate_preserves_other_sections(tmp_path: Path) -> None:
    path = tmp_path / ".groot-project.toml"
    path.write_text(
        textwrap.dedent("""
            [iterm]
            color = "#111111"

            [editor]
            theme = "dark"
        """).lstrip()
    )
    migrate_groot_project_toml(path)
    content = path.read_text()
    assert "[editor]" in content
    assert 'theme = "dark"' in content
    assert "[iterm]" not in content


# --- Back-compat: old API names still resolve --------------------------------


def test_legacy_function_names_alias_to_new_ones() -> None:
    """Anything importing read_groot_project_iterm / write_groot_project_iterm
    keeps working — same callable as the new name."""
    assert terminal_setup.read_groot_project_iterm is read_groot_project_terminal
    assert terminal_setup.write_groot_project_iterm is write_groot_project_terminal


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
