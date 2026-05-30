---
name: next
description: Forward-only "what should I pick up?" — scans the project's queued-work surfaces (TODO, ready/draft stories, helping-hands, REVISIT, open PRs, stale branches) and presents a few dependency- and leverage-ranked candidates via AskUserQuestion. Pick one or specify your own. Use when asking "what's next?", "what should I work on?", "what should I pick up?", or "/next". Companion to /sup — /next is forward-only with no situation recap and offers multiple options; /sup is situation-report-first with a single pick.
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# Next — what should I pick up?

`/next` answers one question: **"I'm free — what's the best next chunk of work?"** It scans where queued work lives, reasons about _sequencing_ (what unblocks what, what makes other work easier), and hands you a few ranked candidates to choose from.

**Companion to `/sup`, not a clone.** `/sup` is situation-report-first — it recaps this window, then emits _one_ pick only when the current chunk is parkable. `/next` skips the recap entirely and goes straight to _multiple_ forward-looking options with dependency reasoning up front. Reach for `/sup` on a cold resume ("what was I doing here?"); reach for `/next` when you already know you're done and want to choose what's next.

Both call the same scanner (`~/bin/backlog-scan`) so there's one definition of "where queued work lives" — no drift.

## Routing

| Invocation   | Does                                               |
| ------------ | -------------------------------------------------- |
| `/next`      | Scan, rank, present candidates, let the user pick. |
| `/next help` | Print usage (see [Help](#help)).                   |

## Sequence

1. **Glance at current state.** Run `git status --short`. `/next` is forward-only, but if there's substantial uncommitted in-flight work, the honest first answer is "finish/commit that" — surface it as a one-line preamble (not a candidate). Don't deep-dive; this is a glance.

2. **Scan the surfaces.** Run `backlog-scan` (no args, from anywhere in the repo). It emits a grouped, counted inventory of TODO entries, ready/draft stories, helping-hands, pending REVISIT items, open PRs, and stale branches. Use its titles for triage — read an individual file only when a candidate needs disambiguating (e.g. to confirm a dependency). **Don't deep-read everything.**

3. **Reason about sequencing, then pick 3–4 candidates.** This is the core — model judgment, not a script. Apply the [ranking criteria](#ranking-criteria) below. Look for cross-references between items (a TODO that says "full story: design/stories/…", an item "gated on" or "blocked by" another, a helping-hands item that unblocks a story). Prefer the unblocker. Group tightly-related small items into one candidate when it's natural ("the three OSC-11 / terminal-color chores").

4. **Present via AskUserQuestion.** One question, 3–4 options. Each option's label is a short pick name; its description carries the _why_ — the dependency/leverage reasoning and a rough size. The user picks one, or chooses "Other" to specify their own. (AskUserQuestion always offers Other — don't add it manually.)

5. **Context-window check (conservative, pick-scaled).** After the user picks, read the live context figure and decide whether to raise a fresh-session / clear / compact suggestion. See [context check](#context-window-check). Most of the time, emit nothing. This step comes last so it can scale to the chosen pick, and so the suggestion lands at the bottom where the eye goes.

## Ranking criteria

Tiebreakers, in order:

1. **Unblocks downstream work.** Helping-hands often gate other items; a ready story may be a prerequisite for drafts. The thing that makes _other_ things possible wins. This is the headline value of `/next` — lead candidates with it.
2. **Makes other work easier (leverage).** Infrastructure, a shared script, a refactor that several queued items would build on. Lower the cost of everything after it.
3. **Removes risk.** Broken main, security, data loss, a flaky thing that keeps biting.
4. **Matches capacity.** If context is already tight (see step 5), prefer something small and self-contained. If fresh, a candidate can be ambitious.
5. **Continuity.** If files just touched relate to a queued item, that's a real pull — less re-orientation cost.
6. **Tied? Smaller, concrete item beats larger, ambiguous one.**

Rules:

- **Only propose what the scan actually surfaced.** No imagined work. If you read a file to check it, characterize it in one line — don't paste contents.
- **State the dependency reasoning explicitly** in each candidate's description: "do X first — it unblocks Y and Z" beats "X seems important."
- **REVISIT items are time/event-gated.** Treat far-future or event-only entries as low-priority candidates unless their trigger has plausibly arrived; don't rank a "revisit in August" item above ready work.
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

Usage: /next [help]

Verbs:
  (none)            Scan, rank, and present next-work candidates via
                    AskUserQuestion. Pick one or specify your own.
  help              Show this message.

What it scans (via ~/bin/backlog-scan):
  TODO.md · stories/ready · stories/drafts · helping-hands ·
  REVISIT.md (pending) · open PRs · stale branches

Ranking (tiebreakers in order):
  unblocks-downstream → makes-other-work-easier → removes-risk →
  matches-capacity → continuity → smaller-concrete-wins

Also: after you pick, a conservative context-window check may suggest a
fresh session / clear / compact — only when remaining context is genuinely
low AND the pick is substantial. Reads ~/.claude/state/context-remaining.

Companion to /sup (situation-report-first, single pick). /next is
forward-only, no recap, multiple options.

See SKILL.md for full reference.
```

## Related

- **`/sup`** — situation-report-first; recaps this window then emits one pick. Cold-resume tool. Shares the `backlog-scan` machinery with `/next`.
- **`/sitrep`** — the unembellished base report `/sup` wraps.
- **`/todo`**, **`/revisit`**, **`/helping-hands`** — the skills that _file into_ the surfaces `/next` reads. `/next` is the read-and-choose side of those.
