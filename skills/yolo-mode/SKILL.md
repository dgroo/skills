---
name: yolo-mode
description: Bounded-autonomous "work overnight while I sleep" mode. Pushes forward safely on the design/docs backlog inside an isolated git worktree, keeps a human-readable review log, makes atomic commits, and defers destructive ops to a queue instead of running them. Fans work out to subagents to extend session endurance. Use when the user says "work on this overnight", "see what you can get done while I sleep", "yolo mode", or "/yolo-mode". For true unattended running the session must be launched with --dangerously-skip-permissions (or accept-edits) — the skill is the behavioral half only.
argument-hint: [<task or scope hint> | --code | --branch <name>]
---

# yolo-mode

Bounded autonomy for "I'm going to bed — see what you can get done overnight." The contract: **push forward as far as you safely can, make every step reviewable, and make the whole night trivially throw-away-able.** It is the closest safe approximation of "do all the work in `design/` with `--dangerously-skip-permissions`" — without the part where a 2am mistake lands on `master`.

The two halves of "run overnight" are independent, and this skill only owns one of them:

- **Behavioral half (this skill):** what to work on, how to stay safe, how to leave a reviewable trail.
- **Permission half (NOT this skill):** a skill is just an injected prompt — it cannot grant itself permissions. A normal session will still stop at the first permission prompt at 2am. For genuinely unattended running, **the user must launch the session with `--dangerously-skip-permissions`** (or run in accept-edits mode). Surface this at the top of every run if you can't tell the session is already in such a mode.

## When to use

- "I'm going to bed, work on X overnight" / "see what you can get done while I'm asleep."
- The user wants a batch of design/docs backlog progress they can review and selectively keep or discard in the morning.
- `/yolo-mode`, "yolo mode", "go heads-down on the backlog."

## When NOT to use

- A single well-scoped task the user is watching → just do it; this is overhead.
- Anything where each change needs the user's eyes before the next one → that's interactive, not yolo.
- Production, shared systems, paid-API-on-usage work → out of scope by design (see Safety).

## The contract (non-negotiable)

These are the invariants. If you cannot satisfy one, stop and say so rather than relaxing it.

| Invariant                                                                                       | Why                                                                                                                    |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Isolated worktree + dedicated branch.** Never run yolo-mode on the working checkout.          | Discard the whole night with `git worktree remove` + drop branch; review with `git diff master`.                       |
| **Atomic commits, one logical change each.**                                                    | Individual changes can be reverted without unpicking a megacommit.                                                     |
| **A human-readable running log** (`YOLO-LOG.md` at the worktree root, committed on the branch). | The morning review surface. Lives on the branch so it's discarded along with the work if the night is thrown away.     |
| **Destructive ops are deferred, never run** (`YOLO-QUEUE.md` at the worktree root).             | Respects the global "destructive commands need per-instance confirmation" rule by _deferring_ rather than _bypassing_. |
| **Stay in the allowed scope** (design/docs by default).                                         | Tiny blast radius; nothing wakes up broken.                                                                            |
| **Anchor on the project goal before going to find new work.**                                   | The "find new work if stuck" behavior is where autonomy drifts furthest from intent.                                   |

## Phase 1 — Set up the isolated workspace

1. **Confirm the permission half.** If you can detect the session is _not_ in skip-permissions / accept-edits mode, say so up front: yolo-mode will stall on the first prompt; the user should relaunch with `--dangerously-skip-permissions`. Proceed anyway (the user may have it set), but don't pretend it's unattended if it isn't.
2. **Create the worktree + branch.** Invoke the `superpowers:using-git-worktrees` skill (or `git worktree add`). Location convention: `~/code/worktrees/<project>/yolo-<short-scope>/`, branch `yolo/<short-scope>`. Base off the current branch's HEAD.
3. **Seed the artifacts** at the worktree root:
   - `YOLO-LOG.md` — header with the start time (the user passes timestamps; don't synthesize), the goal as you understand it, the allowed scope, and the launch-mode note. Entries appended newest-last so the morning read is chronological.
   - `YOLO-QUEUE.md` — header explaining it holds deferred destructive/blocking actions for the user to run by hand.
4. **State the plan back** in one short message: branch name, worktree path, allowed scope, and the goal you're anchoring on. This is the last thing the user reads before bed — make it scannable.

## Phase 2 — The work loop

Repeat until a stopping condition (see Phase 4):

1. **Pick the next in-scope item.** Prefer the project's own queued-work surfaces — `TODO.md`, `design/stories/ready/`, `REVISIT.md` items that are due, `helping-hands` items you can advance LLM-side. When you have to _go find_ new work, first run the **goal anchor**: "what are this project's goals, and does this candidate serve them?" If unsure, log the candidate and skip it rather than doing speculative work.
2. **Do the work.** Follow the project's normal conventions (tests, lint, atomic commits). Fan out aggressively — see Endurance below.
3. **Commit atomically** with a clear message. One logical change per commit.
4. **Append to `YOLO-LOG.md`**: what you did, which commit, and anything the user should double-check. Narrative, not a bullet dump — this is for a human waking up.
5. **Loop.**

## Endurance — fan out to subagents

A single session has a hard context ceiling; it cannot literally work all night. **The mitigation is aggressive subagent use.** Keep the orchestrator's context lean: dispatch self-contained units of work to subagents (`Agent` tool, or the `superpowers:dispatching-parallel-agents` skill for independent batches) and keep only the conclusions in the main loop. Independent items run in parallel. The orchestrator's job is to pick work, anchor on the goal, commit, and log — not to hold every file it touched in context. Treat context budget as the scarce resource that determines how long the night lasts.

## Safety — the deferred-actions queue

Never auto-run destructive or blocking commands, even in skip-permissions mode. This includes (per global CLAUDE.md): `rm`, `rmdir`, `git restore`, `git reset`, `git rebase`, `git push --force`, database drops/schema deletions, and anything that overwrites files or destroys history. Also anything touching production, shared systems, or paid-on-usage APIs.

When a task _needs_ one of these to proceed:

1. Append a precise entry to `YOLO-QUEUE.md` — the exact command, why it's needed, and what it unblocks.
2. Log that the task is blocked on a queued action.
3. **Move on to other in-scope work.** A blocked task is not a stopping condition.

This is the "put `rm` in a queue and find something else to do" behavior, made concrete.

## Scope

- **Default (v1): design/docs only** — `design/`, docs, notes, stories, READMEs, and similar low-blast-radius prose/structure work. The destructive queue rarely fires here and there's no build to wake up broken.
- **Code work is opt-in.** Only touch code when the user explicitly names it at launch (`--code`, or "you can work on the <feature> code too"). Even then, every other invariant still holds — worktree, atomic commits, deferred destructives, tests before commit.
- "Find new work if stuck" stays _within_ the allowed scope. Don't escalate from docs to code on your own initiative.

## Phase 3 — Goal anchor

Before each foray to _find_ new work (not before every commit — before every "what should I do next?"), restate to yourself: the project's goal, and whether the candidate work serves it. This mirrors the global "Keep the goal in view" stance. When the answer is "not sure," the safe move is to **log the candidate for the user and pick something clearly in-goal** — autonomy should narrow toward the goal, not wander from it.

## Phase 4 — Stopping & morning handoff

**Keep going** through: a blocked task (queue it, move on), a failed approach (log it, try another or move on), running low on one work surface (check the others).

**Stop** only when: out of safe in-scope work, out of context runway, or you hit a genuine wall that blocks _all_ remaining work (e.g., a decision only the user can make that everything depends on).

On stop, write a **morning handoff** at the end of `YOLO-LOG.md`:

- What got done (with commit range), what's queued in `YOLO-QUEUE.md`, what's blocked and why.
- The one-line decision the user should make first.
- The exact commands to **keep** (`git -C <worktree> diff master`, then merge) or **discard** (`git worktree remove <path> --force && git branch -D yolo/<scope>`) the night's work.

Leave the worktree and branch in place — the user decides keep-vs-discard, not the skill.

## Companion to

- **`bug-bash`** — autonomous work-through scoped to the _bug tracker_; no worktree/queue/scoping. yolo-mode is the safer, broader, design-first sibling.
- **`next` / `sup`** — work _discovery_ (one recommendation, human picks). yolo-mode discovers _and_ executes.
- **`superpowers:using-git-worktrees`** — the isolation primitive yolo-mode requires.
- **`superpowers:dispatching-parallel-agents`** — the endurance primitive.
- **`wrapup`** — the interactive session-end gate; yolo-mode's morning handoff is the unattended analog.

## Help

When invoked as `/yolo-mode help`, print the following block verbatim:

```
yolo-mode — Bounded-autonomous "work overnight while I sleep" mode.

Usage: /yolo-mode [<task or scope hint>] [--code] [--branch <name>]

Arguments:
  (none)            Work the design/docs backlog autonomously in an isolated
                    worktree until a real wall or out of safe work.
  <scope hint>      Narrow what to work on (e.g. "the relay docs").
  --code            Opt in to code work (default is design/docs only).
  --branch <name>   Override the yolo/<scope> branch name.
  help              Show this message.

Contract:
  - Isolated worktree + dedicated branch (never the working checkout).
  - Atomic commits; running log in YOLO-LOG.md; destructive ops deferred
    to YOLO-QUEUE.md, never run.
  - Fans work to subagents to extend session endurance.
  - Anchors on the project goal before finding new work.

Permission half (NOT granted by this skill):
  For true unattended overnight running, launch the session with
  --dangerously-skip-permissions (or accept-edits). The skill is behavioral
  only; it cannot grant itself permissions.

See SKILL.md for full reference.
```

## Related

- **`superpowers:executing-plans`**, **`superpowers:subagent-driven-development`** — for executing a _known_ plan autonomously; yolo-mode is for open-ended backlog progress, not a fixed plan.
- **`careful` / `freeze` / `guard`** (gstack) — destructive-warn and edit-scoping guardrails; complementary if installed.
