# Walkthrough Rework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the walkthrough rework spec'd in `design/stories/drafts/walkthrough-rework.md` — collapse 6 verbs + 4×3 scoping into 5 verbs with an iteration-toward-design spine, retire `/integrate-comments`, drop `trajectory` mode.

**Architecture:** Pure documentation rework — a SKILL.md rewrite, a sub-file deletion, a sibling skill deletion, and tracking-file updates. No code, no tests. Verification is reading the rewritten skill and doing a smoke `/walkthrough help`.

**Tech Stack:** Markdown. Make for symlink refresh. Git for atomic commits.

---

## File Structure

**Files modified:**
- `skills/walkthrough/SKILL.md` — full rewrite of Routing, Modes, Draft, and new Review/Revise/Apply sections; deletions for Check / Clean-comments / Follow-ups / Trajectory; updated Help and Quick Reference. Preserve: When-to-use, Self-bootstrap, the auto-discovery rules, the framing-note discipline, the failure-mode prose around cast/texture drift and scope disambiguation.
- `README.md` — remove `integrate-comments` row from Skills table.
- `MAINTAINERS.md` — remove `integrate-comments` row.
- `DIARY.md` — new top entry recording the rework.

**Files created:**
- (none beyond the spec and this plan, already in `design/stories/drafts/`)

**Files deleted:**
- `skills/walkthrough/trajectory.md`
- `skills/integrate-comments/SKILL.md`
- `skills/integrate-comments/FOLLOWUPS.md`
- `skills/integrate-comments/` (the directory itself)

**Files audited for cross-references** (may or may not need edits depending on what they say):
- `skills/cleanup-design/SKILL.md`
- `skills/groot-project/SKILL.md`
- `skills/helping-hands/SKILL.md`
- `skills/project-setup/SKILL.md`
- `skills/skill-add/SKILL.md`
- `skills/skills-review/SKILL.md`

**Files preserved as-is:**
- `skills/walkthrough/FOLLOWUPS.md` — historical record of resolved follow-ups from earlier dogfood passes. Don't touch.

---

## Phase 1: Retirement

### Task 1: Delete trajectory.md and integrate-comments/

**Files:**
- Delete: `skills/walkthrough/trajectory.md`
- Delete: `skills/integrate-comments/` (whole dir)

- [ ] **Step 1: Confirm both paths are local-owned, not upstream-tracked**

```bash
grep -E "integrate-comments|walkthrough" MAINTAINERS.md
```
Expected: both listed as local-owned entries with dates. If they aren't in MAINTAINERS.md as local, STOP and surface to the user before deleting.

- [ ] **Step 2: Delete both**

```bash
rm skills/walkthrough/trajectory.md
rm -rf skills/integrate-comments/
```

- [ ] **Step 3: Verify**

```bash
ls skills/walkthrough/
ls skills/integrate-comments/ 2>&1 | head -1
```
Expected: `walkthrough/` shows `SKILL.md FOLLOWUPS.md` only; `integrate-comments/` shows "No such file or directory".

- [ ] **Step 4: Commit**

```bash
git add -A skills/walkthrough/ skills/integrate-comments/
git commit -m "retire: trajectory mode + /integrate-comments skill

Per design/stories/drafts/walkthrough-rework.md — trajectory mode
doesn't fit the iteration-toward-design spine; /integrate-comments
has never been called outside walkthrough and the user is the only
consumer of this skills directory."
```

### Task 2: Update README.md and MAINTAINERS.md

**Files:**
- Modify: `README.md` (remove `integrate-comments` row from Skills table)
- Modify: `MAINTAINERS.md` (remove `integrate-comments` row)

- [ ] **Step 1: Find the integrate-comments row in README.md**

```bash
grep -n "integrate-comments" README.md
```
Expected: one or two lines (table row + possibly a reference).

- [ ] **Step 2: Remove the row from README.md's Skills table**

Open `README.md`, find the row whose first column is `integrate-comments` (or links to that skill), delete the line. Leave the rest of the table intact (alphabetical order preserved). If there are non-table references to `/integrate-comments` elsewhere in the README, delete those too.

- [ ] **Step 3: Remove the row from MAINTAINERS.md**

```bash
grep -n "integrate-comments" MAINTAINERS.md
```
Open `MAINTAINERS.md`, find the row whose first column is `integrate-comments`, delete the line.

- [ ] **Step 4: Verify both files no longer mention integrate-comments**

```bash
grep -i "integrate-comments" README.md MAINTAINERS.md
```
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add README.md MAINTAINERS.md
git commit -m "docs: drop /integrate-comments from README + MAINTAINERS"
```

### Task 3: Audit cross-references in other skills

**Files audited:**
- `skills/cleanup-design/SKILL.md`
- `skills/groot-project/SKILL.md`
- `skills/helping-hands/SKILL.md`
- `skills/project-setup/SKILL.md`
- `skills/skill-add/SKILL.md`
- `skills/skills-review/SKILL.md`

- [ ] **Step 1: Grep each for mentions of the retired verbs and skill**

```bash
grep -nE "walkthrough (integrate|check|clean-comments|follow-ups|trajectory)|integrate-comments|/walkthrough integrate" skills/cleanup-design/SKILL.md skills/groot-project/SKILL.md skills/helping-hands/SKILL.md skills/project-setup/SKILL.md skills/skill-add/SKILL.md skills/skills-review/SKILL.md
```

- [ ] **Step 2: For each hit, decide: update, delete, or leave**

For each line that referenced a retired verb or skill:
- If the line references a verb that's been replaced (`integrate` → `revise`; `check` → `review`; `follow-ups` → `apply`; `clean-comments` → none, absorbed into `revise`), update the reference to the new verb.
- If the line references `/integrate-comments` as a callable skill, delete the mention or rewrite to point at `/walkthrough revise` if the context still applies.
- If the line is a historical reference (DIARY-style commentary or "see also" anchored in a specific moment), leave it as-is — historical context shouldn't get retconned.

Use Edit (not Write) for these — they're surgical.

- [ ] **Step 3: Verify**

```bash
grep -nE "/integrate-comments|walkthrough (trajectory|check|clean-comments|follow-ups)" skills/cleanup-design/SKILL.md skills/groot-project/SKILL.md skills/helping-hands/SKILL.md skills/project-setup/SKILL.md skills/skill-add/SKILL.md skills/skills-review/SKILL.md
```
Expected: only historical references survive (if any), and they're justified.

- [ ] **Step 4: Commit**

```bash
git add skills/
git commit -m "skills: update cross-references for walkthrough rework"
```

(If no edits were needed, skip the commit — Step 3 verification was enough.)

---

## Phase 2: Rewrite SKILL.md

The rewrite is one big edit. Use `Write` (full overwrite of `skills/walkthrough/SKILL.md`). Below is the *complete* target file content. The executor should write this verbatim, then move to Phase 3.

Two notes for the executor:
1. **The "Common mistakes" prose carries hard-won failure-mode signal from real dogfood.** Several bullets are preserved from the old SKILL.md (cast/texture drift, scope-disambiguation, framing-note, mode-bleed, untagged extrapolation). New bullets are added for the new shape. Don't summarize; the verbatim prose IS the value.
2. **The "When to use vs skip" section and "Self-bootstrap" section are preserved verbatim** from the old SKILL.md.

### Task 4: Write new SKILL.md

**Files:**
- Write: `skills/walkthrough/SKILL.md` (full overwrite)

- [ ] **Step 1: Write the new file**

Full target content is in this plan's Appendix A below. Copy it verbatim.

- [ ] **Step 2: Verify the file renders sensibly**

```bash
wc -l skills/walkthrough/SKILL.md
head -10 skills/walkthrough/SKILL.md
```
Expected: file exists, starts with frontmatter `---` block, `name: walkthrough` line present.

- [ ] **Step 3: Verify no references to retired verbs or sub-files remain**

```bash
grep -nE "trajectory|/integrate-comments|clean-comments|follow-ups|^## (Check|Clean-comments|Follow-ups|Integrate|Registers|Trajectory)" skills/walkthrough/SKILL.md
```
Expected: no output. (If "trajectory" appears in a historical comment, that's acceptable; the section headers and verb references are what matter.)

- [ ] **Step 4: Commit**

```bash
git add skills/walkthrough/SKILL.md
git commit -m "walkthrough: rewrite around iteration-toward-design spine

Per design/stories/drafts/walkthrough-rework.md. Five verbs
(bare/new/review/revise/apply) replacing the prior six. Drops
trajectory mode and the register axis. Adds Review auto-detect,
Revise re-imagine semantics, and Apply diff-first batch-approval."
```

---

## Phase 3: Validate + Integrate

### Task 5: make install + smoke test

**Files:**
- (no edits; runs `make install` and inspects symlinks)

- [ ] **Step 1: Refresh symlinks**

```bash
make install
```
Expected: output mentions linking `walkthrough` (and others); no error about `integrate-comments` (it's gone now and shouldn't appear in install output).

- [ ] **Step 2: Verify integrate-comments is no longer symlinked into ~/.claude/skills**

```bash
ls ~/.claude/skills/ | grep -i integrate-comments
```
Expected: no output. If output appears, the symlink is stale — investigate `make install` to ensure it cleans dropped skills.

- [ ] **Step 3: Verify the new walkthrough SKILL.md reads through CC's skill registry**

In a fresh Claude Code session, type `/walkthrough help` and confirm the help block matches the new content (5 verbs listed, no `check`/`clean-comments`/`follow-ups`/`integrate` verbs, no trajectory mode, no register axis).

(This step requires a session restart since SessionStart loads the skill catalog. The executor can flag this as a manual user step or skip if the project's harness loads skills dynamically.)

### Task 6: DIARY entry

**Files:**
- Modify: `DIARY.md` (add top entry, latest-first convention)

- [ ] **Step 1: Read the current top of DIARY.md to match the format**

```bash
head -5 DIARY.md
```

- [ ] **Step 2: Add a new top entry**

Insert below the `---` separator under the first `# Engineering Diary` block. Suggested content:

```markdown
## 2026-05-24 — `/walkthrough` rework around iteration-toward-design spine

Collapsed `/walkthrough` from six verbs (bare/new/integrate/check/clean-comments/follow-ups) down to five (bare/new/review/revise/apply), centered on a clear iteration loop: draft → review → branch (write more analysis / re-imagine the walkthrough / apply to design) → loop → archive. Retired `/integrate-comments` entirely (never used outside walkthrough) and deleted `trajectory` mode (4-artifact build didn't fit the new spine). Dropped registers as a formal axis; default voice is now a one-paragraph guideline ("grounded — named protagonist as anchor only") with the failure-mode prose about cast/texture drift preserved as a Common Mistakes bullet.

The forcing question was Derek's: he wrote up exactly how he intended to use the skill (three flows, one iteration loop), and the existing surface had grown sideways from that mental model. The earlier `/walkthrough integrate` alias (DIARY 2026-05-23) addressed the discoverability symptom but not the underlying mismatch — the skill had verbs the user wasn't reaching for and lacked verbs for the things he was actually doing.

The decision worth pinning: **register axes are a tax against a real failure mode but a wrong-shape tax.** Registers (spec/grounded/storied) were added after a draft sprouted cast and texture the user didn't want (kids, partner, atmosphere). The fix at the time was to make voice an explicit scoping question; the better fix turned out to be a default with one paragraph naming the failure mode in Common Mistakes. Scoping-as-guardrail is heavier than guideline-plus-failure-mode-callout when the failure mode is narrow and well-named.

Migration: `make install` cleaned up the `/integrate-comments` symlink; cross-references in other skills (cleanup-design, groot-project, helping-hands, project-setup, skill-add, skills-review) were audited and updated where they pointed at retired verbs.
```

(Adjust prose to match what actually happened during execution — if Phase 1 Task 3 found no cross-references that needed updating, drop that sentence.)

- [ ] **Step 3: Commit**

```bash
git add DIARY.md
git commit -m "diary: walkthrough rework (iteration-toward-design spine)"
```

### Task 7: Push

- [ ] **Step 1: Push all commits**

```bash
git push
```

Expected: 5–6 commits pushed (depending on whether Task 3 needed a commit).

---

## Self-Review

**Spec coverage:**
- Verb surface (5 verbs): Task 4 (SKILL.md Routing section)
- Retirements (trajectory, integrate-comments, check, clean-comments, follow-ups, integrate): Tasks 1, 2, 3, 4
- Draft scoping (modes, register guideline): Task 4 (Modes + Draft sections)
- Review auto-detect + branches: Task 4 (Review section)
- Revise mechanics (marker-ack, version-aside, re-imagine): Task 4 (Revise section)
- Apply mechanics (diff-first, batch approve, archive offer): Task 4 (Apply section)
- Artifact model (flat versioned dir): Task 4 (Save subsection of Draft, plus Revise)
- Bare smart-route: Task 4 (Routing table + Smart-route subsection)
- Cross-reference cleanup: Task 3
- Migration completeness: Phase 3 tasks

All spec sections are covered.

**Placeholder scan:** None — task content is concrete throughout. The Appendix A content (next section) needs to be the full SKILL.md prose.

**Type consistency:** N/A — no types, no APIs. Verb names are consistent across spec, plan, and SKILL.md target content (Appendix A).

---

## Appendix A: Target content for `skills/walkthrough/SKILL.md`

````markdown
---
name: walkthrough
description: Use when asked to produce a narrative walkthrough of how an application or system is used end-to-end from a specific user's perspective ("walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc"). Tutorial-quadrant docs — story-shaped, learning-oriented — distinct from reference, spec, and how-to. Centered on a draft → review → branch (write / revise / apply) iteration loop that converges on integrating insights back into the project's design.
---

<!-- Maintenance: SKILL.md loads on every invocation. Before adding mass, prefer compressing in place. Check size with `wc -w SKILL.md`. -->

# Walkthrough

Produces tutorial-quadrant narrative docs that show how a real user would install, configure, and use an application end-to-end. Story-shaped, learning-oriented. Distinct from architecture/spec/reference (which live in design docs), step-by-step task instructions (how-to), and conceptual explanation.

The skill is organized around a single iteration loop: **draft** a walkthrough (CC or human-authored, sometimes both), **review** the current state (analysis surfaced in conversation), branch into one of three actions (**write** more analysis to a review file, **revise** the walkthrough into a fresh version, or **apply** insights to the project's design), loop until satisfied, and archive the working dir.

## When to use vs. skip

Use for: "walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "describe what installing and using this looks like".

Skip if the user wants architecture/API/spec content (that's reference), step-by-step task instructions for one task (that's how-to), or conceptual explanation (that's explanation).

## Modes

A walkthrough's _temporal stance_ — what slice of the app it describes — is chosen during scoping. Mode is metadata of the doc, persisted in the framing-note at the top of the file.

| Mode | Sources | Tagging | When to pick it |
|------|---------|---------|-----------------|
| `current` | Code + README + shipped behavior. No speculative design docs, no draft stories. | None — refuse to extrapolate. If the code doesn't settle it, ask or omit. | "How does this work today?" — onboarding, dogfooding, support docs. |
| `planned` | `current` sources + near-term planned work (`stories/ready/`, `stories/drafts/`, roadmap docs treated as committed). | `[planned]` for not-yet-shipped items. No `[extrap]`. | "How will this work next milestone?" — sequencing reviews, scoping decisions. |
| `infinity` (default) | Everything: code + all stories + speculative design docs + extrapolation past spec. | `[extrap]` for anything past spec. | "What does this become eventually?" — selling the vision, finding spec gaps, North Star docs. |

**Default:** `infinity` for actively-developing projects. The framing-note at the top of an `infinity` doc explains what's shipping now vs. described-as-future.

**Framing-note (every mode).** First paragraph of the doc declares the slice the reader is in:

- `current`: "This walkthrough describes the app as it ships today (commit `<sha>` / `<date>`)."
- `planned`: "...as planned through milestone `<name>`. `[planned]` marks items not yet shipped."
- `infinity`: "...as currently conceived end-state. `[extrap]` marks speculation past spec."

## Verb surface

Five verbs. Bare invocation smart-routes.

| Invocation | Action |
|------------|--------|
| `/walkthrough` (bare) | Smart-route. See [Smart-route logic](#smart-route-logic). |
| `/walkthrough new` | Force-fresh draft regardless of existing state. Used for parallel artifacts (e.g., a CC draft alongside a human draft for two-input review). |
| `/walkthrough review [path]` | Analyze current state; auto-detects single-CC / single-human / two-input cases. Produces analysis in conversation and surfaces three branches. See [Review](#review). |
| `/walkthrough revise [path]` | Re-imagine `walkthrough.md` from current state + comments + design surface. See [Revise](#revise). |
| `/walkthrough apply [path]` | Propose diff of design-surface mutations, batch-approve, apply, offer to archive. See [Apply](#apply). |
| `/walkthrough help` | Print Unix-style usage block. See [Help](#help). |

### Smart-route logic

`/walkthrough` (bare) decides what to do by inspecting the expected walkthrough dir (see [Auto-discovery](#auto-discovery)):

- No dir or no walkthroughs → draft (run scoping pass)
- Walkthrough exists with unseen `@user:` markers anywhere in the dir (`walkthrough.md` or any `review-N.md`) → `review`
- Walkthrough exists, no unseen markers → ask: `revise` / `apply` / draft new?

If the auto-discovery finds multiple candidate dirs, ask which one — don't guess.

### Auto-discovery

When a verb is invoked without a path, search for the walkthrough dir in this order, first existing root wins:

1. `design/walkthroughs/<YYYY-MM-DD>-<slug>/`
2. `design/notes/` (legacy flat-file layout)
3. `notes/`
4. `docs/walkthroughs/`
5. `docs/`

Within `design/walkthroughs/`, the candidate unit is the per-walkthrough subdirectory. Within the flatter fallback locations, candidates are files matching `*walkthrough*`, `*narrative*`, or frontmatter `doc-kind: narrative-walkthrough`.

Single match → use it. Multiple → ask (with last-modified date and mode in the prompt). Zero → ask whether to draft new.

## Draft

Default action when no walkthrough exists in the expected location.

### Orient

Read the project's design surface to ground the narrative. Typical entry points: `README`, `CLAUDE.md`, anything in `docs/` or `design/`. Skip if the user already supplied source material in the prompt.

**Don't read prior walkthroughs during orient.** If `design/walkthroughs/` (or equivalent) exists, do not include its contents in the orient pass — those are tutorial-quadrant docs, not the canonical design surface, and reading them at orient time biases the new draft toward the prior one's framing. Even in projects without a documented read-with-permission rule on the walkthroughs dir, hold the line. The exception is the _one_ walkthrough the user names as a comparison target.

### Scope

Use `AskUserQuestion` to pin anything not obvious from project docs or the user's request. Skip any question whose answer is already clear:

- **Comparison target / parallel artifact** _(first, before everything else)_ — if the user mentions "compare against," "parallel to," "diverge from," "ignore X but generate Y," or any specific prior narrative, identify the comparison target singularly before scoping anything else. Don't infer scope from "the most recently touched narrative" or from filenames visible via `ls`; visible existence ≠ scope signal. If "ignore X" is said, confirm what's being ignored — the file (as input), the topic, or both. Common failure mode: parsing "ignore the auth narrative" as "don't read that file" while still anchoring on auth as the topic.
- **Mode**: temporal stance — `current` / `planned` / `infinity` (default). Don't ask if the user's phrasing pins it ("how does this work today" → `current`; "what's it look like when finished" → `infinity`).
- **Perspective**: who is the narrative for? (end-user / admin / developer / API consumer / specific role). If the app has multiple user types, surface candidates and pick one; others get bottom-section variation notes.
- **Scenario**: primary path. If the app has modes / tiers / target systems, pick one primary; capture others as bottom-section variation notes.
- **Output location**: if `design/walkthroughs/` exists, use the per-dir layout: `design/walkthroughs/<YYYY-MM-DD>-<slug>/walkthrough.md`, with `<slug>` = mode (`current`/`planned`/`infinity`) for whole-product walkthroughs or `<topic>` for scoped walkthroughs. Otherwise fall back to a dated file in `design/notes/`, `docs/walkthroughs/`, or wherever the project keeps informal/snapshot docs.

### Draft

**Voice default: grounded.** Named protagonist as anchor only. No supporting cast, no sensory micro-scenes (origin stories, screenshots, atmospheric texture). Hold this default unless the user's prompt pins otherwise:

- "matter-of-fact" / "concise" / "no fluff" / "spec-shaped" → strip the protagonist to phases, roleless.
- "have fun with it" / "make it a story" / "with characters" → permit named supporting cast and sensory texture.

License to name humans is _not_ a signal to permit cast and texture; it's a license for the protagonist name only.

Mode rules:
- `current` — refuse to extrapolate. If the code doesn't settle a behavior, ask or omit. No `[extrap]`.
- `planned` — tag not-yet-shipped items with `[planned]`. Speculative material past the next milestone is out of scope.
- `infinity` (default) — describe the app as "done as currently conceived." `[extrap]` for anything past spec. Top-of-doc framing-note explains what's shipping now vs. described-as-future.

Standard arc:

1. **Install / first contact** — what the user downloads, where it lands, what the first command/click is
2. **Setup / first-run configuration** — first-run rituals, config files written, API keys
3. **Core usage loop** — the main reason the user is here; the rhythm they'll repeat
4. **Variations within the chosen scenario** — branch points the same user might hit
5. **End-state** — what success looks like; what's persisted; what cleanup looks like
6. **Bottom-section variation notes** — short paragraphs on materially different scenarios. Not full repeats; just deltas.

Drafting principles:

- **Concrete commands and file paths.** Show what the user actually types and what files get created.
- **Tag extrapolations** with `[extrap]` and a brief inline note when you infer past what the docs settle.
- **Iceberg discipline.** Describe just enough of each feature for the story to make sense; don't unload spec content.

### Save

Write to the location determined in scope. When using the `design/walkthroughs/<date>-<slug>/` layout, create the dir as part of the save step (`mkdir -p` plus the file in one motion).

The dir uses a flat versioned layout:

```
design/walkthroughs/<YYYY-MM-DD>-<slug>/
  walkthrough.md           ← current
  walkthrough-v1.md        ← prior, with @user+seen: markers preserved (post-revise)
  walkthrough-v2.md
  review-1.md              ← chained, never overwritten (post-write-review)
  review-2.md
```

At first draft, only `walkthrough.md` exists. Versioned-prior and review files appear as the iteration loop runs.

### (Optional) LLM companion

If the user asked for it, generate a second file with the same arc but a different shape:

- Frontmatter with retrieval metadata (`doc-kind`, `perspective`, `scenario`, `snapshot-date`, `source-anchors`)
- Phases as state declarations: `precondition / actions / artifacts / invariants / failure-modes`
- Roles instead of named characters
- Explicit cross-references to source-of-truth design artifacts
- `[extrap]` tags retained inline
- Bottom section explaining how this doc differs from the human companion

## Review

`/walkthrough review [path]` opens by inspecting the walkthrough dir to choose its analysis mode:

| Dir state | Action |
|-----------|--------|
| 0 walkthroughs | Ask: draft? |
| 1 walkthrough, CC-authored | Standard analysis of `walkthrough.md` + comments + any `review-N.md` files |
| 1 walkthrough, human-authored | 3-way gap-analysis (narrative ↔ design ↔ code) |
| 1 CC + 1 human walkthrough in dir | Compare-style synthesis review |

**Authorship detection signals** (any one is sufficient):
- Frontmatter declares author/source
- Marker style: `@user:` review markers → CC-authored target of review; `[[design-actionable]]` / `((aside))` markers → human-authored intent doc
- Filename convention if present
- Fallback: ask

### Single CC-authored: standard analysis

Read `walkthrough.md` and all `review-N.md` files. Identify each `@user:` comment and form a position on it: agree / disagree / needs-discussion / spec-gap. Surface the analysis in conversation as a numbered list, then present the three branches as options.

### Single human-authored: 3-way gap-analysis

The human has written a narrative encoding how they envision using the app. Compare it against the codebase + design docs to surface drift in any direction.

**Marker parsing** (default conventions; override if the narrative's preamble declares different markers):

- `[[design-actionable text]]` — embedded design notes the author wants picked up.
- `((parenthetical aside))` — clarifying context for the human reader, not design-actionable.

Procedure:
1. Read the narrative end-to-end. Capture its implied surface: commands the user types, files the app creates, behaviors invoked, modes / states / entry points referenced.
2. Skim the design surface. README + design index + any `design/` doc whose title overlaps a narrative-named verb or feature.
3. Skim the code. Targeted greps for narrative-named commands, file paths, config keys.
4. Build the three-way map. For each behavior the narrative implies, record what design-docs say (if anything) and what code shows (if anything). For each feature the code has, record whether the narrative mentions it.
5. Surface the analysis in conversation, structured as: recommended-pickup-order (3-5 highest-leverage gaps) → N→C gaps (narrative implies, code lacks) → C→N gaps (code has, narrative omits) → 3-way disagreements → `[[...]]` triage.

**Provenance discipline.** Every claim needs at least one anchor (`<file>:<line>` or `<file>`). No anchor → don't claim it.

After surfacing, present the three branches.

### Two-input (compare)

Both a CC-drafted walkthrough and a human-drafted walkthrough exist in the dir. Synthesize a comparison: where they agree (validates intent), where they diverge (the interesting signal), where each says something the other doesn't.

After surfacing, present the three branches.

### The three branches

After surfacing analysis, present the three branches as options (or invoke a branch verb directly):

1. **Write review file.** Persist the analysis as `review-<N+1>.md` (N = current count of review files in the dir). Before writing, marker-ack any `@user:` markers on prior files (`walkthrough.md`, `review-1.md..N.md`) — `@user:` → `@user+seen:` in place. The new review file is now a comment-able artifact in its own right; adding `@user:` markers to it and re-running `review` continues the loop.
2. **Revise.** See [Revise](#revise).
3. **Apply.** See [Apply](#apply).

## Revise

`/walkthrough revise [path]` produces a fresh `walkthrough.md` that re-imagines the story informed by the iteration so far.

Procedure:

1. Read `walkthrough.md` (with any `@user:` markers).
2. Rewrite those markers to `@user+seen:` in place. Preserves provenance — the prior file shows what was considered.
3. Read all `review-N.md` files; marker-ack their `@user:` too.
4. Move the current `walkthrough.md` to `walkthrough-v<N+1>.md` (next available number). Review files stay in place.
5. Write a fresh `walkthrough.md`, re-imagining the story informed by: prior walkthrough content, all comments (now seen-marked) across walkthrough.md and review-N.md, current design surface.
6. Surface a brief summary in conversation of what shifted vs. the prior version (1-3 bullets, not a diff).

**Not a surgical weave.** This is a genuine re-draft — fresh prose informed by the conversation, not edits-in-place. The prior version is preserved on disk (with seen markers) and in git.

## Apply

`/walkthrough apply [path]` mutates the project's design surface based on the iteration's accumulated insight.

Procedure:

1. Synthesize from current `walkthrough.md` + all `review-N.md` + comments into a **proposed diff** covering:
   - Story file creates (`design/stories/drafts/<slug>.md`, with frontmatter matching repo convention)
   - Story file edits (existing `drafts/` or `ready/` stories)
   - Story file moves (e.g., draft → ready, ready → done, or → archived)
   - Updates to supporting design docs (`README.md`, `CLAUDE.md`, `DESIGN.md`, etc. — per-project convention)
2. Surface the full diff in conversation. The user can:
   - Approve the batch
   - Reject individual items (re-render the remaining set)
   - Ask for revisions to a specific item
3. On approval, apply all changes.
4. Ask: "Move `design/walkthroughs/<date>-<slug>/` to `design/walkthroughs/archived/`?" Confirm with user; move if yes.

The archived dir is treated as read-with-permission per the project's standard `archived/` discipline.

## Help

When invoked as `/walkthrough help`, print the following block verbatim:

```
walkthrough — Tutorial-quadrant narrative docs from a user's perspective.
              Iteration loop converges on integrating insights into the design.

Usage: /walkthrough [verb] [path]

Verbs:
  (none)            Smart-route: review if walkthrough has unseen @user:
                    markers; ask revise/apply/new if no markers; else draft.
  new               Force-fresh draft regardless of existing state.
  review [path]     Analyze current state. Auto-detects single-CC /
                    single-human / two-input cases. Surfaces three branches.
  revise [path]     Re-imagine walkthrough.md from current state + comments.
                    Marker-acks the prior, version-asides it, writes fresh.
  apply [path]      Propose diff of design-surface mutations (story
                    creates/edits/moves + supporting doc updates).
                    Batch-approve, apply, offer to archive the dir.
  help              Show this message.

Modes (draft only):
  current           As-ships-today; no extrapolation.
  planned           Includes near-term roadmap; tags [planned] for unshipped.
  infinity (default) End-state as currently conceived; tags [extrap].

Voice default: grounded — named protagonist as anchor only, no side-cast or
sensory texture. Say "spec-shaped" / "concise" to strip; say "have fun with
it" / "make it a story" to permit cast and texture.

Markers:
  [[...]]           Human-authored design-actionable note (review input).
  ((...))           Human-authored aside / clarification (non-actionable).
  <!-- @user: -->   Unseen review marker on CC-drafted walkthrough.
  <!-- @user+seen: --> Marker acknowledged during revise / write-review.

Artifact layout (per walkthrough dir):
  design/walkthroughs/<YYYY-MM-DD>-<slug>/
    walkthrough.md           ← current
    walkthrough-v1.md ...    ← prior versions (post-revise)
    review-1.md ...          ← chained review files (post-write-review)

See SKILL.md for full reference.
```

## Out of scope

- **Archival initiation** is offered by `apply` but never forced. Manual move-to-archived/ remains valid at any time.
- **Pre-rework migration of existing in-flight walkthroughs.** Walkthrough dirs from before this skill's rework keep their original layout; the new conventions apply to walkthroughs drafted after.
- **Multi-author review markers.** The skill assumes one reviewer; the `@user:` namespacing supports multi-user if needed but the iteration loop's mechanics are written for the single-reviewer case.

## Self-bootstrap

On second invocation in the same project: if scoping conversations are repeating the same answers (same perspective, same output location, same naming convention), offer to write a thin project-specific wrapper skill (`walkthrough-<project-slug>`) that pre-fills those answers. User decides whether to bother — extraction is opt-in.

## Common mistakes

- **Drifts into architecture/spec content.** Narrative becomes a reorganized DESIGN.md. Fix: re-center on the protagonist's actions and what they see.
- **Skips the scoping pass.** Produces a generic narrative that satisfies no specific user type. Fix: confirm perspective + scenario before drafting unless they're obvious.
- **Forgets variation notes.** Assumes the chosen scenario covers all cases. Fix: always end with bottom-section notes on materially different scenarios.
- **Untagged extrapolation.** Implies behaviors the docs don't settle; reader trusts the narrative as spec. Fix: `[extrap]` every speculative passage.
- **Mode bleed.** `current` mode quietly imports planned behavior; `planned` quietly imports speculation. Fix: hold the line on what each mode sources — when in doubt for `current`, ask or omit; when in doubt for `planned`, defer to `infinity`.
- **Missing framing-note.** Reader can't tell which era they're in. Fix: every mode opens with a one-paragraph framing-note declaring the slice.
- **Anchors on the topic of a visible-but-unread narrative.** Sees `<date>-<topic>.md` in `design/notes/` during orient and infers the new walkthrough should be on `<topic>` — even when the user told it to ignore that file or generate something different. Filename existence ≠ scope signal. Fix: if the user mentions a comparison target, identify it singularly before scoping; parse "ignore X" carefully (file? topic? both?); ground in the project's canonical design surface (DESIGN.md, README, stories), not whatever narrative files happen to be in `design/notes/`.
- **Drifts into a story register by accident.** User gives "feel free to name humans" license and the draft sprouts a Reddit-thread origin scene, a screenshot-taking moment, a side-character cast, and atmospheric micro-paragraphs. The result is fun but eats reader budget for what was meant to be design-feeding material. Fix: hold the grounded default — named protagonist only, no cast or texture. License to name humans is _not_ a license for cast. If the draft grows side-cast or sensory micro-scenes that weren't asked for, excise (or surface as drift to the user).
- **`review` auto-detect fails silently on ambiguous artifacts.** Walkthrough has both `@user:` AND `[[...]]` markers (CC-drafted, then the user added their own design notes in `[[]]` style); auto-detect picks one path and proceeds. Fix: when both marker styles are present, surface the ambiguity and ask which review mode the user wants.
- **`apply` proposes too narrow a diff.** Only creates story drafts; misses that an existing `DESIGN.md` or `README.md` claim needs to be updated to match. Fix: when building the diff, scan supporting design docs for claims the walkthrough contradicts and include them in the diff for approval.
- **`revise` produces a near-identical re-draft.** The user's comments were superficial; the re-imagined walkthrough barely differs from the prior version. This is signal that `revise` was the wrong branch — the right action was probably `apply` (the comments already pointed at design mutations) or `write` (more analysis was needed). Fix: when the re-draft diff is small, mention this to the user and offer to back out.
- **`apply` archives without offering.** Some skill iteration might be tempted to auto-move the dir on apply. Don't. The archive move is offered, never forced — the user might want to keep the dir live for further iteration even after a partial apply.

## Quick reference

| Verb | Output | When |
|------|--------|------|
| (bare) `/walkthrough` | Smart-route: review / draft / ask | Default invocation |
| `/walkthrough new` | Force-fresh draft | Parallel artifact (e.g., for compare) |
| `/walkthrough review [path]` | Analysis in conversation + branch options | Iterate on existing walkthrough |
| `/walkthrough revise [path]` | Fresh walkthrough.md, prior version-asided | Branch: re-imagine the story |
| `/walkthrough apply [path]` | Diff to design surface, batch-approve, archive | Branch: integrate insights into design |
| `/walkthrough help` | Usage block | "How do I use this?" |

**Modes:** `current` / `planned` / `infinity` (default). See [Modes](#modes).

**Voice:** grounded default (named protagonist, no cast/texture). Override in prompt language ("spec-shaped" / "have fun with it"). See [Common mistakes](#common-mistakes) for the cast/texture drift failure mode.

**Tags:**

| Tag | Used by mode | Meaning |
|-----|--------------|---------|
| `[planned]` | `planned` | Item is on the near-term roadmap but not yet shipped. |
| `[extrap]` | `infinity` | Speculation past spec; reader should not treat as commitment. |

**Review-comment markers** (processed by `revise` and `write review file`):

- `<!-- @<username>: <comment> -->` — unseen; will be acked during the next revise / write-review pass
- `<!-- @<username>+seen: <comment> -->` — acknowledged; preserved on the file for provenance

**Embedded human-narrative markers** (processed by `review` on a human-authored walkthrough):

- `[[design-actionable text]]` — author wants this picked up; triaged into the `[[...]]` section of the analysis
- `((parenthetical aside))` — clarifying context for the human reader; not surfaced as action items

**Diátaxis quadrant:** tutorial. If the user actually wants reference / how-to / explanation, this is the wrong skill.
````

(End of Appendix A.)
