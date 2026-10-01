---
name: request
description: Ask another project's agents for a change instead of editing their repo. Use when a fix belongs in another repository.
argument-hint: <project> "<title>" | inbox | sent | show <id> | accept|decline|done <id>
---

# Request: work across projects without stomping

Projects depend on each other: zepto needs a fix in hangon; a sidebrain retro finds skill improvements for the skills repo. The old way — jump into `../otherproject` and fix it yourself — puts you in someone else's checkout with no knowledge of their in-flight branches, leases, or conventions, and their agents in yours. Agents stomped on each other.

This is the mailbox pattern real teams use: **you never edit another project's repository.** You file a request; their agents triage it under their own rules, in their own worktrees, and tell you when it's done.

## Where requests live, and why

`~/.claude/requests/<target-project>/<id>.md` — one file per request, **outside every checkout.**

- No git conflicts and no writes into anyone's working tree, however dirty or mid-merge it is.
- Worktree-independent: the target may have thirty worktrees or no session running; the request waits.
- A project is identified by the basename of its *main* checkout (`git rev-parse --git-common-dir`), so a request filed from a worktree still says `zepto`, and one addressed to `sidebrain` is found from any of its worktrees.
- The transport is the file; **the record is the target's own tracker.** When the target accepts, its agent copies the request into its `ASKS.md`/`TODO.md` with provenance and commits — the git-tracked event is made by the owner, in their repo.

Override the location with `$CLAUDE_REQUESTS_DIR`, the project name with `--project` or `$CLAUDE_REQUESTS_PROJECT`. Two repos with the same basename would share an inbox; rename one or set the override.

## Sending

```bash
python3 ~/.claude/skills/request/scripts/request.py send <project> "<title>" \
  --body "<what you observed (measured), and what you need>" \
  [--repro "<how to see it>"] [--hunch "<your guess at the cause>"] [--priority blocking|normal|low]
```

Write the request the way a good brief is written, because it *is* one:

- **Observation and goal first.** What you saw, marked as measured where it is; what you need to be true afterwards. Not a diagnosis.
- **Your hunch goes last, labelled.** A diagnosis at the top tells a capable agent where to look, and they look there — two rounds were once spent fixing a normaliser when the data was stored elsewhere. The target forms its own view first, then checks yours.
- **Repro if you have one.** The target can't see your screen.
- **Priority `blocking`** only if your work is actually stopped. It sorts their inbox.

The script prints two follow-ups: a one-line `SendMessage` ping to use **only if** the target has a live session (check `ListAgents`; the ping carries the id and title, never the content — the file is the record), and a reminder to note the dependency in your own tracker ("Waiting on hangon 20260903-…: title") so it shows up in your `/sitrep`.

Then get on with something else. Do not go and fix it yourself.

## Receiving

```bash
python3 ~/.claude/skills/request/scripts/request.py inbox          # open + accepted, blocking first
python3 ~/.claude/skills/request/scripts/request.py show <id>      # ids prefix-match, like git SHAs
python3 ~/.claude/skills/request/scripts/request.py accept <id> --note "reproduced; scheduling"
python3 ~/.claude/skills/request/scripts/request.py decline <id> --reason "..."
python3 ~/.claude/skills/request/scripts/request.py done <id> --ref <sha|branch|PR>
```

`/sitrep` shows the inbox. `/go-team` dispatches from it — **after** the human's own `ASKS.md`, **before** the project's self-generated backlog: a blocked peer is external demand, not work the fleet invented for itself. On accept, copy the request into your tracker with its id; on done, record the ref so the requester can pull it. Decline with a reason rather than letting it rot — the requester is waiting on an answer either way.

## Checking on what you sent

```bash
python3 ~/.claude/skills/request/scripts/request.py sent [--all]
```

`/sitrep` includes this. When one turns `done`, the ref tells you what to pull or bump.

## The rule, and the mechanism that enforces it

**Never edit a repository other than the one you were dispatched into.** Written down, that's an intention. The mechanism is `scripts/guard_foreign_repo.py`, a `PreToolUse` hook on `Edit|Write|MultiEdit|NotebookEdit` that denies a write whose target is inside a *different* git repository and replies with the `request.py send` line to use instead. Same-repo worktrees, `~/.claude`, and temp directories are allowed. `/project-setup` installs it (by reference, so it never goes stale).

It does not police `Bash` — `cd ../other && …` is unguardable in general — so the rule still has to be in every dispatch brief. But the common case, an agent reaching for Edit on a sibling repo's file, is refused before it happens.
