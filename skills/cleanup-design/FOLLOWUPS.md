# cleanup-design — follow-ups

Surfaced 2026-05-11 from dogfooding against a real personal project. Items are skill-level improvements; each came up during the first real use.

## S1. Read-before-edit failures during bulk reference cleanup

**Problem.** Several Edit calls in the bulk-reference bucket failed with "File has not been read yet" because the executor tried to update files it hadn't previously read. The Edit tool requires Read on the file first; the skill didn't ensure that.

**Proposed fix.** In the Execute phase, when a bucket touches multiple files that haven't been individually read in-session:
1. Pre-Read every target file (one round, parallel).
2. Then fire Edits (parallel, by file).

For bulk-reference-style updates where the replacement is a simple path swap, the skill could also note that `Edit` with `replace_all: true` is the right tool (vs. multiple positional Edits), once the file has been Read.

## S2. Drift detection from recently-closed helping-hands worked

**Validation.** The strong heuristic from the SKILL.md ("for each helping-hand marked `status: done` in last N days, grep canonical doc for pre-decision state") found the cleanup items correctly:

- Q1/Q2 (lazy-gm + attribution decisions closed 2026-05-11) → caught DESIGN.md §M3, assistant-mode-first.md slices, NEXT.md slice-4.
- Q3 (deprecated-notes-regression closed 2026-05-11) → caught DESIGN.md §M6 + 5 stale `notes/virtual-gm-personality-init.md` references.

Bonus find from the same scan: setup-ritual.md Phase 2 outputs still listed `vibe anchor` and `failure mode` despite §M10 having relocated them. The drift wasn't from a 2026-05-11 decision but from the older §M10 decision — suggests the skill should periodically widen the lookback window when invoked explicitly, not just look at "last N days." Maybe: default N=14 for auto-runs, N=∞ when the user asks for a broader sweep.

## S3. Bulk reference cleanup as a first-class bucket pattern

**Pattern observed.** When a file moves (e.g., `notes/foo.md` → `notes/deprecated/foo.md`), many other files reference the old path. These accumulate into a "bulk reference cleanup" bucket that's:

- Trivially safe (path string swap, no semantic change).
- Tedious to walk through per-item.
- Best handled as a single bulk-approve action.

The skill currently treats this as `update-reference`. Worth making it explicit in the Present phase: when 3+ findings share the same root cause (a single file moved), group them under one bulk-approve question rather than 3+ individual approvals.

## Related

- `SKILL.md` — the skill these improvements target
