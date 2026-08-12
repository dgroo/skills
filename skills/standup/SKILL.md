---
name: standup
description: Who is waiting on you, across every Claude Code session on this host. Sorted longest-stall-first, because you are the bottleneck in the conversations you are running in parallel. Use when asking "is anyone waiting on me?", "what's stuck?", "standup", "/standup", or when returning to a project after working elsewhere. Scope defaults to the current project; `/standup all` covers the host. Distinct from /sup (this session's situation) and /roci-sitrep (whole-host vitals).
allowed-tools: Read, Bash
---

# Standup — who is waiting on you

`/standup` answers one question: **"which of my sessions is stalled on me right now?"**

When several sessions run at once, each is a conversation you are personally in — and the cost that hurts is not two sessions colliding on a file. It is a session that asked you something forty minutes ago while you were talking to a different one. That stall is invisible from every seat: the waiting session shows nothing in the terminal you are looking at, and you only find it by tabbing around.

**Not a status report on autonomous workers.** This is your own queue.

## Scope

| Form | Behavior |
| --- | --- |
| `/standup` | The project owning the cwd (worktrees roll up to their checkout) |
| `/standup all` | Every project on this host |
| `/standup <project>` | One named project |
| `/standup <N>h` | Widen the stale window to N hours (e.g. `/standup 72h`) |

## Sequence

### 1. Read the board

```bash
cc-session-board --waiting --here          # /standup
cc-session-board --waiting                 # /standup all
cc-session-board --waiting --project NAME  # /standup <project>
cc-session-board --waiting --stale-hours N # widen the window
```

**Run it sandbox-disabled.** Liveness needs an unsandboxed `ps`; inside the sandbox every session reads as dead and the answer is a confident, wrong "nothing waiting on you."

Add `--json` when you need the `tmux` / `cmux` coordinates to tell Derek where a session lives.

### 2. Report it, then add what the tool cannot know

Print the tool's output as-is — the columns are urgency, how long it has been stalled, the lane, and what was asked. Then add the judgment a script has no basis for:

- **Which one to take first**, if it is not simply the longest wait. A `blocked` permission prompt is a five-second unblock; an `asked` design question may be twenty minutes of thinking. Say so when the order by cost differs from the order by age.
- **What the question actually is**, when the captured message is truncated or generic ("Claude needs your permission" is all a permission prompt carries). Read the session's `tldr` from `cc-session-board --json` for context rather than guessing.
- **Whether it is still live.** A session may have been asked something an hour ago and moved on without the queue clearing. If the tl;dr has clearly advanced past the question, say it looks resolved rather than presenting it as open.

### 3. The stalled count is a real line, not noise

Waits older than the window print as `+N stalled >24h`. **Never drop it.** It is the difference between "nobody is waiting" and "nobody is waiting *recently*", and the second one is how a question goes unanswered for four days. If the count is more than two or three, suggest `/standup 200h` to look at what accumulated.

### 4. Nothing waiting is a real answer

`nothing waiting on you` is the good case and should be reported plainly in one line. Do not pad it, and do not go hunting for other work to report — that is `/next`.

## What this is not

- **Not `/sup`.** `/sup` is this session — where were we, what is uncommitted, what to pick up. `/standup` is every *other* session and one question only.
- **Not `/roci-sitrep`.** That is host vitals, git fleet, services, relay. This is attention.
- **Not `/next`.** This tells you who is blocked, not what to work on.
- **Not yet the full standup.** The design (`groot-claude-coord/design/session-teams/DESIGN.md` §7) has four sections: waiting-on-you, what each conversation is about, mechanical trouble (main red, a lane behind, a wrapped lane with unlanded work), and what landed. **Only §1 is built.** Do not improvise the other three from partial data — say they are not built if asked.

## Related

- `~/bin/cc-session-board` — the primitive; `--waiting` is this skill's whole data path
- `~/.claude/hooks/_waiting_queue.py` — the store, written by the notification and stop hooks
- `groot-claude-coord/design/session-teams/DESIGN.md` — the design, and what §2–4 will add
- `/sup`, `/next`, `/roci-sitrep` — the neighbours above
