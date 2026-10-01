---
name: pm
description: Periodic backlog-stewardship pass for a project's design corpus — the "sit in the PM chair" ceremony. Delegates document hygiene to /cleanup-design, then adds the two layers cleanup-design won't: a judgment-heavy accuracy review of stories/notes (is this still true and still wanted?), durable reprioritization of the backlog (reorder TODO / story priority / NEXT.md on strong signal, ask on genuine tradeoffs), and grounded gap-proposal (file drafts for work the corpus clearly implies but nobody's filed). Stateless — the backlog files ARE the state. Use for "run a PM pass", "tidy and reprioritize the backlog", "is our backlog stale / correctly ordered / missing anything", "/pm".
argument-hint: "? | ! | help"
---

# /pm — the project's PM

## Routing

| Invocation          | Behavior                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------ |
| `/pm`, `/pm ?`, `/pm !` | The periodic pass. **Read [`review.md`](review.md)** (installed at `~/.claude/skills/pm/review.md`) and follow it. |
| `/pm help`          | Print the Help block below verbatim.                                                       |

## Help

When invoked as `/pm help`, print the following block verbatim:

```
pm — Periodic backlog-stewardship pass (the project-manager chair). Wraps
/cleanup-design for hygiene, then adds accuracy review, durable
reprioritization, and grounded gap-proposal. Stateless — the backlog
files are the state.

Usage: /pm [? | !]

Verbs:
  (none)            Default pass: hygiene (via /cleanup-design) + accuracy
                    review + strong-signal reprioritization written back to
                    TODO/story-frontmatter/NEXT.md. Present gaps + genuine
                    priority tradeoffs for a decision.
  help              Show this message.

Modifiers (decisiveness dial):
  ?                 Advise only — run the full pass read-only, write nothing.
  !                 Autonomous — also file grounded gap-drafts and act on more
                    reorders without asking. Still surfaces genuine priority
                    TRADEOFFS (those stay Derek's call even under !).

Sequence:
  1. Orient         Discover the design layout.
  2. Hygiene        Delegate to /cleanup-design (drift, dead links, move-to-done).
  3. Accuracy       Semantic review cleanup-design won't do: is each story still
                    true / still wanted / still ready? Demote / rewrite / close.
  4. Reprioritize   Rank the whole backlog (shared backlog-ranking.md model) and
                    write the order back. Strong signal acts; real ties ask.
  5. Gaps           Propose drafts for work the corpus IMPLIES but nobody filed —
                    every one evidenced, never imagined.
  6. Present        One glance: Tidied / Reprioritized / Gaps.

Companions:
  Wraps /cleanup-design; reuses ~/bin/backlog-scan; adjacent to /next
  (ephemeral session pick) and /beginners-mind (fresh-eyes external audit);
  nudged by /wrapup when the backlog looks untended.

See review.md for the full pass.
```
