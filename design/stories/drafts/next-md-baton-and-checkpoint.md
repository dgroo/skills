# NEXT.md baton + context-pressure checkpoint

*Authored by Claude Opus 5.5 with Derek · Last updated 2026-09-27.*

## Problem

Derek's observation (2026-09-27): after a `/wrapup`, the next session often just picks up "the general design queue" rather than the specific thing the prior session meant to hand over. The pipeline exists — `/wrapup` writes a `## Thread:` section into `design/NEXT.md`, `boot-ritual.py` points at the file, `/sup` + `/next` rank it first (`next/backlog-ranking.md` §3 rule 0) — but it behaves like a thread board, not a baton:

- **Threads accumulate.** A section is only deleted when some session recognises it finished that thread, which rarely happens. `remote-coding-setup`'s NEXT.md held four threads, all `wrapped 2026-08-24`, a month stale — a second backlog.
- **The most recent handoff is indistinguishable.** A 2026-09-23 session appended a note into one thread without bumping its `wrapped` date; day-granular dates tie, so "most recently wrapped" was an arbitrary pick.
- **Sections are lists, not an action.** 4–7 items each, several of them "Derek decides X" — rule 0 leads with item 1, which reads like any backlog item.
- **The start hook only points.** `boot-ritual.py` said "read NEXT.md"; if the first prompt isn't `/sup`//`next`, nothing reads it.
- **The only explicit baton was cross-machine only** (`/wrapup` Phase 6's ephemeral prompt).

Second question from the same conversation: when `<context-pressure>` fires, should the session just run `/wrapup`? Mostly harmless, and the real value is capture-before-auto-compaction (the compaction summary is lossy, and handoff intent is exactly what it drops). The costs are auto-pushing mid-task work and writing a NEXT.md section a continuing session then leaves stale.

## Design

**1. A single baton slot at the top of NEXT.md** — orthogonal to the thread board, not a replacement:

```markdown
## Baton · 2026-09-27 08:40 · thread <slug> · branch <branch>

<one concrete action, one or two sentences — the exact thing the next session should do first>
```

- At most one. Written by `/wrapup` only when there is a specific next move, never a list. Overwritten by the next writer (it is the *latest* intent by definition).
- **Consumed on pickup:** the session that acts on it deletes the block as it starts the work. This is what keeps it from going stale the way thread sections did.
- `boot-ritual.py` quotes the baton text inline in `<session-handoff>`, so it is in context without a read. `backlog-scan` emits it as its own `NEXT.md baton` surface, above the thread surface. `/sup` / `/next` make it the `go` lead — above rule 0's thread picks.

**2. Parked threads, computed not marked.** A `## Thread:` section whose `wrapped <YYYY-MM-DD>` is older than **14 days** is *parked*: still listed, never the lead, its items excluded from `backlog-scan`'s count. Computed from the date, so no writer has to remember to flip a marker. `/wrapup` bumps `wrapped` whenever it touches a section (and may add `HH:MM`), which fixes the tie problem too. Threshold lives in the design-corpus doc; code carries it as a named constant with a pointer back.

**3. `/wrapup checkpoint` — the context-pressure mode.** Refresh this thread's NEXT.md section and the baton, write a diary entry only if warranted, **commit locally, never push** (Derek, 2026-09-27), no verdict, no STAY analysis, don't end the session. `context-low-check.py`'s `<context-pressure>` message tells the session to run it at the next natural pause instead of "suggest a fresh session" — consistent with CLAUDE.md's "low context isn't itself a breakpoint".

## Decisions

1. **Who clears the baton when a checkpoint wrote it and the same session then did the work?** The session's own real `/wrapup` rewrites or deletes it (common case). If the session dies after the checkpoint, the baton surviving is *correct* — it's the protection. Guard against the stale case the same way rule 0 guards threads: consumers cross-check recent commits and say "looks already done" instead of re-recommending.
2. **Checkpoint pushes?** No — local commit only. The real wrap pushes. (In design-synced repos the watcher still delivers `design/NEXT.md` itself, which is fine: that's the part worth protecting.)
3. **Parked: marker vs computed** → computed (above).

## Consumers touched

- `dgroo/skills`: `wrapup/SKILL.md` (writer + checkpoint), `next/backlog-ranking.md` rule 0, `sup/SKILL.md`, `next/SKILL.md`.
- `dgroo/dot-claude`: `hooks/boot-ritual.py` (+tests), `hooks/context-low-check.py`.
- dotfiles: `~/bin/backlog-scan` (+`~/bin/tests/test_backlog_scan.py`).
- `groot-claude-coord`: `design/design-corpus/DESIGN.md` — NEXT.md shape (baton, threads, parked threshold).
- Not changed: `peer-pulse` (reads a legacy `**Current focus:**` line; unaffected), `/pm` and `/cleanup-design` (treat NEXT.md as prose; baton is compatible).
