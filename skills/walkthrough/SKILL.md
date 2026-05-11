---
name: walkthrough
description: Use when asked to produce a narrative walkthrough of how an application or system is used end-to-end from a specific user's perspective ("walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "narrative description of installing and using"). Tutorial-quadrant docs — story-shaped, learning-oriented — distinct from reference, spec, and how-to. Also handles iterating on existing walkthrough docs via inline-comment review and extracting spec-gap follow-ups.
---

# Walkthrough

Produces tutorial-quadrant narrative docs that show how a real user would install, configure, and use an application end-to-end. Story-shaped, learning-oriented. Distinct from architecture/spec/reference (which live in design docs), step-by-step task instructions (how-to), and conceptual explanation.

## When to use vs. skip

Use for: "walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "describe what installing and using this looks like".

Skip if the user wants architecture/API/spec content (that's reference), step-by-step task instructions for one task (that's how-to), or conceptual explanation (that's explanation).

## Phases

### 1. Orient

Read the project's design surface to ground the narrative. Typical entry points: `README`, `CLAUDE.md`, anything in `docs/` or `design/`. Skip if the user already supplied source material in the prompt.

### 2. Scope

Use `AskUserQuestion` to pin down anything not obvious from project docs or the user's request. Skip any question whose answer is already clear:

- **Perspective**: who is the narrative *for*? (end-user / admin / developer / API consumer / specific role). If the app has multiple user types, surface the candidates and pick one — the others get bottom-section variation notes or separate docs later.
- **Scenario**: primary path. If the app has modes / tiers / flavors / target systems, pick one primary and capture others as bottom-section variation notes.
- **Format**: human-readable narrative (default). Ask whether to also produce an LLM-optimized companion (default: no, can be added later).
- **Depth**: rough length. Default 2–3 pages of text (~1500–2500 words).
- **Output location**: where the doc lives. Default: dated filename like `<YYYY-MM-DD>-walkthrough-<scenario>-<perspective>.md` in `design/notes/`, `docs/walkthroughs/`, or wherever the project keeps informal/snapshot docs.

### 3. Draft

Story-shaped, not spec-shaped. Standard arc:

1. **Install / first contact** — what the user downloads, where it lands, what the first command/click is
2. **Setup / first-run configuration** — first-run rituals, config files written, API keys
3. **Core usage loop** — the main reason the user is here; the rhythm they'll repeat
4. **Variations within the chosen scenario** — branch points the same user might hit
5. **End-state** — what success looks like; what's persisted; what cleanup looks like
6. **Bottom-section variation notes** — short paragraphs on materially different scenarios (other modes, other contexts, other target systems). Not full repeats; just deltas.

Drafting principles:

- **Named protagonist.** Concrete cast for the human version (e.g., "Derek runs `setup`..."). Roles only for the LLM version ("Meta GM runs setup...").
- **Concrete commands and file paths.** Show what the user actually types and what files get created.
- **Tag extrapolations** with `[extrap]` and a brief note when you infer past what the docs settle. Lets the user audit your interpretation.
- **Iceberg discipline.** Describe just enough of each feature for the story to make sense; don't unload spec content into the narrative.

### 4. Save

Write to the file location determined in scope. Confirm the path before writing if it wasn't preset. Don't assume `notes/` or `docs/`; surface the choice.

### 5. (Optional) LLM companion

If the user asked for it, generate a second file with the same arc but a different shape:

- Frontmatter with retrieval metadata (`doc-kind`, `perspective`, `scenario`, `snapshot-date`, `source-anchors`)
- Phases as state declarations: `precondition / actions / artifacts / invariants / failure-modes`
- Roles instead of named characters
- Explicit cross-references to source-of-truth design artifacts
- `[extrap]` tags retained inline
- Bottom section explaining how this doc differs from the human companion

## Iterate mode

Triggered when the user has reviewed an existing walkthrough and wants feedback incorporated.

**Comment convention.** Reviewer comments live as inline HTML comments next to the passages they target:

```markdown
... Derek's ready to run his Tuesday group through a campaign.
<!-- @derek: player onboarding should happen here, before campaign add -->
He calls it *Tides of Azure*.
```

HTML comments don't render in markdown previews, so the doc stays presentable. Username defaults to `git config user.name` (lowercased); the skill greps for `<!-- @<username>:`.

Process:

1. Grep the doc for `<!-- @<username>:` markers
2. For each marker, integrate the comment into the surrounding prose and strip the marker
3. Append a `<docname>-review-log.md` sibling recording each comment and how it was handled — preserves the audit trail across iterations
4. Flag anything that surfaces a real spec gap as a follow-up candidate (defer to follow-ups mode unless trivially actionable now)
5. Show the diff and stop. Don't auto-commit.

If no markers exist but the doc has been edited directly, surface the diff and ask whether to learn from the edits.

## Follow-ups mode

Triggered when the user says the doc is "good enough for now" or explicitly asks for follow-up extraction.

Scan the doc + review-log for: `[extrap]` tags, resolved comments that surfaced gaps, and open questions raised during drafting. Triage into:

- **Candidate new specs / stories** — design-gap material that wants a real design doc
- **Candidate blockers / helping-hands items** — items the user must do (per project convention)
- **Open design questions** — to surface in the project's canonical design questions log

Stage the triage as a markdown list with suggested file locations. Ask the user which to file. Don't write into spec/story/blocker directories without explicit per-item approval.

## Self-bootstrap

On second invocation in the same project: if scoping conversations are repeating the same answers (same perspective, same output location, same naming convention), offer to write a thin project-specific wrapper skill (`walkthrough-<project-slug>`) that pre-fills those answers. User decides whether to bother — extraction is opt-in, not automatic.

## Common mistakes

- **Drifts into architecture/spec content.** Narrative becomes a reorganized DESIGN.md. Fix: re-center on the protagonist's actions and what they see.
- **Skips the scoping pass.** Produces a generic narrative that satisfies no specific user type. Fix: always confirm perspective + scenario before drafting unless they're obvious.
- **Forgets variation notes.** Assumes the chosen scenario covers all cases. Fix: always end with bottom-section notes on materially different scenarios, even if short.
- **Untagged extrapolation.** Implies behaviors the docs don't settle; reader trusts the narrative as spec. Fix: `[extrap]` every speculative passage with a one-line note on what's being inferred.
- **Auto-files follow-ups.** Skill writes stories or todos into spec directories without approval. Fix: stage and surface; user files.
- **Generates LLM companion by default.** Doubles output for a thing the user may not want. Fix: ask; default no.

## Quick reference

| Phase | Output | When |
|-------|--------|------|
| Orient | Internal context | Always |
| Scope | Perspective, scenario, format, depth, location | When unclear |
| Draft | Narrative doc | Primary use |
| Save | File at chosen path | Primary use |
| LLM companion | Second file with structured shape | If requested |
| Iterate | Revised draft + review-log | On re-invocation with comments |
| Follow-ups | Triaged list of spec-gap candidates | At "good enough for now" |

**Review comment marker:** `<!-- @<username>: <comment> -->` (invisible in markdown render, grep-friendly).

**Diátaxis quadrant:** tutorial. If the user actually wants reference / how-to / explanation, this is the wrong skill.
