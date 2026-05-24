---
name: cleanup-design
description: Use when asked to clean up, audit, or refresh the project's design corpus ("clean up design", "what's stale", "should anything move to done", "audit the design docs", "any drift between recent decisions and docs", "post-decision sweep"). For maintaining design-doc invariants in projects that use `design/` (or equivalent) with stories, helping-hands, notes, and canonical design docs.
---

# cleanup-design

Audits and refreshes a project's design corpus — `stories/`, `helping-hands/`, `notes/`, and canonical design docs (`DESIGN.md` or similar). Catches drift that accumulates when decisions are made in one place but the docs elsewhere haven't been updated yet.

## When to use vs. skip

Use for: "clean up design", "audit design docs", "what's stale", "should anything move to done", "any drift since [date]", "post-decision sweep".

Skip if: the project has no `design/` or equivalent corpus, or the user wants a single targeted edit (use Edit directly).

## Phases

### 1. Orient

Discover the project's design layout. Typical:

- **Stories** at `design/stories/` with sub-categories: `drafts/`, `ready/`, `done/` (newer convention) or `llm_generated/`, `user_updated/`, `z.done/` (older).
- **Helping-hands** at `design/helping-hands/` (its README usually carries the project's conventions for status/closing).
- **Notes** at `design/notes/` (and `design/notes/deprecated/` if present).
- **Canonical docs**: `design/DESIGN.md`, `design/README.md`, `design/NEXT.md` if present.
- **Project README** + **CLAUDE.md** for conventions.

If the project uses a different layout (`docs/architecture/`, `docs/specs/`, etc.), adapt accordingly. If unclear, ask via `AskUserQuestion` rather than guess.

### 2. Scan

Run focused checks per artifact category.

**Stories** (`ready/` + `drafts/`):

- Read frontmatter (`status`, `priority`, `author`).
- Check cross-references in the body: do `../stories/...`, `../../notes/...`, `../helping-hands/...` paths resolve to live files?
- Check whether referenced files have moved to `deprecated/`.
- For acceptance criteria: surface only obvious satisfactions (a checkbox names a file/function that grep-able-exists in the codebase). Don't be aggressive.
- For Open Questions: check whether recently-closed helping-hands or recent commits answer them.

**Helping-hands**:

- Read frontmatter (`status`).
- If `status: done` and a Decision section exists, fine.
- If `status: open` but a Decision section or "resolved" mention exists elsewhere, flag.
- Closed items stay in place per the helping-hands convention; don't propose archiving unless the project's README says otherwise.

**Notes**:

- Check for `deprecated: true` frontmatter on files inside `deprecated/`.
- Check that files in `notes/` (not `notes/deprecated/`) don't have `deprecated: true`.
- Dead-link check: find `notes/<foo>` paths in any artifact that point at files now under `deprecated/`.

**Canonical design docs** (DESIGN.md or equivalent):

- Section-level dead-link check (path references that no longer resolve).
- **Drift detection** — the strong one: for each helping-hand marked `status: done` in the last N days (default N=14), grep the canonical doc for references to the _pre-decision_ state. Surface mismatches.
- Open Questions section: cross-reference against recent helping-hands marked done.

**Resume pointers** (`NEXT.md` or similar):

- "Next concrete action" — does it still reference content that's been updated?

### 3. Triage

Group findings into buckets with suggested dispositions:

- **`update-section`** — prose update needed in a specific file/section
- **`move-to-done`** — story whose acceptance criteria appear satisfied (only on strong signal)
- **`mark-resolved`** — helping-hand has decision elsewhere but status still open
- **`update-reference`** — cross-reference path is stale (file moved/deprecated)
- **`archive`** — note that should move to `deprecated/`
- **`leave`** — flagged but no action; mention only if explicitly listed

### 4. Present

Show the staged list grouped by bucket. For each item: file path, line number (if applicable), short description, suggested action.

- **0 findings** → report "design corpus is clean."
- **1–5 findings** → present each individually with a proposed change preview; `AskUserQuestion` per item or bulk-approve.
- **6+ findings** → present grouped by bucket; `AskUserQuestion` for bucket-level approval first, then walk per-item only for buckets the user opts to review.

### 5. Execute

On approval:

- Edit prose changes.
- Move files (with `git mv` if in a git repo; otherwise Write+verify+delete).
- Update frontmatter (status changes, deprecation flags).
- Strip dead references or update to new paths.

Never auto-act on items the user hasn't approved.

## Discovery heuristic — drift detection (the strong one)

The most useful finding type is _drift_: a recently-made decision whose spec hasn't caught up. To detect:

1. Find helping-hands with `status: done` and recent `resolved:` date (or recent mtime if no `resolved:` field).
2. Find the artifacts those helping-hands `Related:` link to (or are reciprocally linked from). Also include the canonical design doc (sections it touches) and any active story (likely in `ready/`).
3. Check those artifacts: do they still describe the pre-decision state?
4. Surface mismatches with the specific helping-hand cited as the evidence.

This is what catches "we made decision X in a helping-hand but DESIGN.md still says ~X."

## Common mistakes

- **Aggressive auto-archive.** Moving a story to `done/` because acceptance criteria _look_ met. Always confirm with the user.
- **Treating drafts as drift candidates.** `drafts/` are inherently unsettled; don't propose archiving or moving them without strong signal.
- **Over-scanning a clean corpus.** Re-running on a clean corpus should report "clean" quickly, not produce noise.
- **Conflating recency with importance.** A 90-day-old story may still be live; don't propose archiving by date alone.
- **Reading deprecated files.** If the project has a `deprecated/` directory or a CLAUDE.md rule about it, respect it. Surface the existence of deprecated files but don't load their contents.

## Quick reference

| Bucket           | Action                           | Strict approval?       |
| ---------------- | -------------------------------- | ---------------------- |
| update-section   | Edit prose                       | yes (per item)         |
| move-to-done     | Move story                       | yes (per item)         |
| mark-resolved    | Update status + decision section | yes (per item or bulk) |
| update-reference | Edit stale path                  | bulk-approve ok        |
| archive          | Move to deprecated/ + flag       | yes (per item)         |
| leave            | nothing                          | n/a                    |

## Help

When invoked as `/cleanup-design help`, print the following block verbatim:

```
cleanup-design — Audit and refresh a project's design corpus for drift.

Usage: /cleanup-design

Walks stories/, helping-hands/, notes/, and canonical design docs; catches
drift between recently-made decisions and the docs that should reflect them.

Phases (run in sequence):
  Orient            Discover project's design layout.
  Scan              Per-artifact checks: stories, helping-hands, notes,
                    canonical docs, resume pointers. Drift detection is
                    the strongest finding type.
  Triage            Group by bucket: update-section, move-to-done,
                    mark-resolved, update-reference, archive, leave.
  Present           Show staged list; per-item or bulk approval.
  Execute           Edit / mv / update frontmatter on approval only.

Layout conventions (auto-detected):
  design/stories/{drafts,ready,done}/           Newer (groot-project)
  design/stories/{llm_generated,user_updated,z.done}/  Older
  design/helping-hands/, design/notes/, design/DESIGN.md

For drafting walkthroughs from a user perspective, see /walkthrough.

See SKILL.md for full reference.
```

## Related

- `walkthrough` — sister skill for narrative production + iteration toward design integration; this one is for design-corpus maintenance.
