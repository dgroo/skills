---
name: wrapup
description: Actively assess whether this session is safe to end. Inventories in-flight state (uncommitted changes, undocumented decisions, open tasks), proposes prep, asks permission for any writes, then gives a definitive READY / WAIT / STAY verdict. With an intent hint, also judges whether THIS session is the right place for that next chunk and pushes back if it is.
argument-hint: "[<optional intent for next work>]"
---

# Wrapup — explicit session-end readiness gate

> "Are we actually in a good place to wrap up and start fresh? If so, get us to the /sup state. If not, say so."

Use when you're about to bounce the session and want a yes-or-no answer (not silence-as-signal). Trigger phrases: "are we good to wrap?", "safe to bounce?", "can I end here?", "I'm going to start a new session if you think we are good to do so", "/wrapup", "/wrapup I'm thinking about picking up X next."

**Companion to `/sup`.** `/sup` is descriptive (situation report, default-silent on end-of-session). `/wrapup` is action-imperative (always answers, always preps). Same neighborhood, different verb class. After a successful `/wrapup` READY verdict, opening a fresh session and running `/sup` will work cleanly — that's the contract.

**Not the same as `/context-save`.** `/context-save` persists this session's working context for `/context-restore` later. `/wrapup` doesn't preserve anything cross-session — it just ensures the _vault and repo state_ would let any fresh CC session pick up cleanly.

## Three verdicts

| Verdict      | When                                                                                                                  | What                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| ✅ **READY** | Clean tree, decisions journaled, tasks resolved or written down. Or intent hint isn't a fit for this session's cache. | Confirm safe-to-bounce. End.                                                                 |
| ⏸ **WAIT**   | Something in-flight would be lost or hard to pick up cold.                                                            | List items + proposed prep, ask permission for any writes, execute approved prep, re-assess. |
| ↺ **STAY**   | Intent hint matches what this session has hot in cache. Bouncing would discard real context value.                    | Push back: explain what's in cache that helps, suggest staying. User decides.                |

## Sequence

### Phase 1: Inventory in-flight state

Gather in parallel — same shape as `/sup`'s sitrep mirror, with sharper edges on "what would be lost":

1. `git status` — uncommitted changes, untracked files. The blocker question: is any of this hand-typed work that would be hard to redo? (Lockfile churn = no; new feature half-done = yes.)
2. `git stash list` — stashes are usually forgotten. Any non-empty stash is a flag.
3. `git log --oneline <branch>..HEAD` (or `git log -5` on detached) — what shipped this session, for the journal-completeness check below.
4. **TaskList** — open tasks the conversation never closed.
5. **Conversation context** — scan for:
   - Non-trivial **decisions** made this session (architecture, tradeoffs, scope calls) that aren't in `DIARY.md` or `design/` notes yet. These are the highest-leverage "would be lost" items — code commits don't capture the why.
   - In-flight reasoning ("I was about to…", "next step is…") that isn't pinned anywhere durable.
   - Half-done refactors mentioned but not finished.

Don't read whole files — this is a scan, not an audit. Heuristic: would a fresh CC session running `/sup` on this repo have everything it needs?

### Phase 2: Judge cache-relevance (only if intent hint given)

If invoked as `/wrapup <intent>` (e.g., "/wrapup picking up next-set-bugs"), evaluate whether THIS session is well-positioned for that work _before_ doing wrap-up prep.

Three signals say STAY:

1. **Files just touched relate to the intent.** Recent edits to `idm/journals.py` and the intent says "fix next_set bugs" — the warm cache is exactly the right cache.
2. **Decisions just made inform the intent.** This session settled tradeoffs that the next chunk would otherwise have to re-derive cold.
3. **Implementation context is hot.** You just shipped slice N of a multi-slice story and the intent is slice N+1 of the same story — fresh-session restart would re-read the same files anyway.

Signals that say BOUNCE (proceed to Phase 3):

- Intent lives in a different repo, different working directory, or different code surface than this session touched.
- This session is at high context pressure (the `<context-pressure>` reminder fired, or you've been re-reading files).
- Subject is genuinely orthogonal — different story, different layer of the stack, different user goal.

If STAY: skip Phase 3, emit ↺ STAY verdict with the specific signals that fired ("recent commits in `idm/journals.py`," "this session decided <X>"). Let the user override.

### Phase 3: Propose prep (only if Phase 1 found in-flight state)

For each in-flight item, propose specific prep and **ask permission** before any write. Standard preps:

- **Uncommitted changes that should land**: propose an atomic commit with a drafted message. Ask before committing. (Per global CLAUDE.md "Never commit unless explicitly asked.")
- **Uncommitted changes that are mid-experiment**: propose either committing-as-WIP, stashing with a descriptive name, or leaving as-is with a note. Default suggestion is "leave as-is, but note it" — most mid-experiment dirt should not become a commit.
- **Decisions not journaled**: propose a `DIARY.md` entry. Show the drafted body before writing. Same propose-then-curate discipline a persona-driven journaling tool would use: draft, surface, write only on the OK.
- **In-flight todos worth not losing**: propose adding to `design/NEXT.md`, `design/stories/drafts/`, or — if the project has a `dev-inbox` — a dev-inbox entry. Default to the lightest-weight surface that won't get forgotten.
- **Open TaskList items that are actually done**: mark them completed. Items genuinely incomplete: leave open + flag in the verdict.

Execute _only_ the preps the user OKs. Re-assess afterward and proceed to Phase 4.

### Phase 4: Verdict

Emit one of the three verdicts as a bright-yellow ANSI block (visible at a glance, matches `/sup`'s end-of-session signal shape):

```bash
# ✅ READY
printf '\n\033[1;32m✅ READY TO WRAP — safe to bounce. A fresh session with /sup will pick up cleanly.\033[0m\n'

# ⏸ WAIT
printf '\n\033[1;33m⏸ NOT YET — <N> item(s) need attention first.\033[0m\n'
# Then list the items.

# ↺ STAY (intent-hint variant)
printf '\n\033[1;36m↺ STAY HERE — this session has <specific signals> in cache for <intent>; bouncing discards real context. Recommend continuing.\033[0m\n'
```

For READY and STAY, that's the whole emission — no extra prose. For WAIT, list the items below the yellow block with explicit next steps the user can act on.

## Output expectations

- **One verdict per invocation.** Don't hedge across two verdicts ("READY-ish but maybe STAY"). Pick the one that fits and explain.
- **The yellow block is the headline.** Anything above it is inventory; the block itself is the answer.
- **Brief above the block.** If READY, no prose needed — yellow line alone. If WAIT, items list below. If STAY, the rationale is _inside_ the yellow line; expand only if the user asks.
- **Don't repeat /sup's content.** `/wrapup` is not a sitrep. Don't list the backlog, don't recommend a pick, don't reproduce git status. That's `/sup`'s job after the bounce.

## Companion to /sup

The READY verdict's contract: after the user bounces and runs `/sup` in a fresh session, the new session has everything it needs. That's why journal-completeness, NEXT-currency, and "uncommitted decisions" matter as inventory items — they're the things `/sup` can't recover if `/wrapup` didn't catch them first.

If you're tempted to skip the journal-decisions check because "the diff captures it" — don't. The commit message captures _what_; DIARY entries capture _why_. A fresh session reads `git log` and sees the _what_; only the DIARY tells it the _why_.

## Rules

- **Always emit a verdict.** Silence is the bug this skill exists to fix.
- **Never silently auto-commit.** Even when the path is obvious, ask. Mid-experiment dirty trees are sometimes intentional.
- **DIARY entries: propose, don't write.** Show the drafted body, get the OK, then write. No silent journal entries.
- **STAY is high-confidence only.** If you're not sure whether the cache actually helps the named intent, lean READY and let the user push back. Don't manufacture a STAY out of "well, you've been working here."
- **One sentence per inventory item.** This is a glance, not a report.

## Help

When invoked as `/wrapup help`, print the following block verbatim:

```
wrapup — Actively assess whether this session is safe to end; prep if needed; give a definitive verdict.

Usage: /wrapup [<optional intent for next work>]

Arguments:
  (none)            Inventory in-flight state; propose prep; emit READY or WAIT.
  <intent>          Same + judge whether THIS session is the right place
                    for that intent. May emit STAY instead.

Verdicts:
  ✅ READY          Clean handoff state. Bounce + /sup will work.
  ⏸ WAIT            N items need attention first. List + prep proposals follow.
  ↺ STAY            Intent hint is hot in this session's cache. Recommend staying.

Verbs:
  help              Show this message.

Companion to /sup (descriptive sitrep). See SKILL.md for full reference.
```
