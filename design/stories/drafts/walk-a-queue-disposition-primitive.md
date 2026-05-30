---
author: claude
priority: low
---

# Walk-a-queue: a shared per-item disposition primitive (parked)

## Problem

At least four skills independently reimplement the same interaction loop — *present a
queue of items one at a time, offer a small set of per-item dispositions, apply each,
advance*:

- `/revisit walk` — per entry: resolve / skip / push-the-date
- `/idea iterate` — per spark: elaborate / delete / skip
- `/helping-hands` — per item: validate-still-live / scaffold-further / surface-the-ask
- `/beginners-mind` — the ledger walk over prior recommendations: apply / dismiss / defer

Each one re-grows the same scaffolding: the entry gate ("you have N items — want the
list, or walk them one at a time?"), the per-item `AskUserQuestion`, the disposition
verb set, the write-back of a resolution/audit line, and (in some but not all) a
"can I clean this up before bothering the human?" pre-filter. Divergence is already
visible — the verb sets differ, only some auto-resolve before surfacing, some batch
and some go strictly one-at-a-time.

A fifth consumer is incoming and is the reason this story exists now: the **HUMAN-REVIEW
queue** being designed in `remote-coding-setup` (`design/HUMAN-REVIEW*.md`) wants exactly
this loop — per item: keep / drop / mark-reviewed — plus a confidence pre-filter that
auto-clears items the LLM can assert no longer need a human (the feature shipped / was
removed / is demonstrably working). That pre-filter is the same shape as the
`helping-hands` "validate still live" step.

## Proposed shape

A shared primitive the consumers delegate to (skill) or cite (reference doc) that owns
the parts that don't vary:

- **The gate** — "N items waiting. List / walk / skip?" Gentle, never do-now pressure.
- **The per-item loop** — iterate, present one item, collect a disposition from a
  consumer-supplied verb set, apply, advance.
- **The confidence pre-filter** — before surfacing item *i*, give the consumer a hook to
  assert "this no longer needs the human" and auto-resolve it (the helping-hands /
  HUMAN-REVIEW cleanup rule). Only survivors reach the human. This is where the
  staleness-rot failure mode gets solved actively rather than by hope.
- **The write-back convention** — a resolution/audit line appended in place
  (`**Resolved:** …` / `**Reviewed:** …`), so the queue keeps its own history.

Consumers supply: the queue source (file path + parser), the disposition verbs and what
each does, the audit-line format, and the pre-filter predicate.

## Open questions

- **Skill vs reference doc.** Skills can't cleanly *call* other skills today, so a true
  `/walk-queue` delegate may not be mechanically realistic. The pragmatic shape might be
  a documented pattern (a shared reference fragment the consumers' `SKILL.md` files cite),
  not a callable. Decide before building.
- **`AskUserQuestion` ergonomics.** It's the natural per-item UI but caps at 4 options and
  a long queue means many sequential prompts. Batching (show 5, act on all) vs strict
  one-at-a-time is a real UX fork — `/beginners-mind`'s ledger walk and `/idea iterate`
  may want different answers.
- **Does this over-abstract?** Four consumers with genuinely different verb sets might not
  share *enough* to justify a primitive. Forcing test below.

## Trigger to pick up

- **Primary:** when the HUMAN-REVIEW queue in `remote-coding-setup` is actually built.
  Build *that* consumer's walk loop first by copying the pattern. If it copies cleanly
  and the pre-filter lines up with `helping-hands`, that's the signal the abstraction is
  real and worth extracting. If the copy diverges hard, the abstraction was premature —
  leave it parked.
- **Secondary:** a fifth-plus divergence the user notices ("why does `/idea iterate`
  behave so differently from `/revisit walk`?").

## Related

- Consumers in this repo: `skills/revisit/`, `skills/idea/`, `skills/helping-hands/`,
  `skills/beginners-mind/`
- Originating discussion: `remote-coding-setup` HUMAN-REVIEW queue design
  (`diary/serenity26.md`, ~2026-05-30) — the fifth consumer and forcing function
- `../../MAINTAINERS.md` — ownership manifest
