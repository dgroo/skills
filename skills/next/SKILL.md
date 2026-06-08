---
name: next
description: Forward-only "what should I pick up?" — scans the project's queued-work surfaces (TODO, ready/draft stories, helping-hands, REVISIT, open PRs, stale branches) plus the current conversation for outstanding loose ends, and presents a few dependency- and leverage-ranked candidates via AskUserQuestion. Pick one or specify your own. Use when asking "what's next?", "what should I work on?", "what should I pick up?", or "/next". Companion to /sup — /next is forward-only with no situation recap and offers the options as an interactive AskUserQuestion chooser; /sup is situation-report-first and surfaces the same ranking as a non-blocking list (no prompt).
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# Next — what should I pick up?

`/next` answers one question: **"I'm free — what's the best next chunk of work?"** It scans where queued work lives — the file-based backlog surfaces **and** the current conversation for loose ends — reasons about _sequencing_ (what unblocks what, what makes other work easier), and hands you a few ranked candidates to choose from.

**Companion to `/sup`, not a clone.** `/sup` is situation-report-first — it recaps this window, then emits _one_ pick only when the current chunk is parkable. `/next` skips the recap entirely and goes straight to _multiple_ forward-looking options with dependency reasoning up front. Reach for `/sup` on a cold resume ("what was I doing here?"); reach for `/next` when you already know you're done and want to choose what's next.

**On the conversation: `/next` still skips the _recap_, but it does harvest _loose ends_.** This is the line between the two skills, worth holding precisely. `/sup`'s Session recap is _descriptive_ — "here's what this session did," finished work included. `/next`'s conversation pass is _forward-only_ — it extracts only the still-**outstanding** threads (things the assistant said it'd do, items it surfaced but didn't act on, carry-forwards, deferred sub-tasks) and feeds them into the candidate pool alongside the backlog. So a conversation item that already got _filed_ (to TODO/REVISIT/a story) is the backlog's job, not a separate conversation candidate — dedup against what the scan already found.

The file surfaces come from one scanner (`~/bin/backlog-scan`), shared with `/sup` so there's one definition of "where queued work lives" — no drift. The conversation pass is `/next`-local: it reads _this_ window, which a script can't.

## Routing

| Invocation   | Does                                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `/next`      | Scan, rank, present candidates, let the user pick.                                                                       |
| `/next !`    | Scan, rank, **auto-pick the top candidate (bugs first) and start it** — no AskUserQuestion. See [Modifier](#modifier--). |
| `/next help` | Print usage (see [Help](#help)).                                                                                         |

## Modifier — `!` (just start the top pick)

`/next` participates in the decisiveness-dial convention shared with `/wrapup` and `/sup`: **`?` = assess, minimize mutation · `!` = act decisively, minimize interruption.** `/next`'s default _already_ asks before acting (it presents candidates via AskUserQuestion), so plain `?` would be a no-op — it isn't implemented here. Only `!` adds behavior:

- **`/next !`** — run the same scan + harvest + ranking (steps 1–4), then **skip the AskUserQuestion and just start the single top candidate**, with **bugs first**: if the scan surfaced open bugs / broken-main / risk items, they outrank features regardless of the normal tiebreaker order (this is the global "fix bugs before new work" rule made explicit). Announce the pick and the one-line why, then begin.
- **The in-flight guard still wins (step 1).** If `git status --short` shows substantial uncommitted in-flight work, the honest answer is still "finish/commit that first" — surface it and do _not_ auto-start a new pick on top of it. `!` is decisive, not reckless.
- **The context check still runs (step 6), before starting.** If remaining context is genuinely low _and_ the top pick is substantial, surface the fresh-session / `/compact` suggestion instead of auto-starting in an impaired session — same as plain `/next`, just resolved before work begins rather than after the pick.
- **Nothing queued → say so, don't invent.** If the scan is empty, `!` doesn't manufacture a pick; it reports the empty backlog like plain `/next`.

Plain `/next` is unchanged: present candidates, let the user choose.

## Sequence

1. **Glance at current state.** Run `git status --short`. `/next` is forward-only, but if there's substantial uncommitted in-flight work, the honest first answer is "finish/commit that" — surface it as a one-line preamble (not a candidate). Don't deep-dive; this is a glance.

2. **Scan the surfaces.** Run `backlog-scan` (no args, from anywhere in the repo). It emits a grouped, counted inventory of TODO entries, ready/draft stories, helping-hands, pending REVISIT items, open PRs, and stale branches. Use its titles for triage — read an individual file only when a candidate needs disambiguating (e.g. to confirm a dependency). **Don't deep-read everything.**

3. **Harvest outstanding threads from this conversation.** The backlog is only what got _filed_; a live session almost always leaves loose ends that never made it to a file. Scan this conversation's scrollback for still-open work and add it to the candidate pool: things the assistant said it would do but didn't ("I'll file that", "let me come back to", "next we should"), items it _surfaced_ but didn't act on (per the global "surface opportunities, don't silently act" rule), carry-forwards / deferred sub-tasks it explicitly parked, and bugs noticed-but-not-fixed. **Forward-only — outstanding items only, not a recap** (that's `/sup`'s job; see the intro). Two filters: (a) **dedup against the backlog scan and against what's already committed** — if it's already in TODO/REVISIT/a story, or already shipped this session, it's not an open candidate; (b) **drop items that aren't yours to do** — another host's `dotpull`, something gated on the user's hands or a paid credential belongs in a one-line aside (like the HUMAN-REVIEW gate), not the pick list. On a genuinely fresh session with no prior turns, this step yields nothing and `/next` behaves exactly as a pure backlog scan — it's purely additive.

4. **Reason about sequencing, then pick 3–4 candidates.** This is the core — model judgment, not a script. Apply the [ranking criteria](#ranking-criteria) below across the merged pool (backlog + conversation loose ends). Look for cross-references between items (a TODO that says "full story: design/stories/…", an item "gated on" or "blocked by" another, a helping-hands item that unblocks a story). Prefer the unblocker. Group tightly-related small items into one candidate when it's natural ("the three OSC-11 / terminal-color chores").

5. **Present via AskUserQuestion.** One question, 3–4 options. Each option's label is a short pick name; its description carries the _why_ — the dependency/leverage reasoning and a rough size. **Mark conversation-derived candidates** so the source is legible (e.g. "_(this session)_") — they didn't come from a file the user can go re-read. The user picks one, or chooses "Other" to specify their own. (AskUserQuestion always offers Other — don't add it manually.)

6. **Context-window check (conservative, pick-scaled).** After the user picks, read the live context figure and decide whether to raise a fresh-session / clear / compact suggestion. See [context check](#context-window-check). Most of the time, emit nothing. This step comes last so it can scale to the chosen pick, and so the suggestion lands at the bottom where the eye goes.

## Ranking criteria

Tiebreakers, in order:

1. **Unblocks downstream work.** Helping-hands often gate other items; a ready story may be a prerequisite for drafts. The thing that makes _other_ things possible wins. This is the headline value of `/next` — lead candidates with it.
2. **Makes other work easier (leverage).** Infrastructure, a shared script, a refactor that several queued items would build on. Lower the cost of everything after it.
3. **Removes risk.** Broken main, security, data loss, a flaky thing that keeps biting.
4. **Matches capacity.** If context is already tight (see step 6), prefer something small and self-contained. If fresh, a candidate can be ambitious.
5. **Continuity.** If files just touched relate to a queued item, that's a real pull — less re-orientation cost. Conversation-harvested loose ends (step 3) score high here almost by definition — they came out of what you were _just_ doing — so weight them on genuine leverage/unblocking, not on the continuity they trivially have, or they'll always float to the top.
6. **Tied? Smaller, concrete item beats larger, ambiguous one.**

Rules:

- **Only propose what the scan or the conversation actually surfaced.** No imagined work. A backlog candidate must come from `backlog-scan`; a conversation candidate must be a real, quotable loose end from _this_ scrollback (something actually said or left undone) — not a plausible-sounding task you inferred the project "should" want. If you read a file to check it, characterize it in one line — don't paste contents.
- **State the dependency reasoning explicitly** in each candidate's description: "do X first — it unblocks Y and Z" beats "X seems important."
- **REVISIT items are time/event-gated.** Treat far-future or event-only entries as low-priority candidates unless their trigger has plausibly arrived; don't rank a "revisit in August" item above ready work.
- **HUMAN-REVIEW items are never candidates.** `backlog-scan`'s `HUMAN-REVIEW (open)` surface is _Derek's to eyeball, not Claude's to do_ — never offer one as an AskUserQuestion option, and never auto-pick one with `/next !`. If it has open items, run the confidence filter (`design/HUMAN-REVIEW.md` rule 2 — drop any you can confidently assert are already resolved); if any survive, add a one-line aside _after_ the candidates: `👀 N item(s) also waiting for your eyes (non-blocking) — say "review" to walk them.` The auto-cleanup _write_ (rule 1) happens only on explicit confirmation, not during a plain scan.
- If nothing's queued anywhere, say so plainly and ask what the user wants to work on — don't manufacture candidates.

## Context-window check

Runs after the pick. The goal is a _rare, evidence-based_ suggestion — the opposite of the trigger-happy heuristics elsewhere. Two things make that possible and they only line up here: `/next` fires at a genuine clean break (you're choosing the _next_ chunk, so the re-orient cost is about to be paid anyway), and it reads the **actual** number rather than guessing.

**Read the real figure** (don't estimate from feel):

```bash
cat ~/.claude/state/context-remaining 2>/dev/null
```

This is the percent of context _remaining_, written by the statusline on every render (same value `~/.claude/hooks/context-low-check.py` trusts). Missing/unreadable → skip the check entirely and stay silent.

**Fire only when BOTH hold:**

- Remaining is **genuinely low — under ~30%** (be conservative; the whole point is to not be aggressive). A transient mid-task dip isn't your concern — you're at a clean break, so the number reflects real accumulated state.
- The **chosen pick is substantial** — a multi-step story or a fresh exploration, not a 5-minute chore. A small self-contained pick is fine to do in-place even at 20% remaining; don't suggest a reset for it.

**Tailor the suggestion to the pick** (this is why it runs _after_ the choice):

- Pick is **unrelated** to the current conversation → suggest a **fresh session** (or `/clear`) — nothing here is worth carrying.
- Pick is **related / builds on** what's in context → suggest **`/compact`** — keep the thread, shed the bulk.

**Framing:** optional, one line, at the very bottom. "You're at 22% context and `<pick>` is a meaty one — worth starting it in a fresh session." Never a hedge-stack ("you might consider possibly…"). Either the number and the pick-size both clear the bar (say it, once) or they don't (silent).

## Help

When invoked as `/next help`, print this block verbatim:

```
next — Forward-only "what should I pick up?" Scans queued-work surfaces,
ranks candidates by dependency + leverage, presents them to pick from.

Usage: /next [! | help]

Verbs:
  (none)            Scan, rank, and present next-work candidates via
                    AskUserQuestion. Pick one or specify your own.
  !                 Skip the question — auto-pick the top candidate
                    (bugs first) and start it. Defers to the in-flight
                    guard and the low-context check before starting.
                    Plain ? is a no-op here (/next already asks), so
                    it isn't implemented.
  help              Show this message.

What it scans:
  Files (via ~/bin/backlog-scan):
    TODO.md · stories/ready · stories/drafts · helping-hands ·
    REVISIT.md (pending) · open PRs · stale branches
    (HUMAN-REVIEW open items are scanned too but never offered as a
     pick — surfaced as a non-blocking "waiting for your eyes" aside.)
  This conversation:
    outstanding loose ends from the current session — things the
    assistant said it'd do, surfaced-but-not-acted-on items, parked
    sub-tasks. Forward-only (not /sup's recap); deduped against the
    backlog + what's already committed; not-mine items go to an aside.
    Conversation candidates are marked "(this session)" in the chooser.

Ranking (tiebreakers in order):
  unblocks-downstream → makes-other-work-easier → removes-risk →
  matches-capacity → continuity → smaller-concrete-wins

Also: after you pick, a conservative context-window check may suggest a
fresh session / clear / compact — only when remaining context is genuinely
low AND the pick is substantial. Reads ~/.claude/state/context-remaining.

Companion to /sup (situation-report-first; same ranking as a
non-blocking list, no prompt). /next is forward-only, no recap, and
presents the options as an interactive AskUserQuestion chooser.

See SKILL.md for full reference.
```

## Related

- **`/sup`** — situation-report-first; recaps this window then emits one pick. Cold-resume tool. Shares the `backlog-scan` machinery with `/next`.
- **`/sitrep`** — the unembellished base report `/sup` wraps.
- **`/todo`**, **`/revisit`**, **`/helping-hands`** — the skills that _file into_ the surfaces `/next` reads. `/next` is the read-and-choose side of those.
