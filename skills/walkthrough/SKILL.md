---
name: walkthrough
description: Use when asked to produce a narrative walkthrough of how an application or system is used end-to-end from a specific user's perspective ("walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "narrative description of installing and using"). Tutorial-quadrant docs — story-shaped, learning-oriented — distinct from reference, spec, and how-to. Also handles iterating on existing walkthrough docs via inline-comment review, cleaning processed comments, and extracting spec-gap follow-ups.
---

<!-- Maintenance: SKILL.md loads on every invocation. Before adding mass, prefer compressing in place or extracting sub-files (see `trajectory.md` as precedent for load-on-demand sub-procedures). Check size with `wc -w SKILL.md`; this skill is structurally larger than typical due to multiple verbs + modes — keep growth justified. -->

# Walkthrough

Produces tutorial-quadrant narrative docs that show how a real user would install, configure, and use an application end-to-end. Story-shaped, learning-oriented. Distinct from architecture/spec/reference (which live in design docs), step-by-step task instructions (how-to), and conceptual explanation.

## When to use vs. skip

Use for: "walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "describe what installing and using this looks like".

Skip if the user wants architecture/API/spec content (that's reference), step-by-step task instructions for one task (that's how-to), or conceptual explanation (that's explanation).

## Modes

A walkthrough's *temporal stance* — what slice of the app it describes — is chosen during scoping. Mode is metadata of the doc, not a verb; you can `iterate` on any mode.

| Mode | Sources | Tagging | When to pick it |
|------|---------|---------|-----------------|
| `current` | Code + README + shipped behavior. No speculative design docs, no draft stories. | None — refuse to extrapolate. If the code doesn't settle it, ask or omit. | "How does this work *today*?" — onboarding readers to the live app, dogfooding what actually shipped, support docs. |
| `planned` | `current` sources + near-term planned work (`stories/ready/`, `stories/drafts/`, roadmap docs the project treats as committed). | `[planned]` for not-yet-shipped items. No `[extrap]`. | "How will this work *next milestone*?" — sequencing reviews, sanity-checking the next chunk, scoping decisions. |
| `infinity` (default) | Everything: code + all stories + speculative design docs + extrapolation past spec. | `[extrap]` for anything past spec. | "What does this become *eventually*?" — selling the vision, finding spec gaps, North Star docs. Preserves the prior `v-infinity-with-progression-notes` behavior. |
| `trajectory` | Produces a four-artifact set built iteratively. See `trajectory.md` (load when chosen). | Inherits `[planned]` + `[extrap]`; synthesis surfaces deltas. | "Show me the journey." — comparing eras side-by-side. Heavier (four artifacts); opt-in. |

**Default.** `infinity` for actively-developing projects (back-compat with the previous skill behavior). The framing-note at the top of an `infinity` doc explains what's shipping now vs. described-as-future. Override only on explicit user request.

**Framing-note (every mode).** First paragraph of the doc declares the slice the reader is in, e.g.:
- `current`: "This walkthrough describes the app as it ships today (commit `<sha>` / `<date>`)."
- `planned`: "...as planned through milestone `<name>`. `[planned]` marks items not yet shipped."
- `infinity`: "...as currently conceived end-state. `[extrap]` marks speculation past spec."
- `trajectory`: synthesis sibling explains the four-artifact set.

**Mode + verb interaction.** A doc's mode is fixed at draft time and preserved through `iterate`. `clean-comments` and `follow-ups` are mode-agnostic. `trajectory` is the only mode that produces multiple artifacts in one run.

**Back-compat.** Existing walkthrough files without a mode suffix in the filename are treated as `infinity`. Don't rename them retroactively.

## Routing

Four verbs. Bare invocation is smart-routed.

| Invocation | Action |
|---|---|
| `/walkthrough` (bare) | If a walkthrough artifact exists in the expected location (see auto-discovery), default to **iterate**. Else → **draft new**. |
| `/walkthrough new` | **Force-fresh draft** regardless of what exists. Dated filename naturally avoids collision. Use for comparison runs (parallel artifacts). |
| `/walkthrough clean-comments [path]` | Strip `<!-- @<user>+seen: -->` markers; with confirmation, also bare `<!-- @<user>: -->` markers. Explicit-only; never auto-runs. |
| `/walkthrough follow-ups [path]` | Triage `[extrap]` tags + review-log resolved items + open questions into candidate stories / helping-hands / design questions. Stage; user files. |

**Auto-discovery (when no path is given to iterate / clean-comments / follow-ups):**

1. Search order, first existing root wins: `design/notes/`, `notes/`, `docs/walkthroughs/`, `docs/`.
2. Within that root, identify candidates by:
   - `<!-- @<user>:` or `<!-- @<user>+seen:` markers (iterate / clean-comments signal)
   - `[extrap]` or `[planned]` tags or a sibling `<docname>-review-log.md` (follow-ups signal)
   - Filename pattern (`*walkthrough*`, `*narrative*`) or frontmatter (`doc-kind: narrative-walkthrough`) as fallback
3. Single match → use it. Multiple → `AskUserQuestion` with last-modified date **and mode** (inferred from filename suffix, or `infinity` if un-suffixed). Zero → ask whether to draft new.

## Draft new (default for bare invocation when no prior artifact exists)

### 1. Orient

Read the project's design surface to ground the narrative. Typical entry points: `README`, `CLAUDE.md`, anything in `docs/` or `design/`. Skip if the user already supplied source material in the prompt.

### 2. Scope

Use `AskUserQuestion` to pin down anything not obvious from project docs or the user's request. Skip any question whose answer is already clear:

- **Mode**: temporal stance — `current` / `planned` / `infinity` (default) / `trajectory`. See [Modes](#modes). Don't ask if the user's phrasing already pins it ("how does this work today" → `current`; "what's it look like when finished" → `infinity`). Default to `infinity` for actively-developing projects.
- **Perspective**: who is the narrative *for*? (end-user / admin / developer / API consumer / specific role). If the app has multiple user types, surface the candidates and pick one — the others get bottom-section variation notes or separate docs later.
- **Scenario**: primary path. If the app has modes / tiers / flavors / target systems, pick one primary and capture others as bottom-section variation notes.
- **Format**: human-readable narrative (default). Ask whether to also produce an LLM-optimized companion (default: no, can be added later).
- **Depth**: rough length. Default 2–3 pages of text (~1500–2500 words).
- **Output location**: dated filename like `<YYYY-MM-DD>-walkthrough-<scenario>-<perspective>[-<mode>].md` in `design/notes/`, `docs/walkthroughs/`, or wherever the project keeps informal/snapshot docs. Mode suffix omitted for `infinity` (back-compat); included for `current` / `planned` / `trajectory`.

### 3. Draft

Story-shaped, not spec-shaped. **Framing follows the chosen mode** (see [Modes](#modes)): open with a one-paragraph framing-note declaring the slice, then honor that mode's sourcing + tagging rules. Reminder of the rules:

- `current` — refuse to extrapolate. If the code doesn't settle a behavior, ask or omit. No `[extrap]`.
- `planned` — tag not-yet-shipped items with `[planned]`. Speculative material (past the next milestone) is out of scope.
- `infinity` (default) — describe the app as it would look when "done as currently conceived." `[extrap]` for anything past spec. The top-of-doc framing-note explains what's shipping now vs. described-as-future. This is the back-compat behavior; preserve it unless mode says otherwise.
- `trajectory` — load `trajectory.md` for the iterative four-artifact procedure.

Standard arc:

1. **Install / first contact** — what the user downloads, where it lands, what the first command/click is
2. **Setup / first-run configuration** — first-run rituals, config files written, API keys
3. **Core usage loop** — the main reason the user is here; the rhythm they'll repeat
4. **Variations within the chosen scenario** — branch points the same user might hit
5. **End-state** — what success looks like; what's persisted; what cleanup looks like
6. **Bottom-section variation notes** — short paragraphs on materially different scenarios (other modes, other contexts, other target systems). Not full repeats; just deltas.

Drafting principles:

- **Named protagonist** for the human version (e.g., "Derek runs `setup`..."). Roles only for the LLM version ("Meta GM runs setup...").
- **Concrete commands and file paths.** Show what the user actually types and what files get created.
- **Tag extrapolations** with `[extrap]` and a brief inline note when you infer past what the docs settle.
- **Iceberg discipline.** Describe just enough of each feature for the story to make sense; don't unload spec content.

### 4. Save

Write to the file location determined in scope. Confirm the path before writing if it wasn't preset.

### 5. (Optional) LLM companion

If the user asked for it, generate a second file with the same arc but a different shape:

- Frontmatter with retrieval metadata (`doc-kind`, `perspective`, `scenario`, `snapshot-date`, `source-anchors`)
- Phases as state declarations: `precondition / actions / artifacts / invariants / failure-modes`
- Roles instead of named characters
- Explicit cross-references to source-of-truth design artifacts
- `[extrap]` tags retained inline
- Bottom section explaining how this doc differs from the human companion

## Trajectory mode

Documented in `trajectory.md`. Load that file before proceeding when the user has chosen `trajectory` during scoping — it covers the iterative `current` → `planned` → `infinity` build, the synthesis sibling's shape, spine-divergence handling, and cost guidance. Don't try to reconstruct from memory; the procedure has specific ordering and tagging rules that matter.

## Iterate

Triggered when the user has reviewed an existing walkthrough and wants feedback incorporated. Default for bare `/walkthrough` when an artifact exists.

**Comment convention.** Reviewer comments live as inline HTML comments next to the passages they target:

```markdown
... Derek's ready to run his Tuesday group through a campaign.
<!-- @derek: player onboarding should happen here, before campaign add -->
He calls it *Tides of Azure*.
```

HTML comments don't render in markdown previews, so the doc stays presentable.

**Username discovery.** First, scan the doc for whatever `@<word>:` markers actually appear; if there's a single distinct prefix, use it (handles e.g. `@derek` when `git config user.name` returns `iamgroot`). Else fall back to `git config user.name` (lowercased), then `git config user.email`'s local-part, then `$USER`. Else ask.

**Uncommitted-artifact safety check (precondition; hard stop).** Before mutating the target, run `git status --porcelain <path>`. If the target has uncommitted changes, stop and ask the user to either commit or explicitly accept loss. Iterate rewrites prose; running it on dirty working state risks destroying un-saved work with no clean recovery path.

**Preserve-don't-strip.** Iterate marks reviewed comments rather than removing them. For each `<!-- @<user>: <comment> -->`:

1. Integrate the comment into the surrounding prose.
2. **Rewrite the marker in place** from `@<user>:` to `@<user>+seen:` (preserve the comment text verbatim). The inline context stays visible — a reader can tell which paragraph each comment hung off — while the prefix signals the skill has processed it.
3. Record the disposition in the review-log (see below). Markers are not the disposition record; the log is. **One marker variant only** — no `+deferred:` / `+ack:` subtypes. Disposition richness lives in the log.

Stripping seen markers is a separate, explicit operation (`/walkthrough clean-comments`).

**Review-log.** Append a `<docname>-review-log.md` sibling:

- **Framing-decision preamble** at the top — any reframing decisions (e.g., mode choice or mode-change request) called out before the per-comment table. Mode itself is preserved through iterate; explicit mode changes are a re-draft, not an iterate.
- **Tabular per-comment record:** `# | Topic | What changed` rows for integrated comments, plus sections for deferred / follow-up-candidates / positive-feedback / skill-level-meta-issues.

After integration: show diff and stop. Don't auto-commit. Flag anything that surfaces a real spec gap as a follow-up candidate (defer to follow-ups verb unless trivially actionable now).

If no markers exist but the doc has been edited directly, surface the diff and ask whether to learn from the edits.

## Clean-comments

Explicit `/walkthrough clean-comments [path]`. Never auto-runs.

1. Auto-discovery if path omitted.
2. Default: strip all `<!-- @<user>+seen: ... -->` markers (the processed ones).
3. With `--strict` or explicit confirmation in the conversation: also strip bare `<!-- @<user>: ... -->` markers (un-processed comments). Without confirmation, surface those as "not yet processed; run iterate first?" rather than stripping.
4. Show diff. Don't auto-commit.

## Follow-ups

Explicit `/walkthrough follow-ups [path]`, or user phrases like "good enough for now" / "extract follow-ups".

Scan the doc + sibling review-log for: `[extrap]` tags, resolved comments that surfaced gaps, and open questions raised during drafting. Triage into:

- **Candidate new specs / stories** — design-gap material; suggest `stories/drafts/` or equivalent.
- **Candidate blockers / helping-hands items** — items the user must do (per project convention).
- **Open design questions** — to surface in the project's canonical questions log (e.g., DESIGN.md "Open Questions").

Stage the triage as a markdown list with suggested file locations. Ask the user which to file. **Don't write into spec/story/blocker directories without explicit per-item or per-bucket approval.**

## Out of scope for this skill

- **Archival / moving prior narratives** (to `deprecated/` or elsewhere) — manual workflow decision; the skill does not move files between locations.

## Self-bootstrap

On second invocation in the same project: if scoping conversations are repeating the same answers (same perspective, same output location, same naming convention), offer to write a thin project-specific wrapper skill (`walkthrough-<project-slug>`) that pre-fills those answers. User decides whether to bother — extraction is opt-in.

## Common mistakes

- **Drifts into architecture/spec content.** Narrative becomes a reorganized DESIGN.md. Fix: re-center on the protagonist's actions and what they see.
- **Skips the scoping pass.** Produces a generic narrative that satisfies no specific user type. Fix: confirm perspective + scenario before drafting unless they're obvious.
- **Forgets variation notes.** Assumes the chosen scenario covers all cases. Fix: always end with bottom-section notes on materially different scenarios.
- **Untagged extrapolation.** Implies behaviors the docs don't settle; reader trusts the narrative as spec. Fix: `[extrap]` every speculative passage.
- **Mode bleed.** `current` mode quietly imports planned behavior; `planned` mode quietly imports speculation. Fix: hold the line on what each mode sources — when in doubt for `current`, ask or omit; when in doubt for `planned`, defer to `infinity`.
- **Missing framing-note.** Reader can't tell which era they're in. Fix: every mode opens with a one-paragraph framing-note declaring the slice.
- **Picks `trajectory` reflexively.** Generates four artifacts when the user wanted one. Fix: confirm trajectory before running; most asks want a single mode.
- **Trajectory ignores spine.** Re-drafts `planned` and `infinity` from scratch, producing three independent narratives instead of three layered versions of the same one. Fix: each layer uses the prior layer as its spine; only the deltas change.
- **Strips markers during iterate.** Removes inline context a future reader (or future iterate pass) might want. Fix: rewrite `@<user>:` → `@<user>+seen:` in place; use the separate `clean-comments` verb when removal is wanted.
- **Iterates over dirty working state.** Destroys un-saved edits. Fix: hard-stop if `git status` shows the target dirty; ask the user to commit or accept loss.
- **Auto-files follow-ups.** Skill writes stories/todos into spec directories without approval. Fix: stage and surface; user files.
- **Generates LLM companion by default.** Doubles output for a thing the user may not want. Fix: ask; default no.

## Quick reference

| Verb | Output | When |
|------|--------|------|
| (bare) `/walkthrough` | Routes to iterate (if existing) or draft new | Default invocation |
| `/walkthrough new` | Force-fresh draft | Comparison / parallel artifact |
| `/walkthrough clean-comments [path]` | Stripped seen markers | Explicit cleanup |
| `/walkthrough follow-ups [path]` | Triaged spec-gap candidates | After iterate, at "good enough for now" |

| Phase | Output |
|-------|--------|
| Orient | Internal context |
| Scope | Mode, perspective, scenario, format, depth, location |
| Draft | Narrative doc (mode-aware framing; `infinity` is default) |
| Save | File at chosen path (mode suffix when non-default) |
| LLM companion | Second file with structured shape (opt-in) |

**Modes:** `current` / `planned` / `infinity` (default) / `trajectory`. Mode sets sourcing + tagging; see [Modes](#modes).

| Tag | Used by mode | Meaning |
|-----|--------------|---------|
| `[planned]` | `planned`, `trajectory` | Item is on the near-term roadmap but not yet shipped. |
| `[extrap]` | `infinity`, `trajectory` | Speculation past spec; reader should not treat as commitment. |

**Review-comment markers:**
- `<!-- @<username>: <comment> -->` — unseen, pending iterate
- `<!-- @<username>+seen: <comment> -->` — processed; disposition in review-log; remove via `clean-comments`

**Diátaxis quadrant:** tutorial. If the user actually wants reference / how-to / explanation, this is the wrong skill.
