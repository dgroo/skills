#!/usr/bin/env bash
# Block staged edits to skills/<name>/ where <name> is tracked in upstream/main.
#
# Rationale: this repo is a fork of joewalnes/skills. Editing an upstream-tracked
# skill in place guarantees merge conflicts on every `git fetch upstream` pull.
# Fork the skill under a new local name instead.
#
# Override (for the rare case of an actual upstream contribution):
#   SKIP_UPSTREAM_GUARD=1 git commit ...
#
# Top-level files (CLAUDE.md, README.md, Makefile) are intentionally not guarded
# — they're soft-tracked and local edits are expected.

set -euo pipefail

if [ "${SKIP_UPSTREAM_GUARD:-0}" = "1" ]; then
    exit 0
fi

# No upstream remote = nothing to guard against. Quietly succeed.
if ! git remote get-url upstream >/dev/null 2>&1; then
    exit 0
fi

# Need upstream/main locally to know what's tracked. If it's missing, skip
# rather than fail — a fresh clone without `git fetch upstream` shouldn't be
# blocked from committing.
if ! git rev-parse --verify --quiet upstream/main >/dev/null; then
    exit 0
fi

upstream_skills="$(git ls-tree -r --name-only upstream/main \
    | awk -F/ '$1 == "skills" && NF >= 2 { print $2 }' \
    | sort -u)"

if [ -z "$upstream_skills" ]; then
    exit 0
fi

staged="$(git diff --cached --name-only --diff-filter=ACMRT)"
violations=""

while IFS= read -r file; do
    [ -z "$file" ] && continue
    case "$file" in
        skills/*/*)
            name="$(printf '%s' "$file" | awk -F/ '{print $2}')"
            if printf '%s\n' "$upstream_skills" | grep -qx "$name"; then
                violations="${violations}  $file"$'\n'
            fi
            ;;
    esac
done <<< "$staged"

if [ -n "$violations" ]; then
    cat >&2 <<EOF
ERROR: staged changes touch upstream-tracked skills:

${violations}
These skills are tracked in upstream/main (joewalnes/skills). Editing them
locally guarantees merge conflicts on every upstream pull.

Fork the skill into a new local skill name instead:

    cp -r skills/<name> skills/<your-name>
    # edit skills/<your-name>/SKILL.md, change frontmatter name

Override (e.g., for an actual upstream contribution):

    SKIP_UPSTREAM_GUARD=1 git commit ...
EOF
    exit 1
fi
