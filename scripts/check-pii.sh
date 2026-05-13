#!/usr/bin/env bash
# Scan files for PII patterns defined in .pii-patterns at the repo root.
#
# Usage:
#   check-pii.sh                   # scan all tracked files (default)
#   check-pii.sh --all             # scan all tracked files (explicit)
#   check-pii.sh --staged          # scan files staged for commit (pre-commit mode)
#   check-pii.sh path [path ...]   # scan specific files
#
# An inline marker "pii-allow" on a matched line suppresses the finding.
# Use it for intentional references, e.g.:
#   # Example assumes /Users/alice/...  # pii-allow: example only
#
# Exits 1 if any unallowed match is found, 0 otherwise.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATTERNS_FILE="$REPO_ROOT/.pii-patterns"
SCANNER_BASENAME="$(basename "$0")"

if [[ ! -f "$PATTERNS_FILE" ]]; then
  echo "check-pii: no .pii-patterns at $PATTERNS_FILE — nothing to scan against" >&2
  exit 0
fi

# Build a clean patterns file (strip blank/comment lines)
tmp_patterns="$(mktemp)"
trap 'rm -f "$tmp_patterns"' EXIT
grep -vE '^[[:space:]]*(#|$)' "$PATTERNS_FILE" > "$tmp_patterns" || true
if [[ ! -s "$tmp_patterns" ]]; then
  exit 0
fi

# Choose file set
mode="${1:-}"
case "$mode" in
  --staged)
    files_raw="$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)"
    ;;
  --all|"")
    files_raw="$(git ls-files 2>/dev/null || true)"
    ;;
  *)
    # Treat all args as filenames
    files_raw="$(printf '%s\n' "$@")"
    ;;
esac

[[ -z "$files_raw" ]] && exit 0

exit_code=0
finding_count=0

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  [[ ! -f "$file" ]] && continue

  case "$(basename "$file")" in
    .pii-patterns|.pii-allowlist|"$SCANNER_BASENAME") continue ;;
  esac

  # Skip binary files
  if file --mime-encoding "$file" 2>/dev/null | grep -q 'binary'; then
    continue
  fi

  matches="$(grep -nEHf "$tmp_patterns" "$file" 2>/dev/null || true)"
  [[ -z "$matches" ]] && continue

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if printf '%s' "$line" | grep -q 'pii-allow'; then
      continue
    fi
    printf '%s\n' "$line" >&2
    finding_count=$((finding_count + 1))
    exit_code=1
  done <<< "$matches"
done <<< "$files_raw"

if [[ $exit_code -ne 0 ]]; then
  cat >&2 <<EOF

check-pii: $finding_count match(es) found.
Resolve by one of:
  - Redact the offending content.
  - Add an inline "# pii-allow: <reason>" marker on the line (intentional).
  - Update .pii-patterns if the rule itself is wrong.

Emergency override: 'git commit --no-verify' (the GitHub Action still runs on push).
EOF
fi

exit $exit_code
