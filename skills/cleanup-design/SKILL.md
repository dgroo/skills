---
name: cleanup-design
description: Use when asked to clean up, audit, or refresh the project's design corpus ("clean up design", "what's stale", "should anything move to done", "audit the design docs", "any drift between recent decisions and docs", "post-decision sweep"), OR to check a project against the canonical design-corpus model / catch a drifted project up on conventions ("does this match our standard layout", "conform this project", "/cleanup-design conformance"). For maintaining design-doc invariants in projects that use `design/` (or equivalent) with stories, helping-hands, notes, and canonical design docs.
---

# cleanup-design

Audits and refreshes a project's design corpus — `stories/`, `helping-hands/`, `notes/`, and canonical design docs (`DESIGN.md` or similar). Catches drift that accumulates when decisions are made in one place but the docs elsewhere haven't been updated yet.

## Two modes

- **Drift audit (default)** — the phases below. Catches drift _within_ the project: a decision made in one place that the docs elsewhere haven't caught up to. Run with bare `/cleanup-design`.
- **Canonical conformance** (`/cleanup-design conformance`) — diffs the project's _structure_ against the federation's canonical design-corpus model, catching drift _from the standard itself_: meta-files in the wrong place, an outdated stories layout, a convention the project predates. This is the self-repair pass for "I'm back in a project I haven't touched in weeks — catch it up on our conventions." See [Canonical conformance mode](#canonical-conformance-mode).

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

## Canonical conformance mode

**Goal:** answer "does this project match our _current_ canonical design-corpus model, and what would bring it into line?" — the self-repair pass for a project that has drifted from the evolving standard.

**Single source of truth — read it, don't hardcode.** The canonical model lives in `~/code/groot-claude-coord/design/design-corpus/DESIGN.md` (the federation design-corpus spec: the meta-file lane table, per-project-variation rules, and the §8 migration steps + "consumers to update" list). **Read that file at run time and diff against it — never bake a copy of the layout into this skill**, or the two drift (the exact failure this skill exists to prevent). If `~/code/groot-claude-coord/` is absent (different org/host), say so and skip conformance — there's no canon to diff against.

**Steps:**

1. **Load the canon.** Read the design-corpus `DESIGN.md`. Extract the meta-file lane table (which file lives where — `design/TODO.md`, `design/NEXT.md`, …), the stories layout, and §8 (migration steps + the consumers-to-update list).
2. **Inventory the project.** Where are this project's `TODO.md` / `NEXT.md` / `REVISIT.md` / `DIARY.md` (root vs `design/`)? What's the `stories/` shape (`drafts/ready/done` vs flat+frontmatter vs older)? Is there a `plans/` that canon folds into `stories/`? Any missing canonical surface (`HUMAN-REVIEW.md`, per-host diary shards)?
3. **Diff → findings.** One finding per divergence: _what canon says · what the project has · the fix · safe-or-deliberate._
4. **Classify safe vs. deliberate — this is the load-bearing judgment.**
   - **Safe** (apply on approval): additive, no consumer-path risk — create a missing `HUMAN-REVIEW.md`, backfill frontmatter, fix a stale cross-reference.
   - **Deliberate** (flag with a migration plan, never one-click): **moving root meta-files into `design/` is the canonical example** — §8 calls it out as breaking path-hardcoding consumers. Before proposing such a move, **walk §8's consumers-to-update list and verify each actually tolerates the new path** — do not assume. The known trap: `~/bin/backlog-scan` reads root `TODO.md` and root `REVISIT.md` (only `NEXT.md` is `design/`-preferred with a root fallback), so migrating those two to `design/` would _silently stop them being scanned_ until backlog-scan is taught the new path. When the tooling doesn't yet support the canonical location, the finding is **"canon says X but the tooling isn't wired for it — fix the tooling first, or stay put"**, not "migrate now." Use `git mv` only after the consumer check passes.
5. **Present + execute** as in the default mode (per-item or bulk; never auto-act on the deliberate class without an explicit go).

**Don't manufacture conformance churn.** A project deliberately on an older-but-working layout is not a bug. Surface the drift, note that it works today (cite _why_ — e.g. "backlog-scan reads root `TODO.md`"), and let the user choose. Most of the value here is _visibility_, not forced uniformity — and a canon/tooling contradiction surfaced is itself a useful finding (route it to the user, since fixing it means changing the canon or the tooling, not the project).

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

Usage: /cleanup-design [conformance]

Two modes:
  (default)     Drift audit — walks stories/, helping-hands/, notes/, and
                canonical design docs; catches drift between recently-made
                decisions and the docs that should reflect them.
  conformance   Diffs the project's STRUCTURE against the canonical
                design-corpus model in groot-claude-coord (read at run time,
                not hardcoded). Catches meta-files in the wrong place, an
                outdated stories layout, a convention the project predates.
                The "catch a stale project up on our conventions" pass.
                Classifies fixes safe (apply) vs. deliberate (migration plan,
                verify §8 consumers first — e.g. backlog-scan reads root
                TODO.md, so moving it to design/ needs the tooling taught).

Drift-audit phases (run in sequence):
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
