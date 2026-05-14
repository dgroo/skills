#!/usr/bin/env bash
# Show what's new in upstream/main that isn't in HEAD.
# Used by `make upstream-check` and the /sup skill.
#
# Output is empty (and exit 0) when fully up to date — safe to embed in other
# reports without noise.

set -euo pipefail

if ! git remote get-url upstream >/dev/null 2>&1; then
    echo "No 'upstream' remote configured. Add one with:"
    echo "  git remote add upstream https://github.com/joewalnes/skills.git"
    exit 0
fi

# Fetch quietly; if it fails (offline, auth), warn but don't error.
if ! git fetch upstream main --quiet 2>/dev/null; then
    echo "warning: could not fetch upstream/main (offline?). Showing cached state."
fi

if ! git rev-parse --verify --quiet upstream/main >/dev/null; then
    echo "upstream/main not available locally yet. Run 'git fetch upstream main'."
    exit 0
fi

ahead="$(git rev-list --count HEAD..upstream/main 2>/dev/null || echo 0)"

if [ "$ahead" = "0" ]; then
    exit 0
fi

echo "Upstream: $ahead commit(s) ahead of HEAD."
echo
git log --oneline HEAD..upstream/main | sed 's/^/  /'
echo
echo "Changed paths:"
git diff --name-only HEAD..upstream/main | sed 's/^/  /'
echo
echo "To pull: git merge upstream/main  (or rebase per your preference)"
