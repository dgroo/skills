# Candidate model — scan, harvest, rank

The shared "where queued work lives, and how to choose among it" core for **`/next`** and **`/sup`**. Both skills Read this file and apply it, then render the result in their own way (`/next` as an interactive AskUserQuestion chooser; `/sup` as a non-blocking Pick inside its report). Keeping it in one place is deliberate: the two skills had drifted (different ranking criteria, harvest added to one before the other) when this lived as duplicated prose. **Edit the candidate model here, once.** Skill-specific behavior (presentation, modifiers, guards, `/sup`'s HUMAN-REVIEW confidence-filter, `/sup`'s defer-to-sibling) stays in each `SKILL.md`.

## 1. Scan the file surfaces

Run the shared scanner — one command, one definition of "where filed work lives":

```bash
backlog-scan
```

It emits a grouped, counted inventory of the `design/NEXT.md` session handoff (emitted first; see §3 rule 0), `TODO.md` (open entries), `design/stories/ready` (outranks drafts), `design/stories/drafts`, `design/helping-hands`, pending `REVISIT.md` items, open PRs, and stale branches — surfaces with nothing shown as `— 0`. Use its titles and counts directly. **Glance — don't deep-read;** read an individual file only when a candidate genuinely needs disambiguating (e.g. to confirm a dependency).

If `backlog-scan` isn't on PATH (older host, dotfiles not yet pulled), fall back to a quick manual glance at `TODO.md`, `design/stories/ready/*.md`, `design/helping-hands/*.md`, and `gh pr list` — but the script is the intended path; surface the gap so it gets installed.

## 2. Harvest outstanding threads from this conversation

The backlog is only what got _filed_; a live session almost always leaves loose ends that never made it to a file, and those are legitimate candidates. Scan this conversation's scrollback for still-open work and add it to the candidate pool:

- things the assistant said it would do but didn't ("I'll file that", "let me come back to", "next we should"),
- items it _surfaced_ but didn't act on (the global "surface opportunities, don't silently act" rule),
- carry-forwards / deferred sub-tasks it explicitly parked,
- bugs noticed-but-not-fixed.

**Forward-only — outstanding items only, not a recap.** (`/sup`'s Session recap is the descriptive "what happened, finished work included"; this harvest takes only the still-open subset and feeds the pick.) Two filters keep it honest:

- **(a) Dedup** against the backlog scan and against what's already committed this session — if it's already in TODO/REVISIT/a story, or already shipped, it isn't an open candidate.
- **(b) Drop what isn't yours to do** — another host's `dotpull`, anything gated on the user's hands or a paid credential — to a one-line aside, not the pick list.

On a genuinely fresh session with no prior turns this yields nothing and the pick is pure backlog — the harvest is purely additive.

## 3. Ranking criteria (tiebreakers, in order)

**0. The `NEXT.md` session handoff comes first — above every heuristic below.** `design/NEXT.md` (or root `NEXT.md`; surfaced by `backlog-scan` as `NEXT.md handoff`) is the ephemeral "pick up here" note a prior session left for this one — narrative current-focus plus an ordered do-next list. Lead with continuing it: the first do-next item is the pick, the second is next, and so on — do **not** re-rank the handoff's items by the criteria below, which exist only to order the backlog _beneath_ the handoff. This is exactly what a `/clear` would otherwise discard (the handoff lives only in scrollback and `/sup`'s recap), so reading `NEXT.md` is the prior session's plan surviving into this one. When `backlog-scan` shows the surface as `present` (an unparsed handoff), **read `NEXT.md` itself** and lead with what it says. The handoff is _ephemeral_: a session that finishes its items overwrites `NEXT.md` with the new state (that's `/wrapup`'s job) — so if its items look already-shipped (cross-check recent commits), say so rather than re-recommending them.

1. **Unblocks downstream work.** Helping-hands often gate other items; a ready story may be a prerequisite for drafts. The thing that makes _other_ things possible wins — lead with it.
2. **Makes other work easier (leverage).** Infrastructure, a shared script, a refactor several queued items would build on. Lowers the cost of everything after it.
3. **Removes risk.** Broken main, security, data loss, a flaky thing that keeps biting.
4. **Matches capacity.** If context is already tight, prefer something small and self-contained. If fresh, a candidate can be ambitious.
5. **Continuity.** If files just touched relate to a queued item, that's a real pull — less re-orientation cost. **Caveat:** conversation-harvested loose ends (§2) score high here almost by definition (they came out of what you were _just_ doing), so weight them on genuine leverage/unblocking, not the continuity they trivially have, or they'll always float to the top.
6. **Tied? Smaller, concrete item beats larger, ambiguous one.**

## 4. Grounding rules

- **Only propose what the scan or the conversation actually surfaced. No imagined work.** A backlog candidate comes from `backlog-scan`; a conversation candidate must be a real, quotable loose end from _this_ scrollback (something actually said or left undone) — not a plausible-sounding task you inferred the project "should" want.
- **Mark conversation-derived candidates** (e.g. `(this session)`) so the source is legible — they didn't come from a file the user can re-read.
- **State dependency reasoning explicitly:** "do X first — it unblocks Y and Z" beats "X seems important."
- **REVISIT items are time/event-gated.** Treat far-future or event-only entries as low-priority unless their trigger has plausibly arrived.
- **HUMAN-REVIEW items are never candidates.** `backlog-scan`'s `HUMAN-REVIEW (open)` surface is the user's to eyeball, not yours to do — never offer one as a pick. Surface it as a non-blocking aside instead. (Each skill renders that aside its own way; `/sup` additionally runs a confidence filter — see its `SKILL.md`.)
- If a read of a story/helping-hands file was needed, characterize it in _one line_ — don't paste contents.
- If nothing is queued anywhere and the conversation has no loose ends, say so plainly and ask what the user wants to work on — don't manufacture candidates.
