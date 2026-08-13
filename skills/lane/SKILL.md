---
name: lane
description: Move this session into a domain lane — a long-lived worktree for one area of a project (gameplay, ui, infra). `/lane <name>` enters that lane, creating it if needed; `/lane` with no argument reports which lane you are in, or offers the roster when you are in the main checkout. Use when asked to "put this session on the UI work", "switch to the gameplay lane", "which lane am I in", "/lane". Companion to /lanes, which decides what a project's lanes should be.
allowed-tools: Bash, Read, AskUserQuestion, EnterWorktree
---

# Lane — put this session in a lane

A **lane** is a long-lived worktree that one session sits in, named for a **domain** that outlives any feature in it (`gameplay`, `ui`, `game-ai`) rather than for a feature (`kickoff`, `nav-polish`). It is how several sessions work one repo in parallel without tripping over each other.

**`/lane` enters a lane. It never merely labels one.** That distinction is the whole skill. A session's lane *is* the directory it is sitting in — so recording "I am the gameplay lane" while sitting in the main checkout would be a claim nothing enforces: the writes still land in main, the auto-split gate still sees main, and `/standup` renders a lie. Entering makes the assignment true.

## Sequence

### 1. Find out where you are

```bash
lane --json
```

Sandbox-off — occupancy needs an unsandboxed `ps`. Each row carries `name`, `path`, `brief`, `live`, `declared`, `primary`, and `current` (the lane holding this session's cwd).

### 2. Branch on what you find

| Situation | Do |
| --- | --- |
| **Already in a lane** (a row has `current: true` and `primary: false`) | Report it in one line — lane name, brief, and how many other lanes are live. Stop. |
| **Argument given, you are in the main checkout** | `lane <name> --no-session` to ensure the worktree, then `EnterWorktree(path=<that path>)`. |
| **No argument, in the main checkout, lanes exist** | Offer them with `AskUserQuestion` — one option per lane, the brief as the description. Then enter the chosen one. |
| **No argument, no lanes exist** | Say so and offer `/lanes`, which works out what this project's lanes should be. Do not invent one on the spot. |
| **Already in a lane, and asked for a different one** | Refuse, and say why — see the limit below. |

### 3. Entering

```bash
lane <name> --no-session      # ensure the worktree + branch; starts no session
```

Then `EnterWorktree` with the `path` from `lane --json`. Not `name` — that would create a *new* worktree under `.claude/worktrees/` instead of entering the lane's.

Confirm afterward in one line: which lane, its brief, and its branch. If the lane had no brief, that is worth one sentence — `lane <name> "…"` sets it and an unbriefed lane is invisible to `/standup` and the roster.

## The one hard limit

**You cannot hop from one lane to another mid-session.** `EnterWorktree(path=…)` accepts any path in `git worktree list` on first entry from the launch directory — so main-checkout → lane works — but a session already inside a worktree may only switch to one under `.claude/worktrees/` of the same repo, and this convention puts lanes at `~/code/worktrees/<project>/<slug>/`.

This is the correct limit, not a gap to work around: **one session, one lane, long-lived.** Changing lanes means a different session. When asked, say that, and offer `lane <name>` from a terminal (or `/spawn`) to start one there instead.

## Judgment

- **Do not enter a lane that already has a live session.** `lane --json` says which are `live`. A second session in one lane is the collision worktrees exist to prevent — report where the existing session is instead.
- **Watch the name.** If asked to create a lane named for a feature (`kickoff`, `nav-polish`, `fix-the-clock`), say so before creating it: the test is whether the name is still true in a month. Offer the domain it belongs to. Create it anyway if the user reaffirms — it is their call, and a bad lane name is cheap to abandon.
- **Uncommitted work does not travel.** Entering a lane changes the working directory; edits in the old one stay there. If `git status` is dirty before entering, say so and let the user decide.

## Related

- `/lanes` — works out what a project's lanes *should be*, from the tree and the commit history. Run it first on a project with no lanes.
- `~/bin/lane` — the primitive underneath (`lane`, `lane <name> "<brief>"`, `lane --cluster`). Use it from a terminal when there is no session yet.
- `/standup` — who is waiting on you across lanes.
- `groot-claude-coord/design/session-teams/DESIGN.md` §1 — why identity is discovered rather than declared.
