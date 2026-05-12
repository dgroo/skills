# walkthrough — follow-ups

Surfaced 2026-05-11 from dogfooding the skill against iDM (`/Users/Groot/code/iDM/design/notes/2026-05-11-narrative-assistGM-human.md` + review-log). Each item is a skill-level improvement, not a project-level concern.

## S1. Username discovery fallback

**Problem.** Skill currently spec'd `<!-- @<username>: -->` where username defaults to `git config user.name`. On Derek's setup that returns `iamgroot`, but he annotates with `@derek` (his first name). The grep missed.

**Proposed fix.** Cascade of discovery, first-hit wins:

1. Scan the doc for *any* `<!-- @<word>:` patterns; if exactly one distinct username appears, use it.
2. Else: try `git config user.name` (lowercased), then `git config user.email`'s local-part, then `$USER`.
3. Else: ask the user which marker prefix to use.

The "scan the doc first" step handles the actual case — the doc itself is authoritative for whoever marked it up.

## S2. v0.1 vs v-infinity scope question

**Problem.** When the walkthrough describes an actively-developing project, there's a real ambiguity: is the narrative describing the system *as currently shipping* or *as fully designed*? Different audiences want different answers. The iDM dogfood surfaced this exactly: Derek's first comment was a meta-question about which framing to use, and the answer changed the whole document's tone.

**Proposed fix.** Add to the Scope phase (currently in SKILL.md §"Scope"):

```
- **Maturity framing**: at what version is this narrative pinned?
  - Current implementation (v0.x — what ships today)
  - Full design (v-infinity — the system as fully imagined)
  - Both, with progression note at top (recommended for actively-developing projects)
```

Use `AskUserQuestion` when the project shows signs of active development (recent commits, version <1.0, drafts/ open in stories), skip when the project is mature/stable.

## S3. Large iterate UX (batch vs. interactive)

**Problem.** The iDM iterate pass picked up 22 reviewer comments and made batch decisions on all of them. Several were spec-shaped (substantial rewrites, deferred follow-ups) — the user had to trust the batch synthesis rather than walking through them one at a time.

**Proposed fix.** When iterate mode finds more than N comments (proposed default N=10), offer a choice via `AskUserQuestion`:

- **Batch** (current behavior): integrate all comments in one revision, surface the summary.
- **Interactive walk-through**: present each comment with proposed integration, accept/edit/skip per comment. Slower, more deliberate.
- **Spec-shaped only interactive**: batch the prose-tweak comments; pause on comments that look like spec gaps (LLM heuristic: comment mentions architecture, data model, naming, behavior changes, or starts with "huh — I thought...").

The third option is probably the right default for actively-developing projects.

## Related

- `~/code/iDM/design/notes/2026-05-11-narrative-assistGM-human-review-log.md` — original surfacing
- `SKILL.md` — the skill these improvements target
