#!/usr/bin/env bash
# List Claude Code skills, grouped by source.
#
# Usage:
#   skill-list.sh           # default: same as `make list` (mine + install status)
#   skill-list.sh all       # every group, prefixed
#   skill-list.sh groups    # list available groups
#   skill-list.sh <group>   # mine | gstack | installed | plugins | upstream
set -euo pipefail

REPO_DIR="${SKILL_LIST_REPO_DIR:-$HOME/code/claude/skills}"
MINE_DIR="$REPO_DIR/skills"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
PLUGINS_CACHE_DIR="$HOME/.claude/plugins/cache"

arg="${1:-}"

# Extract `description:` from a SKILL.md.
desc_of() {
    local skill_md="$1"
    [ -f "$skill_md" ] || { echo "(no SKILL.md)"; return; }
    awk '
        /^description:[[:space:]]*\|/ { collect=1; next }
        collect && /^[[:space:]]+/ { sub(/^[[:space:]]+/, ""); print; exit }
        /^description:/ { sub(/^description:[[:space:]]*/, ""); print; exit }
    ' "$skill_md"
}

list_mine() {
    [ -d "$MINE_DIR" ] || { echo "  (no $MINE_DIR)"; return; }
    for skill in "$MINE_DIR"/*/; do
        [ -d "$skill" ] || continue
        name=$(basename "$skill")
        desc=$(desc_of "$skill/SKILL.md")
        printf "  %-30s — %s\n" "$name" "$desc"
    done
}

list_gstack() {
    local gstack_dir="$CLAUDE_SKILLS_DIR/gstack"
    [ -d "$gstack_dir" ] || { echo "  (no $gstack_dir)"; return; }
    for skill in "$gstack_dir"/*/; do
        [ -d "$skill" ] || continue
        [ -f "$skill/SKILL.md" ] || continue
        name=$(basename "$skill")
        desc=$(desc_of "$skill/SKILL.md")
        printf "  %-30s — %s\n" "$name" "$desc"
    done
}

# Direct entries under ~/.claude/skills that are real dirs, not symlinks,
# and not the gstack catalog dir.
list_installed() {
    [ -d "$CLAUDE_SKILLS_DIR" ] || { echo "  (no $CLAUDE_SKILLS_DIR)"; return; }
    for skill in "$CLAUDE_SKILLS_DIR"/*/; do
        [ -d "$skill" ] || continue
        name=$(basename "$skill")
        [ "$name" = "gstack" ] && continue
        [ -L "${skill%/}" ] && continue
        [ -f "$skill/SKILL.md" ] || continue
        desc=$(desc_of "$skill/SKILL.md")
        printf "  %-30s — %s\n" "$name" "$desc"
    done
}

list_plugins() {
    [ -d "$PLUGINS_CACHE_DIR" ] || { echo "  (no $PLUGINS_CACHE_DIR)"; return; }
    # Layout: cache/<marketplace>/<plugin>/<version>/skills/<skill>/SKILL.md
    for marketplace in "$PLUGINS_CACHE_DIR"/*/; do
        [ -d "$marketplace" ] || continue
        for plugin in "$marketplace"*/; do
            [ -d "$plugin" ] || continue
            plugin_name=$(basename "$plugin")
            # Plugins can have multiple versions cached; show only the latest
            # (last after sort -V on the version dir basename).
            latest_version=""
            for version_dir in "$plugin"*/; do
                [ -d "$version_dir" ] || continue
                latest_version="$version_dir"
            done
            [ -n "$latest_version" ] || continue
            # If multiple version dirs exist, pick the highest by version sort.
            mapfile -t version_dirs < <(find "$plugin" -mindepth 1 -maxdepth 1 -type d | sort -V)
            latest_version="${version_dirs[-1]}/"
            skills_dir="$latest_version/skills"
            [ -d "$skills_dir" ] || continue
            for skill in "$skills_dir"/*/; do
                [ -d "$skill" ] || continue
                [ -f "$skill/SKILL.md" ] || continue
                name=$(basename "$skill")
                desc=$(desc_of "$skill/SKILL.md")
                printf "  %-40s — %s\n" "$plugin_name:$name" "$desc"
            done
        done
    done
}

list_upstream() {
    if ! git -C "$REPO_DIR" rev-parse --git-dir >/dev/null 2>&1; then
        echo "  (not a git repo at $REPO_DIR)"
        return
    fi
    git -C "$REPO_DIR" ls-tree -r --name-only upstream/main 2>/dev/null \
        | awk -F/ '$1 == "skills" && NF >= 2 { print $2 }' \
        | sort -u \
        | sed 's/^/  /' \
        || echo "  (no upstream remote — see 'git remote -v')"
}

list_default() {
    echo "Skills in this repo:"
    list_mine
    echo ""
    echo "Installed symlinks in $CLAUDE_SKILLS_DIR:"
    for skill in "$MINE_DIR"/*/; do
        [ -d "$skill" ] || continue
        name=$(basename "$skill")
        target="$CLAUDE_SKILLS_DIR/$name"
        if [ -L "$target" ] && [ "$(readlink "$target")" = "${skill%/}" ]; then
            echo "  ✓ $name"
        elif [ -e "$target" ]; then
            echo "  ✗ $name (exists, not our link)"
        else
            echo "  - $name (not installed)"
        fi
    done
}

case "$arg" in
    "")
        list_default
        ;;
    all)
        echo "== mine =="
        list_mine
        echo ""
        echo "== gstack =="
        list_gstack
        echo ""
        echo "== installed =="
        list_installed
        echo ""
        echo "== plugins =="
        list_plugins
        echo ""
        echo "== upstream =="
        list_upstream
        ;;
    mine)        list_mine ;;
    gstack)      list_gstack ;;
    installed)   list_installed ;;
    plugins)     list_plugins ;;
    upstream)    list_upstream ;;
    groups)
        cat <<'EOF'
Available groups:
  mine        — your fork at ~/code/claude/skills/skills/ (default = this + install status)
  gstack      — gstack catalog at ~/.claude/skills/gstack/
  installed   — direct installs at ~/.claude/skills/<name>/ (real dirs, not symlinks, not gstack)
  plugins     — plugin-installed skills under ~/.claude/plugins/cache/
  upstream    — skills tracked in upstream/main (joewalnes/skills fork base)
  all         — every group, prefixed
EOF
        ;;
    -h|--help|help)
        cat <<'EOF'
Usage: skill-list [<group>]

  (no arg)    Same as `make list` — your skills + install status.
  all         Every group, prefixed with [group] headers.
  groups      List available group names.
  <group>     One of: mine, gstack, installed, plugins, upstream.
EOF
        ;;
    *)
        echo "Unknown group: $arg" >&2
        echo "Run 'skill-list groups' for the list." >&2
        exit 2
        ;;
esac
