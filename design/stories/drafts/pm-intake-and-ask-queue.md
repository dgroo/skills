---
author: claude
priority: high
---

# The PM takes the work: one door for asks, one queue Derek can read

*Authored by Claude Fable 5.1 with Derek · Last updated 2026-10-01.*

Derek's words: "I often want to file 'I'd like to work on this soon' tasks into projects, that may or may not already be stories, and are more significant than /idea — add this to the work/story queue; if there's already a story, bump it in priority, if not create one. What I probably actually want is something that acts as the PM: as CTO/CEO I'd talk to a PM and fire off tasks/work, confident they would organize them into the queue and help prioritize." And: "one way I'd really want to be able to use this is to fire things into a session while it is working on something else."

This is a design draft. Nothing is built, and nothing gets built from `drafts/`.

## The proposal on one screen

1. **One new file per project, `design/ASKS.md`**, holding what Derek has asked for, in order. It has an `## Inbox` (raw asks, verbatim, untriaged) and a `## Queue` (an ordered list of pointers to the story or TODO entry each ask became). The name and the idea come from upstream `/go-team`, which already reads `ASKS.md` before anything else.
2. **`/pm <text>` becomes intake, in two phases.** Receipt appends the text to the Inbox and does nothing else, so it is safe to fire at a busy session. Triage happens later: size the ask, check it against existing work by reading bodies (not just filenames), then either create a stub or append to the existing story, and place a line on the Queue. That placement is the bump.
3. **Ranking starts reading the Queue.** `/next` and `/sup` rank from `next/backlog-ranking.md`, which today never looks at `priority:` at all. A new rule puts the top open Queue item directly under the session handoff. An ask outranks machine-found work because of which file it is in, with no per-item origin field.
4. **The periodic review is the existing `/pm` pass**, with the Queue as the list Derek reviews. The PM may propose adding, reordering or dropping Queue items; only Derek's word puts an item on it.
5. **The board needs no new plumbing from this side.** The PM writes files. `ASKS.md` is one more list file with a documented line format, and any question the PM has for Derek is written as a `<!-- derek(pm): … -->` mark, which the board's waiting lane and `find-review-marks` already pick up.

## Open decisions

Each is Derek's call. The recommendation is listed first.

### D1. Where the capability lives

1. **Extend `/pm` (recommended).** `/pm <text>` is intake, `/pm triage` drains the Inbox, bare `/pm` stays the periodic pass. `SKILL.md` becomes a short router with receipt at the top; the pass moves to a sibling `review.md` that is read only when the pass runs, so a receipt does not pull 150 lines of ceremony into a working session. One name for "tell the PM."
2. **A new small skill for intake** (`/ask`), with `/pm` gaining only the Queue reconciliation. Cheapest to load, but it splits the persona across two names and adds a skill to maintain.
3. **Minimal: no new verb.** `/story` gains a body-level duplicate check and writes a Queue line; the ranking rule is added. No Inbox, no sizing, no routing to TODO or IDEAS. This reaches "file it, bump it if it exists" and nothing else Derek listed. It is a real option if the PM persona turns out to be more than is wanted.

### D2. A separate `ASKS.md`, or ask metadata on the items themselves

1. **`design/ASKS.md` with Inbox and Queue (recommended).** One file to open, reorder by hand, and annotate. Receipt is a one-line append that cannot be mis-filed. Origin is the file. Compatible with `/go-team`.
2. **Frontmatter only**: an `asked: [dates]` list on stories and an inline marker on TODO entries, with order derived from recency. No second surface and nothing to drift, but there is no list to review, no hand-set order, and a mid-turn receipt would still need somewhere durable to land before triage.
3. **Reuse `design/NEXT.md`.** Rejected in the section on rejected options: it is the session handoff, owned by `/wrapup`.

### D3. What a bump does to order

1. **A position cue in the ask wins; otherwise stamp the date and let the PM place it under the pass's existing rule (recommended)**: strong signal moves it (the ask unblocks the item above it), no signal leaves it where it is, and the re-ask count is what the review weighs ("asked three times, still sixth").
2. **Stamp only.** Order changes only in the review.
3. **A re-ask always goes to the top.** Simple, but it silently rewrites an order Derek set by hand.

### D4. Priority vocabulary

Four vocabularies are in use (see Prior art). The Queue takes over the job of saying what is wanted soon, which lowers the stakes of this decision.

1. **Keep current practice and write it down (recommended).** Stories stay `high | medium | low`, TODO stays `P0–P3`, and the mapping the board already applies (high→P1, medium→P2, low→P3) is recorded once in the corpus standard. Triage sets `priority: high` when it places a story on the Queue and never lowers it, so today's board sorts asked work first with no board change.
2. **Adopt the corpus standard's `now | soon | someday`.** It matches Derek's own phrasing and it is a horizon, which is what an ask carries. It costs a field edit on roughly a hundred stories and a change to every reader. If chosen, the first `/pm` review in each project is the migration.
3. **`P0–P3` everywhere.** One vocabulary, same migration cost as option 2, and it reads as severity, which fits bugs better than stories.

### D5. When triage runs

1. **A background subagent starts as soon as the receipt is written, with two fallbacks (recommended).** The agent keeps the reading out of the working session's context. If no agent tool is available, triage runs in-session when the current block of work ends, the way `/story` resurfaces a stub today. In every case the Inbox is durable, so any later `/pm`, `/sup`, `/next` or `/wrapup` sees the untriaged count.
2. **Always in-session at the block boundary.** No agent cost; spends the working session's context.
3. **Only at the next `/pm`.** Cheapest; the `Filed:` line can never say more than "in the inbox."

### D6. Filing into another project

1. **`/pm @<project> <text>` appends to that project's Inbox and stops (recommended).** Triage happens in a session of that project, which knows its own corpus. If the project is not cloned on this host, the ask goes in the current project's Inbox tagged `@<project>` and the `Filed:` line says so.
2. **Route through upstream `/request`.** Its mailbox lives outside every checkout, so it is not carried between hosts by design sync and is invisible to a board that renders the corpus. Its foreign-repo guard hook is not installed here and contradicts the one-front-door hub workflow.
3. **One central inbox for all projects.** Simplest receipt, but it puts every project's asks in one repo regardless of sensitivity tier.

### D7. A cap on the Queue

1. **Soft cap, PM pushes back (recommended).** Past about eight open items the PM says so and asks which ones drop to `someday`. A queue of twenty is a backlog with a different name.
2. **No cap.**

### D8. How a mid-turn ask is received

What is known is under "Mid-turn mechanics" below. The choice is how much of receipt to trust to the model.

1. **Skill first, then a hook (recommended).** Increment 1 ships `/pm <text>` as a skill. Increment 3 adds a `UserPromptSubmit` hook that recognises the ask, appends it to the Inbox itself, and tells the model it was filed; the existing Stop hook prints the `Filed:` lines for anything received that turn. Receipt and the acknowledgement then no longer depend on the model remembering. The same script is a shell command (`ask "<text>"`), so an ask can be filed from any terminal with no session involved.
2. **Skill only.** Least to build. Receipt and the `Filed:` line rest on the model following the skill while busy with something else.
3. **A plain prefix (`pm: …`) handled by a CLAUDE.md rule.** No skill load, but it is a rule with no mechanism behind it, which is the kind that has repeatedly failed to fire in this setup.

## How intake works

**Receipt.** Append one entry to `## Inbox`: date and time, the text verbatim, and `@<project>` if given. No reading, no slug, no questions. The session then continues what it was doing. Because Derek may be in a mode that shows only a turn's final message, that message must end with one line per ask:

```
Filed: <short title> → design/stories/drafts/<slug>.md (new)
Filed: <short title> → design/stories/ready/<slug>.md (bumped, asked 3×, now 2nd)
Filed: <short title> → design/ASKS.md inbox (triage pending)
```

**Triage.** For each Inbox entry:

- **Size it** from the text: a spark, a task, a story, or an epic.
- **Check it against existing work by content.** Read story titles and opening paragraphs across `drafts/`, `ready/` and `done/`, plus `TODO.md`, `IDEAS.md` and `REVISIT.md`. A match in `done/` is an answer ("already shipped, here"), not a new item.
- **Route it.**
  - Matches an open story: append the verbatim text under `## Captured addition (/pm, unreviewed)` and add or move its Queue line.
  - New and story-sized: write a `/story`-format stub in `drafts/` (verbatim body, not-yet-pondered marker) and add a Queue line.
  - Task-sized: add a TODO entry in that file's own format and a Queue line pointing at it.
  - A spark with no "soon" in it: one line in `IDEAS.md`, no Queue line.
  - Epic-sized: one stub named `<slug>-epic.md`, per the existing convention, with a Queue line and a suggestion to `/ponder` it. Triage never decomposes an epic.
- **Do not guess.** Two plausible matches, or an ask that contradicts a `ready/` story, stays in the Inbox with a `<!-- derek(pm): … -->` mark stating the question and the default the PM would take.
- **Remove the Inbox entry** once routed. Git keeps the history.

**The Queue line.** One line per ask, in priority order:

```
- [ ] <title> → [stories/drafts/<slug>.md](…) · asked 2026-10-01, 2026-10-14 · Done: <one line, optional>
```

The `Done:` clause is what `/go-team`'s preflight requires of every open ask; triage fills it only when the ask states it.

**Ranking.** `backlog-ranking.md` gains one rule between the handoff rule and criterion 1: the top open Queue item leads, and criteria 1–6 order what is below the Queue. A prerequisite of a Queue item inherits its rank, which is the legitimate way machine-found work gets ahead of an ask. `backlog-scan` gains an ASKS surface: untriaged count and the top Queue lines.

**Review.** The `/pm` pass, after hygiene and the accuracy review, reconciles the Queue: check off asks whose story reached `done/`, flag dead pointers and asks that have sat untouched, then propose admissions (each with in-corpus evidence, as gap proposals are today), reorders and drops. Strong signal acts, real tradeoffs ask, as now. The pass stops rewriting `design/NEXT.md`.

## Mid-turn mechanics

Two requirements come from how Derek wants to use this, and both need a mechanism, not a resolution.

- **Receipt must be nearly free at delivery.** A message typed while a turn is running reaches the model between tool calls. Whatever handles it there runs inside someone else's task, so it gets one file append and no thinking.
- **The acknowledgement must be in the turn's final message.** In a mode that shows only that message, a mid-turn "filed" line is never seen.

Observed while writing this draft (2026-10-01): messages delivered during a running turn arrived between tool calls, and the `UserPromptSubmit` hooks fired on each delivery and injected their context. The deliveries observed were subagent reports, not typed input. The Stop hook already prints a `systemMessage` at every turn end.

Not yet established, and to be checked against the Claude Code docs before increment 1 is planned: whether a typed `/pm <text>` is expanded as a skill when delivered mid-turn or held until the turn ends, and whether a `UserPromptSubmit` hook fires at delivery for typed mid-turn input the way it did for the deliveries observed. If skills are held to turn end, option 1 of D8 still works but its first increment only captures between turns, and the hook moves up to increment 1.

## Prior art found

- **`/pm` writes priority and nothing ranks by it.** The pass sets `priority:` on stories and reorders `TODO.md`. `backlog-ranking.md` and `backlog-scan` never read `priority:`. The board is its only reader. A "bump" that only edits the field would not change what `/next` recommends.
- **The level field is too coarse to carry a bump.** `/story` and the story template default to `medium`. Across three projects, 43 of 93 open stories are `medium` and 19 are already `high`, so raising a story to `high` only adds it to that group, and there is no step above.
- **Existing duplicate checks do not bump.** `/story` compares filenames and appends. `/todo` points at the existing entry. `/revisit` proposes an append only when the text names a story. `/idea` has none.
- **Four priority vocabularies.** Stories in practice: `high | medium | low`. TODO: `P0–P3`. The corpus standard (`groot-claude-coord` `design/design-corpus/DESIGN.md`): `now | soon | someday`, on a flat story pile with a `readiness:` field. `/request`: `blocking | normal | low`.
- **The corpus standard and practice have diverged.** The standard describes flat stories sorted by frontmatter and a board that renders `backlog-scan --json`. No project other than the standard's own repo has flattened, `backlog-scan` reads directories and has no `--json`, and the board parses the files itself. The de facto contract is: TODO checkboxes with P-tokens, readiness by directory, `priority:` words.
- **Origin is recorded nowhere as a field.** `/go-team` ranks by origin through which file holds the item: `ASKS.md` first, and one agent always on its top open item. Its reason is a human-approved feature that sat unbuilt for twelve hours among 120 machine-generated entries. No project here has an `ASKS.md`. Some TODO entries carry it in prose ("(Derek, 2026-09-15)").
- **The lead dispatches and keeps no backlog.** In `session-teams/DESIGN.md` §4–§5 the lead is Derek's default conversation; it routes work to lanes as briefs in `design/queue/<lane>.md` and keeps its picture in `NEXT.md`. A groomed backlog was explicitly dropped from that design. Lanes and the lead are inert below two live lanes.
- **`NEXT.md` changed underneath `/pm`.** It is now a baton plus per-thread handoff sections written by `/wrapup`. Step 4 of the pass still says to refresh its do-next order.
- **Epics have a working convention**: `<slug>-epic.md` with `**Epic:**` backlinks on children (two epics, 28 backlinks in use). The standard's `type: epic` is unused.
- **`walk-a-queue-disposition-primitive.md`** (drafts, parked) describes the present-item, pick-disposition loop four skills reimplement. The review's walk over the Queue would be a sixth consumer.
- **One project already runs a numbered inbox with a triage loop** for requests an agent files. Same shape as the Inbox here, different filer.

## How it composes with the lead

The PM files and ranks; it never dispatches. With no lanes, the PM is the whole arrangement. With lanes, the lead runs `/pm <text>` when Derek hands it work that is not for right now, and reads the Queue when choosing what to brief; the brief cites the Queue item's story. Neither requires the other.

## Rejected

- **A ledger or state file inside the skill.** `/pm` is stateless on purpose; the corpus files are the state. `ASKS.md` is corpus, not skill state.
- **`NEXT.md` as the queue.** It is overwritten by `/wrapup` per thread and its sections park after 14 days. A priority queue needs the opposite lifetime.
- **An `origin:` field on every story.** It needs a schema change, a backfill, and a reader in every tool; file membership gives the same ranking with none of that.
- **Decomposing epics at intake.** That is design thinking, which is `/ponder`'s job and needs Derek.
- **Triage from the filing project when the target is another repo.** The filing session does not know the target's corpus; this is the part of `/request`'s reasoning worth keeping.
- **GitHub Issues as the queue.** Already rejected as a second backlog in `session-work-claims.md`.
- **The rest of gstack `plan-ceo-review`.** The minimal alternative (D1 option 3) and the twelve-month check are kept; scope modes and scored options are ceremony for a capture path.

## Twelve months out

The ideal: asks arrive from a terminal, a phone, a chat bot or the board into one Inbox per project; a portfolio view ranks across projects; lanes are briefed from the Queue; an overnight `/go-team` run reads the same file. This plan moves toward it: the Inbox is a file anything can append to, and `ASKS.md` is the shape upstream already reads. If the frontmatter-driven corpus standard is ever built, Queue order could move into frontmatter and `ASKS.md` become a generated view. That is a two-way door.

## First increments, if Derek says go

1. **The file and the verb.** `ASKS.md` format, `/pm <text>` receipt, in-session triage (new or bumped), the `Filed:` line, the ranking rule, the `backlog-scan` surface. Touches `dgroo/skills` and one script in dotfiles. Scope 1x; low novelty; the risk is mid-turn behaviour. Roughly one to two pair-hours, ±2x.
2. **Review integration.** Queue reconciliation, admissions, the cap, and removing the `NEXT.md` rewrite from the pass. 0.5x.
3. **Background triage and the cheaper receipt path** chosen in D8. 1x; more novel.
4. **`@<project>` routing.** 0.5x.
5. **Record the contract** in the corpus standard, including the D4 outcome and the drift listed under Prior art. That lands in `groot-claude-coord`. Board lanes for Inbox and Queue are the board project's own story.

## Non-goals

- Dispatching or implementing work. The lead dispatches; sessions implement.
- Any board code, or any dependency on how the board parses.
- Flattening `stories/` or migrating readiness to frontmatter. The PM writes whichever layout the project has.
- Item ids.
- Cross-project ranking. One Queue per project; a portfolio view is a rendering concern.
- Sensitivity: an ask is filed in the project it is about. Text about a private project is not appended to a public repo's Inbox; the PM says so and files it locally instead.
