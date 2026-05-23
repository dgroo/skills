---
name: walkthrough
description: Use when asked to produce a narrative walkthrough of how an application or system is used end-to-end from a specific user's perspective ("walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc"). Tutorial-quadrant docs — story-shaped, learning-oriented — distinct from reference, spec, and how-to. Also handles gap-analysis (`check` verb) comparing a human-authored narrative to the codebase + design docs, cleaning processed review comments, and extracting spec-gap follow-ups. Comment-driven iteration of LLM-drafted walkthroughs lives in the sibling `/integrate-comments` skill.
---

<!-- Maintenance: SKILL.md loads on every invocation. Before adding mass, prefer compressing in place or extracting sub-files (see `trajectory.md` as precedent for load-on-demand sub-procedures). Check size with `wc -w SKILL.md`; this skill is structurally larger than typical due to multiple verbs + modes — keep growth justified. -->

# Walkthrough

Produces tutorial-quadrant narrative docs that show how a real user would install, configure, and use an application end-to-end. Story-shaped, learning-oriented. Distinct from architecture/spec/reference (which live in design docs), step-by-step task instructions (how-to), and conceptual explanation.

## When to use vs. skip

Use for: "walk me through using X", "how would a new user start with Y", "narrative of usage", "user journey doc", "describe what installing and using this looks like".

Skip if the user wants architecture/API/spec content (that's reference), step-by-step task instructions for one task (that's how-to), or conceptual explanation (that's explanation).

## Modes

A walkthrough's _temporal stance_ — what slice of the app it describes — is chosen during scoping. Mode is metadata of the doc, not a verb; iteration (via `/integrate-comments`) preserves whatever mode the doc was drafted in.

| Mode                 | Sources                                                                                                                         | Tagging                                                                   | When to pick it                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `current`            | Code + README + shipped behavior. No speculative design docs, no draft stories.                                                 | None — refuse to extrapolate. If the code doesn't settle it, ask or omit. | "How does this work _today_?" — onboarding readers to the live app, dogfooding what actually shipped, support docs.                                               |
| `planned`            | `current` sources + near-term planned work (`stories/ready/`, `stories/drafts/`, roadmap docs the project treats as committed). | `[planned]` for not-yet-shipped items. No `[extrap]`.                     | "How will this work _next milestone_?" — sequencing reviews, sanity-checking the next chunk, scoping decisions.                                                   |
| `infinity` (default) | Everything: code + all stories + speculative design docs + extrapolation past spec.                                             | `[extrap]` for anything past spec.                                        | "What does this become _eventually_?" — selling the vision, finding spec gaps, North Star docs. Preserves the prior `v-infinity-with-progression-notes` behavior. |
| `trajectory`         | Produces a four-artifact set built iteratively. See `trajectory.md` (load when chosen).                                         | Inherits `[planned]` + `[extrap]`; synthesis surfaces deltas.             | "Show me the journey." — comparing eras side-by-side. Heavier (four artifacts); opt-in.                                                                           |

**Default.** `infinity` for actively-developing projects (back-compat with the previous skill behavior). The framing-note at the top of an `infinity` doc explains what's shipping now vs. described-as-future. Override only on explicit user request.

**Framing-note (every mode).** First paragraph of the doc declares the slice the reader is in, e.g.:

- `current`: "This walkthrough describes the app as it ships today (commit `<sha>` / `<date>`)."
- `planned`: "...as planned through milestone `<name>`. `[planned]` marks items not yet shipped."
- `infinity`: "...as currently conceived end-state. `[extrap]` marks speculation past spec."
- `trajectory`: synthesis sibling explains the four-artifact set.

**Mode + verb interaction.** A doc's mode is fixed at draft time. Iteration on existing walkthroughs (via `/integrate-comments`) preserves the mode. `clean-comments` and `follow-ups` are mode-agnostic. `trajectory` is the only mode that produces multiple artifacts in one run.

**Back-compat.** Existing walkthrough files without a mode suffix in the filename are treated as `infinity`. Don't rename them retroactively.

## Registers

A walkthrough's _register_ — how story-shaped vs. spec-shaped the prose is — is chosen during scoping. Orthogonal to mode: any mode can be drafted in any register.

| Register             | Protagonist                               | Side-cast / sensory texture | Word budget | When to pick it                                                                                                      |
| -------------------- | ----------------------------------------- | --------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------- |
| `spec`               | Roleless ("the Meta GM does X")           | None                        | ~1000–1500  | Walkthrough's job is to feed design work — surface phases + decision points without narrative weight.                |
| `grounded` (default) | Named protagonist as anchor only          | None                        | ~1800–2500  | Default. Named protagonist provides a reading anchor; no supporting cast, no origin scenes, no sensory micro-scenes. |
| `storied`            | Named protagonist + named supporting cast | Permitted (opt-in)          | ~3000–4500  | Selling-the-vision / North Star / pitch-shaped docs where the texture _is_ the point. Explicit ask, not default.     |

**Default.** `grounded`. Named protagonist keeps prose readable; absence of side-cast and sensory micro-scenes keeps focus on the application's surface. `storied` is opt-in — right register for pitches and vision docs, reader-budget overhead when the goal is feeding design work. `spec` is for cases where even a named protagonist is overhead (e.g., feeding a /plan-eng-review).

**Mode × register.** Independent. `infinity-spec` is a valid draft (spec-shaped speculation past spec); `current-storied` is a valid draft (richly textured snapshot of what ships today). Don't conflate.

**Skip the scoping question when the user pins it.** "Matter-of-fact" / "concise" / "no fluff" / "spec-shaped" → `spec`. "Have fun" / "fleshed out" / "make it a story" / "with characters" → `storied`. Otherwise ask, default `grounded`. Note: "feel free to name the humans" is _license_ for naming, not a register signal — it does not by itself promote `grounded` to `storied`.

## Routing

Six verbs. Bare invocation is smart-routed.

| Invocation                           | Action                                                                                                                                                                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/walkthrough` (bare)                | If a walkthrough artifact with unseen `<!-- @<user>: -->` markers exists in the expected location (see auto-discovery), **hand off to `/integrate-comments`** with that path. Else → **draft new**.                      |
| `/walkthrough new`                   | **Force-fresh draft** regardless of what exists. Dated filename naturally avoids collision. Use for comparison runs (parallel artifacts).                                                                                |
| `/walkthrough integrate [path]`      | **Integrate review comments.** Explicit alias for `/integrate-comments [path]` — same underlying skill, same behavior. Exists so users who think "walkthrough" first don't have to remember the sibling skill's name.    |
| `/walkthrough check [path]`          | **Gap-analysis.** Compare a human-authored narrative against the codebase + design docs. Parses `[[design-actionable]]` and `((aside))` markers. Bidirectional (narrative→code and code→narrative). See [Check](#check). |
| `/walkthrough clean-comments [path]` | Strip `<!-- @<user>+seen: -->` markers; with confirmation, also bare `<!-- @<user>: -->` markers. Explicit-only; never auto-runs. Works on any annotated markdown, not just walkthroughs.                                |
| `/walkthrough follow-ups [path]`     | Triage `[extrap]` tags + review-log resolved items + open questions into candidate stories / helping-hands / design questions. Stage; user files.                                                                        |
| `/walkthrough help`                  | Print unix-style usage (see [Help](#help)).                                                                                                                                                                              |

**Iterating on an existing walkthrough.** Use `/walkthrough integrate [path]` (or `/integrate-comments [path]` directly — same skill). That skill owns the comment-driven workflow (marker rewrite, review-log emission, no-fabrication guardrail, uncommitted-state safety check) and is content-type-agnostic — same mechanics work on survey drafts, design notes, etc.

**Auto-discovery (when no path is given to clean-comments / follow-ups):**

1. Search order, first existing root wins: `design/walkthroughs/`, `design/notes/`, `notes/`, `docs/walkthroughs/`, `docs/`. When the root is `design/walkthroughs/`, the candidate unit is the per-walkthrough subdirectory (`<date>-<slug>/`), not a single file.
2. Within that root, identify candidates by:
   - `<!-- @<user>+seen:` markers (clean-comments signal)
   - `[extrap]` or `[planned]` tags or a sibling `<docname>-review-log.md` (follow-ups signal)
   - Filename pattern (`*walkthrough*`, `*narrative*`) or frontmatter (`doc-kind: narrative-walkthrough`) as fallback
   - For `design/walkthroughs/`, treat every `<date>-<slug>/walkthrough.md` (or any `.md` under the dir) as a walkthrough by virtue of location — the per-dir layout _is_ the doc-kind marker.
3. Single match → use it. Multiple → `AskUserQuestion` with last-modified date **and mode** (inferred from filename suffix, dir-slug suffix, or `infinity` if un-suffixed). Zero → ask whether to draft new.

**Bare-invocation hand-off detail.** When bare `/walkthrough` finds an existing walkthrough artifact with unseen `<!-- @<user>: -->` markers, don't run integrate inline — surface the find ("found walkthrough at X with N unseen comments; handing off to /integrate-comments") and invoke that skill. If the artifact exists but has no unseen markers, ask whether the user wants `clean-comments`, `follow-ups`, or to draft a fresh walkthrough.

## Draft new (default for bare invocation when no prior artifact exists)

### 1. Orient

Read the project's design surface to ground the narrative. Typical entry points: `README`, `CLAUDE.md`, anything in `docs/` or `design/`. Skip if the user already supplied source material in the prompt.

**Don't read prior walkthroughs during orient.** If `design/walkthroughs/` (or equivalent) exists, do not include its contents in the orient pass — those are tutorial-quadrant docs, not the canonical design surface, and reading them at orient time biases the new draft toward the prior one's framing. The CLAUDE.md / `walkthroughs/README.md` convention in projects that use this layout makes this explicit (read-with-permission, same shape as `archived/`/`deprecated/`). Even in projects without that convention, hold the line. The exception is the _one_ walkthrough the user names as a comparison target — see the next step.

### 2. Scope

Use `AskUserQuestion` to pin down anything not obvious from project docs or the user's request. Skip any question whose answer is already clear:

- **Comparison target / parallel artifact** _(first, before everything else)_ — if the user mentions "compare against," "parallel to," "diverge from," "ignore X but generate Y," or any specific prior narrative, **identify the comparison target singularly before scoping anything else**. Don't infer scope from "the most recently touched narrative" or from filenames visible via `ls`; visible existence ≠ scope signal. If there are multiple candidate prior narratives (e.g., several `*-narrative-*` files), `AskUserQuestion` which one is the target. If the user says "ignore X," confirm what's being ignored — the file (as input), the topic, or both — the answers shape scope very differently. Common failure mode: parsing "ignore the auth narrative" as "don't read that file" while still anchoring on auth as the topic.
- **Mode**: temporal stance — `current` / `planned` / `infinity` (default) / `trajectory`. See [Modes](#modes). Don't ask if the user's phrasing already pins it ("how does this work today" → `current`; "what's it look like when finished" → `infinity`). Default to `infinity` for actively-developing projects.
- **Perspective**: who is the narrative _for_? (end-user / admin / developer / API consumer / specific role). If the app has multiple user types, surface the candidates and pick one — the others get bottom-section variation notes or separate docs later.
- **Scenario**: primary path. If the app has modes / tiers / flavors / target systems, pick one primary and capture others as bottom-section variation notes.
- **Format**: human-readable narrative (default). Ask whether to also produce an LLM-optimized companion (default: no, can be added later).
- **Register**: narrative voice — `spec` / `grounded` (default) / `storied`. See [Registers](#registers). Skip the question only if the user's phrasing pins it ("matter-of-fact" → `spec`; "have fun" / "make it a story" → `storied`). License to name humans is _not_ a register signal.
- **Depth**: rough length. Default flows from register (`spec` ~1000–1500, `grounded` ~1800–2500, `storied` ~3000–4500); override only on explicit user ask.
- **Output location**: if `design/walkthroughs/` exists, use the per-walkthrough-dir layout: `design/walkthroughs/<YYYY-MM-DD>-<slug>/walkthrough.md`, with `<slug>` = mode (`current`/`planned`/`infinity`) for whole-product walkthroughs or `<topic>` for scoped walkthroughs. Sibling artifacts (`walkthrough-check.md`, `walkthrough-review-log.md`, LLM companion) live alongside in the same dir. Otherwise, fall back to legacy: dated filename like `<YYYY-MM-DD>-walkthrough-<scenario>-<perspective>[-<mode>].md` in `design/notes/`, `docs/walkthroughs/`, or wherever the project keeps informal/snapshot docs. Mode suffix omitted for `infinity` (back-compat); included for `current` / `planned` / `trajectory`.

### 3. Draft

Shape follows two orthogonal axes: **mode** (see [Modes](#modes)) sets temporal stance and sourcing rules; **register** (see [Registers](#registers)) sets narrative voice and word budget. Open with a one-paragraph framing-note declaring the mode-slice, then honor both the mode's tagging rules and the register's voice rules. Reminder of the mode rules:

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

- **Register drives voice.** The chosen register sets named-vs-roleless protagonist, whether supporting cast is permitted, whether sensory micro-scenes (origin stories, screenshot-taking, partner-cameos, atmospheric details) are permitted, and the word budget. Hold the line. A `grounded` draft that grows a Reddit-thread origin scene is silently a `storied` draft — either re-scope or excise.
- **LLM-companion variant** uses roles ("Meta GM runs setup...") regardless of human-companion register.
- **Concrete commands and file paths.** Show what the user actually types and what files get created. (Mandatory in all registers — even `spec`.)
- **Tag extrapolations** with `[extrap]` and a brief inline note when you infer past what the docs settle.
- **Iceberg discipline.** Describe just enough of each feature for the story to make sense; don't unload spec content.

### 4. Save

Write to the file location determined in scope. Confirm the path before writing if it wasn't preset. When using the `design/walkthroughs/<date>-<slug>/` layout, create the dir as part of the save step — `mkdir -p` plus the narrative file in one motion. Sibling artifacts (check output, review-log, LLM companion) land in the same dir on later runs, not as siblings of the narrative file elsewhere.

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

## Integrate

Explicit `/walkthrough integrate [path]`, or the bare `/walkthrough` smart-route when an existing walkthrough has unseen `<!-- @<user>: -->` markers. Both routes invoke the sibling `/integrate-comments` skill — the explicit verb exists so users who think "walkthrough" first don't have to remember the sibling skill's name. No behavior difference between `/walkthrough integrate` and `/integrate-comments` directly; pick whichever you remember first.

That skill handles: username discovery, uncommitted-state safety check, marker rewrite (`@<user>:` → `@<user>+seen:` in place), review-log emission with framing-decision preamble, and the no-fabrication guardrail. Mode metadata on the walkthrough is preserved — `/integrate-comments` reads framing notes but doesn't rewrite modes.

## Clean-comments

Explicit `/walkthrough clean-comments [path]`. Never auto-runs.

1. Auto-discovery if path omitted.
2. Default: strip all `<!-- @<user>+seen: ... -->` markers (the processed ones).
3. With `--strict` or explicit confirmation in the conversation: also strip bare `<!-- @<user>: ... -->` markers (un-processed comments). Without confirmation, surface those as "not yet processed; run `/integrate-comments` first?" rather than stripping.
4. Show diff. Don't auto-commit.

## Follow-ups

Explicit `/walkthrough follow-ups [path]`, or user phrases like "good enough for now" / "extract follow-ups".

Scan the doc + sibling review-log for: `[extrap]` tags, resolved comments that surfaced gaps, and open questions raised during drafting. Triage into:

- **Candidate new specs / stories** — design-gap material; suggest `stories/drafts/` or equivalent.
- **Candidate blockers / helping-hands items** — items the user must do (per project convention).
- **Open design questions** — to surface in the project's canonical questions log (e.g., DESIGN.md "Open Questions").

Stage the triage as a markdown list with suggested file locations. Ask the user which to file. **Don't write into spec/story/blocker directories without explicit per-item or per-bucket approval.**

## Check

Gap-analysis verb. Inverse of `write` (LLM reads code, drafts narrative) — here the _human_ has written a narrative of how they envision using the app, and the skill compares it against the actual codebase + design docs to surface drift.

The point: a human-authored narrative encodes intent the rest of the design surface may not capture. Comparing it three-ways (narrative ↔ design docs ↔ code) catches silent drift in any direction — features the narrative implies that don't exist, features the code has that the narrative omits, and design-doc-vs-narrative-vs-code disagreements that no unidirectional review would surface.

### Inputs

1. **A human-authored narrative.** Markdown file. Either passed as a path argument or auto-discovered (search order: same locations as the auto-discovery rules in [Routing](#routing); prefer files whose preamble announces a human author or whose markers are `[[...]]` / `((...))` rather than `<!-- @user: -->`).
2. **The codebase.** Inferred from `$CWD` / git root.
3. **The design surface.** README, `design/` or `docs/` trees, anything the project treats as design source-of-truth. Skim — don't ingest exhaustively.

If the narrative path is ambiguous, ask. Don't guess between candidates.

### Marker parsing

Default conventions (override by the narrative's own preamble if it declares different markers):

- **`[[design-actionable text]]`** — embedded design notes the author wants picked up. Treat like `follow-ups`'s `[extrap]` triage: each `[[...]]` is a candidate story / helping-hand / design question. Surface them in the output's triage section.
- **`((parenthetical aside))`** — clarifying context for the human reader, **not** design-actionable. Read as scoping signal (helps disambiguate what the narrative means) but don't produce output items from `(())` content.
- **`<!-- @user: -->`** — review markers from another flow; ignore in `check` (they're owned by `/integrate-comments`). If present, surface a one-liner: "narrative has unseen review markers; consider `/integrate-comments` separately."

If the narrative's preamble announces its own markup conventions (as many human-authored narratives do), honor those declarations and note the override in the output's framing-note.

### Procedure

1. **Read the narrative end-to-end.** Capture its implied surface: commands the user types, files the app creates, behaviors invoked, modes / states / entry points referenced.
2. **Skim the design surface.** README + design index + any `design/` doc whose title overlaps a narrative-named verb or feature. Don't try to load everything.
3. **Skim the code.** Targeted greps for narrative-named commands, file paths, config keys. Identify entry points and primary loops.
4. **Build the three-way map.** For each behavior the narrative implies, record what design-docs say (if anything) and what code shows (if anything). For each feature the code has, record whether the narrative mentions it.
5. **Produce the output artifact** (see below).
6. **Surface priority.** Top of artifact: a short "recommended pickup order" — the 3-5 highest-leverage gaps. Derived from the tables, not invented.

### Output

Write to `<narrative-stem>-check.md` as a sibling of the narrative. Structure:

1. **Framing-note** — one paragraph: narrative source path, snapshot commit, declared markers (and any overrides from preamble), scope of code/design skim.
2. **Recommended pickup order** — 3–5 highest-leverage findings, each one line, with a pointer to the row in the tables below.
3. **N → C gaps** (narrative-to-code) — table: behavior the narrative implies, narrative anchor (file:line), status (`missing` / `partial` / `planned-in-stories` / `contradicted-by-design-doc`), design-doc cross-reference if any, code anchor if any, one-line gap description.
4. **C → N gaps** (code-to-narrative) — table: behavior the code has, code anchor, whether the narrative mentions it, one-line note. This catches silent over-implementation — easy to forget.
5. **Three-way disagreements** — narrative ↔ design-doc ↔ code mismatches where all three say different things. Often the most useful section; surface it even if short.
6. **`[[...]]` triage** — every `[[design-actionable]]` marker, mapped to one of: candidate story (`stories/drafts/<slug>.md`) / candidate helping-hand / open design question / already-handled (with anchor). Stage as a list; don't write into spec/story dirs.

**Provenance discipline.** Every row in every table needs at least one anchor (`<file>:<line>` or `<file>` if line isn't meaningful). No anchor → don't include the row. For rows where one side is the gap itself (N→C row where code doesn't exist; C→N row where narrative doesn't mention the feature), the other side's anchor — or a design-doc line that declares the gap — is sufficient.

### Scoping

Don't try to be exhaustive. Aim for the 80/20: the gaps a careful reader of the narrative + a careful skim of the code would catch. If the codebase is huge, declare what you skipped in the framing-note.

### What `check` is not

- Not a substitute for `write` — doesn't draft a narrative; it consumes one.
- Not a review of the narrative's prose — doesn't suggest tightening or restructuring; only checks claims against code/design.
- Not a story-filer — `[[...]]` triage stages candidates; the user files them.
- Not a one-shot living doc — the output is a report. Re-run `check` after acting on findings rather than commenting on the report itself.

## Help

When invoked as `/walkthrough help`, print the following block verbatim:

```
walkthrough — Tutorial-quadrant narrative docs from a user's perspective. Also gap-analysis and follow-up triage.

Usage: /walkthrough [verb] [args]

Verbs:
  (none)            Smart-route: hand off to /integrate-comments if a
                    walkthrough with unseen review markers exists; else
                    draft a new walkthrough.
  new               Force-fresh draft regardless of existing artifacts.
  integrate [path]  Integrate <!-- @user: --> review comments into the
                    prose. Explicit alias for /integrate-comments —
                    same behavior; lives here so you don't have to
                    remember the sibling skill's name.
  check [path]      Bidirectional gap-analysis: compare a human-authored
                    narrative against the codebase + design docs. Parses
                    [[design-actionable]] and ((aside)) markers.
  clean-comments [path]
                    Strip processed <!-- @user+seen: --> markers from
                    annotated markdown. Works on any annotated doc.
  follow-ups [path] Triage [extrap] tags + review-log items into candidate
                    stories / helping-hands / design questions.
  help              Show this message.

Modes (draft verbs only):
  current           Describes the app as it ships today; no extrapolation.
  planned           Includes near-term roadmap; tags [planned] for unshipped.
  infinity (default) End-state as currently conceived; tags [extrap] past spec.
  trajectory        Four-artifact set (current + planned + infinity + synthesis).

Registers (draft verbs only; orthogonal to mode):
  spec              Roleless, sparse, ~1000-1500 words. For feeding design work.
  grounded (default) Named protagonist as anchor only, no side-cast or sensory
                    texture, ~1800-2500 words.
  storied           Named protagonist + supporting cast + sensory texture,
                    ~3000-4500 words. Opt-in for pitch / vision docs.

Markers:
  [[...]]           Embedded human-narrative design-actionable note (check input).
  ((...))           Embedded aside / clarification (check input; non-actionable).
  <!-- @user: -->   Review marker on LLM-drafted narrative (processed by
                    sibling /integrate-comments skill).

See SKILL.md for full reference.
```

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
- **Bare invocation runs iterate inline.** Old behavior was for `/walkthrough` to mutate prose in place when markers existed. Now: surface the find and hand off to `/integrate-comments`. Don't reimplement iterate logic here.
- **Auto-files follow-ups.** Skill writes stories/todos into spec directories without approval. Fix: stage and surface; user files.
- **Generates LLM companion by default.** Doubles output for a thing the user may not want. Fix: ask; default no.
- **`check` runs unidirectionally.** Only catches narrative→code gaps (missing features) and misses code→narrative gaps (silent over-implementation) or three-way design-doc disagreements. Fix: produce all three sections every run, even if short. C→N is the easy one to skip; don't.
- **`check` invents rows without anchors.** Tables get padded with intuited gaps that aren't tied to a specific file:line. Fix: every row needs at least one anchor; if you can't cite it, don't include it.
- **`check` ignores narrative's declared markup.** Skill assumes `[[]]` / `(())` universally; user's narrative announces different markers in its preamble. Fix: read the preamble for marker declarations and honor them.
- **Drifts into `storied` register by accident.** User gives "feel free to name humans" license and the draft sprouts a Reddit-thread origin scene, a screenshot-taking moment, a side-character cast, and atmospheric micro-paragraphs. The result is fun but eats reader budget for what was meant to be design-feeding material. Fix: register is a separate scoping question, default `grounded`; license to name humans is not a `storied` signal. If the draft grows side-cast or sensory micro-scenes that weren't in the chosen register's rules, treat that as drift and excise (or re-scope to `storied` explicitly).
- **Anchors on the topic of a visible-but-unread narrative.** Sees `<date>-<topic>.md` in `design/notes/` during orient and infers the new walkthrough should be on `<topic>` — even when the user told it to ignore that file or generate something different. Filename existence ≠ scope signal. Fix: if the user mentions a comparison target, identify it singularly before scoping; parse "ignore X" carefully (file? topic? both?); ground in the project's canonical design surface (DESIGN.md, README, stories), not whatever narrative files happen to be in `design/notes/`. The first Scope-phase bullet exists for exactly this failure mode — don't skip it just because the user "seems" to have already provided context.

## Quick reference

| Verb                                 | Output                                                                          | When                                              |
| ------------------------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------- |
| (bare) `/walkthrough`                | Hand-off to `/integrate-comments` (if existing has unseen markers) or draft new | Default invocation                                |
| `/walkthrough new`                   | Force-fresh draft                                                               | Comparison / parallel artifact                    |
| `/walkthrough integrate [path]`      | Integrated review comments + sibling review-log                                 | Explicit alias for `/integrate-comments`          |
| `/walkthrough check [path]`          | Bidirectional gap-analysis (`<stem>-check.md`)                                  | Human wrote a narrative; compare to code + design |
| `/walkthrough clean-comments [path]` | Stripped seen markers                                                           | Explicit cleanup                                  |
| `/walkthrough follow-ups [path]`     | Triaged spec-gap candidates                                                     | After iterate, at "good enough for now"           |
| `/walkthrough help`                  | Unix-style usage block                                                          | User asks "how do I use this"                     |

For integrating reviewer `<!-- @<user>: -->` comments into an existing walkthrough, use **`/walkthrough integrate [path]`** (alias) or **`/integrate-comments [path]`** (sibling skill directly) — same behavior either way.

| Phase         | Output                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------- |
| Orient        | Internal context (don't read prior walkthroughs at orient time)                                                     |
| Scope         | Comparison target, mode, perspective, scenario, format, register, depth, location                                   |
| Draft         | Narrative doc (mode-aware framing; `infinity` is default mode; `grounded` is default register)                      |
| Save          | `design/walkthroughs/<date>-<slug>/walkthrough.md` (preferred when dir exists) or legacy dated filename in `notes/` |
| LLM companion | Second file in same per-walkthrough dir (opt-in)                                                                    |

**Modes:** `current` / `planned` / `infinity` (default) / `trajectory`. Mode sets sourcing + tagging; see [Modes](#modes).

**Registers:** `spec` / `grounded` (default) / `storied`. Register sets voice + word budget; orthogonal to mode. See [Registers](#registers).

| Tag         | Used by mode             | Meaning                                                       |
| ----------- | ------------------------ | ------------------------------------------------------------- |
| `[planned]` | `planned`, `trajectory`  | Item is on the near-term roadmap but not yet shipped.         |
| `[extrap]`  | `infinity`, `trajectory` | Speculation past spec; reader should not treat as commitment. |

**Review-comment markers** (processed by `/integrate-comments`):

- `<!-- @<username>: <comment> -->` — unseen; run `/integrate-comments` to integrate
- `<!-- @<username>+seen: <comment> -->` — processed; disposition in review-log; remove via `clean-comments`

**Embedded human-narrative markers** (processed by `check`):

- `[[design-actionable text]]` — author wants this picked up; triaged as candidate story / helping-hand / design question
- `((parenthetical aside))` — clarifying context for the human reader; not surfaced as output items

**Diátaxis quadrant:** tutorial. If the user actually wants reference / how-to / explanation, this is the wrong skill.
