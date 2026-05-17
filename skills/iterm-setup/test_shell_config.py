"""Tests for shell-config discovery in iterm-setup.py.

Covers the .shrc-aware read/write paths: shell_config_files() discovery,
primary_shell_config_file() selection, aliases_targeting_cwd() reading
from multiple files, and add_alias_to_shell_config() writing to the
discovered primary.

The functions accept an optional `home` parameter (defaulting to Path.home())
so tests can point at a tmp_path-rooted fake HOME without monkeypatching.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("iterm_setup", HERE / "iterm-setup.py")
assert SPEC is not None and SPEC.loader is not None
iterm_setup = importlib.util.module_from_spec(SPEC)
sys.modules["iterm_setup"] = iterm_setup
SPEC.loader.exec_module(iterm_setup)

shell_config_files = iterm_setup.shell_config_files
primary_shell_config_file = iterm_setup.primary_shell_config_file
aliases_targeting_cwd = iterm_setup.aliases_targeting_cwd
add_alias_to_shell_config = iterm_setup.add_alias_to_shell_config


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_discovery_zshrc_only(fake_home: Path) -> None:
    _write(fake_home / ".zshrc", "alias x='cd /tmp'\n")
    assert shell_config_files(home=fake_home) == [fake_home / ".zshrc"]
    assert primary_shell_config_file(home=fake_home) == fake_home / ".zshrc"


def test_discovery_shrc_present_but_not_sourced_falls_back_to_zshrc(
    fake_home: Path,
) -> None:
    """Stale ~/.shrc that no rc file sources shouldn't be the primary write target."""
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".zshrc", "# no source line\nalias y='cd /var'\n")
    assert shell_config_files(home=fake_home) == [fake_home / ".zshrc"]
    assert primary_shell_config_file(home=fake_home) == fake_home / ".zshrc"


def test_discovery_shrc_sourced_by_zshrc(fake_home: Path) -> None:
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    files = shell_config_files(home=fake_home)
    assert files == [fake_home / ".shrc", fake_home / ".zshrc"]
    assert primary_shell_config_file(home=fake_home) == fake_home / ".shrc"


def test_discovery_recognizes_dot_source_form(fake_home: Path) -> None:
    """`. ~/.shrc` (POSIX `.` builtin) counts the same as `source ~/.shrc`."""
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".bashrc", ". ~/.shrc\n")
    assert primary_shell_config_file(home=fake_home) == fake_home / ".shrc"


def test_discovery_recognizes_home_var_form(fake_home: Path) -> None:
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".zshrc", "source $HOME/.shrc\n")
    assert primary_shell_config_file(home=fake_home) == fake_home / ".shrc"


def test_discovery_recognizes_guarded_source_line(fake_home: Path) -> None:
    """`[ -f ~/.shrc ] && source ~/.shrc` is a common defensive pattern."""
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".zshrc", "[ -f ~/.shrc ] && source ~/.shrc\n")
    assert primary_shell_config_file(home=fake_home) == fake_home / ".shrc"


def test_discovery_recognizes_if_then_source(fake_home: Path) -> None:
    """`if [ -f ~/.shrc ]; then source ~/.shrc; fi` — another defensive form."""
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(
        fake_home / ".bashrc",
        "if [ -f ~/.shrc ]; then source ~/.shrc; fi\n",
    )
    assert primary_shell_config_file(home=fake_home) == fake_home / ".shrc"


def test_discovery_skips_commented_source_line(fake_home: Path) -> None:
    """A commented-out source line shouldn't activate shrc as primary."""
    _write(fake_home / ".shrc", "alias x='cd /tmp'\n")
    _write(fake_home / ".zshrc", "# source ~/.shrc\n")
    assert primary_shell_config_file(home=fake_home) == fake_home / ".zshrc"


def test_aliases_targeting_cwd_reads_from_shrc(
    fake_home: Path, tmp_path: Path
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    _write(fake_home / ".shrc", f"alias proj='cd {target}'\n")
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    assert aliases_targeting_cwd(cwd=target, home=fake_home) == ["proj"]


def test_aliases_targeting_cwd_combines_both_files(
    fake_home: Path, tmp_path: Path
) -> None:
    """Aliases from .shrc and .zshrc both contribute to the user's effective set."""
    target = tmp_path / "proj"
    target.mkdir()
    _write(fake_home / ".shrc", f"alias one='cd {target}'\n")
    _write(
        fake_home / ".zshrc",
        f"source ~/.shrc\nalias two='cd {target}'\n",
    )
    assert sorted(aliases_targeting_cwd(cwd=target, home=fake_home)) == ["one", "two"]


def test_aliases_targeting_cwd_resolves_chain_anchored_in_shrc(
    fake_home: Path, tmp_path: Path
) -> None:
    """A `code` alias in .shrc should let chained aliases (`proj='code;cd X'`) resolve.

    Uses an absolute path for the `code` alias rather than `~/code` because
    `~` expands to the real Path.home() (not fake_home) — the test isolates
    the chain mechanism, not tilde expansion (which is exercised in production
    by `_resolve_one_alias_body`).
    """
    code_dir = tmp_path / "code-tree"
    project = code_dir / "proj"
    project.mkdir(parents=True)
    _write(
        fake_home / ".shrc",
        f"alias code='cd {code_dir}'\nalias proj='code;cd proj'\n",
    )
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    assert aliases_targeting_cwd(cwd=project, home=fake_home) == ["proj"]


def test_add_alias_writes_to_shrc_when_primary(
    fake_home: Path, tmp_path: Path
) -> None:
    _write(fake_home / ".shrc", "# existing comment\n")
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    target = tmp_path / "proj"
    target.mkdir()
    status, line = add_alias_to_shell_config("proj", target, home=fake_home)
    assert status == "added"
    shrc_text = (fake_home / ".shrc").read_text()
    zshrc_text = (fake_home / ".zshrc").read_text()
    assert "alias proj=" in shrc_text, "Should have written to .shrc"
    assert "alias proj=" not in zshrc_text, "Should NOT have written to .zshrc"
    assert line in shrc_text


def test_add_alias_writes_to_zshrc_when_no_shrc(
    fake_home: Path, tmp_path: Path
) -> None:
    _write(fake_home / ".zshrc", "# existing zshrc\n")
    target = tmp_path / "proj"
    target.mkdir()
    status, _ = add_alias_to_shell_config("proj", target, home=fake_home)
    assert status == "added"
    assert "alias proj=" in (fake_home / ".zshrc").read_text()


def test_add_alias_noop_when_already_present_in_any_file(
    fake_home: Path, tmp_path: Path
) -> None:
    """If the exact same alias already exists in .shrc or .zshrc, don't duplicate."""
    target = tmp_path / "proj"
    target.mkdir()
    _write(fake_home / ".shrc", f"alias proj='cd {target}'\n")
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    status, line = add_alias_to_shell_config("proj", target, home=fake_home)
    assert status == "noop", f"expected noop, got {status} ({line!r})"


def test_add_alias_conflict_when_different_alias_exists(
    fake_home: Path, tmp_path: Path
) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    _write(fake_home / ".shrc", "alias proj='cd /elsewhere'\n")
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    status, _ = add_alias_to_shell_config("proj", target, home=fake_home)
    assert status == "conflict"
    # File untouched.
    assert (fake_home / ".shrc").read_text() == "alias proj='cd /elsewhere'\n"


def test_add_alias_anchors_after_code_alias_in_primary_file(
    fake_home: Path, tmp_path: Path
) -> None:
    """When the primary file has `alias code='cd ~/code'`, new aliases anchor after it."""
    _write(
        fake_home / ".shrc",
        "# header\n\nalias code='cd ~/code'\nalias other='cd /var'\n",
    )
    _write(fake_home / ".zshrc", "source ~/.shrc\n")
    target = fake_home / "code" / "proj"
    target.mkdir(parents=True)
    add_alias_to_shell_config("proj", target, home=fake_home)
    text = (fake_home / ".shrc").read_text()
    code_idx = text.index("alias code=")
    proj_idx = text.index("alias proj=")
    other_idx = text.index("alias other=")
    assert code_idx < proj_idx < other_idx, (
        f"proj should sit between code and other; got positions "
        f"code={code_idx} proj={proj_idx} other={other_idx}\n{text}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
