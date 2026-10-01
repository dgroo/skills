---
name: sitrep
description: Where were we? Branch, in-progress work, blocked agents, inbox, next steps. Use when resuming a session.
allowed-tools: Read, Glob, Grep, Bash, Agent, ListAgents, TaskOutput, CronList
---

# Situation Report

Give a brief, scannable status report for the current session and working directory. Prioritize signal over completeness — skip sections that have nothing to report.

## Gather context

Run these in parallel:

1. `git status` — uncommitted changes, untracked files, current branch
2. `git diff --stat` — what's been modified
3. `git log --oneline -5` — recent commits for context
4. `git stash list` — anything stashed
5. **`ListAgents`** — background agents and other sessions (see below)
6. `python3 ~/.claude/skills/request/scripts/request.py inbox` and `… sent` — work other projects have asked of this one, and what this one is waiting on elsewhere (skip silently if the script isn't installed)
7. `ASKS.md` (or whatever `CLAUDE.md` names as the requests lane), if present — the human's own top open ask
8. If `$(git rev-parse --git-common-dir)/leases/` is non-empty, `CronList` — a fleet with leases and no scheduled `/go-team` job is a fleet nobody is ticking (measured: four such fleets sat 90–99% idle). That goes under **Needs you**.
9. `python3 ~/.claude/skills/consolidate/scripts/consolidate.py --check` — one line: is the unpushed range reader-ready, or how many commits would become how many (the pre-push gate will refuse the latter)
10. Scan the conversation history you have in context for what was last discussed

### Reading the agent roster

`ListAgents` returns every peer session, agent, and cloud run on the machine — across *all* projects. Most of it is noise for this sitrep.

**Scope to this project first.** Take the project name as the basename of the git root (`git rev-parse --show-toplevel`, falling back to the cwd). Keep only:

- subagents spawned by *this* session (always relevant), and
- sessions whose name, tmux session, or title contains the project name — peer sessions are named after their project directory (`websocketd-9a`, `zepto`), and cloud runs carry a descriptive title.

Drop everything else. A sitrep run in `websocketd` reporting that `sidebrain` is busy is confusing, not informative — the human is here, not there. The one exception: if sessions in *other* projects are `waiting`, add a single trailing line — a count, not a list — e.g. "2 sessions in other projects are waiting on you (`/sitrep` there for detail)". Never enumerate other projects' work.

For the sessions that survive the filter, each has a **status** — and the status is the whole point:

| Status | Means | Report it? |
|---|---|---|
| `waiting` | **Blocked on a human — a permission prompt or a question.** | **Always. This is the headline.** |
| `busy` | Actively working | Yes, one line: name and what it's on |
| `idle` | Finished, or has nothing queued | Only if it just finished something, or is unexpectedly idle |
| `shell` | Dropped to a shell | Only if unexpected |
| `offline` | Disconnected (Remote Control) | Summarize as a count, don't enumerate |

A `waiting` session is time that is being *wasted right now* — an agent that hit a permission dialog at 2am and has been parked ever since. Surface it first, name what it's waiting on if you can tell, and say what would unblock it.

**Don't message agents to interrogate them.** `SendMessage` interrupts work in progress and turns a glance into a conversation. The session name plus status is normally enough. If the human wants depth on one, offer to follow up on that one.

**Even within the project, don't enumerate everything.** Enumerate `waiting` and `busy`; collapse `idle`/`offline` to a count.

### Background tasks in *this* session

For work backgrounded from this session, `<task-notification>` messages report completion, and the tool result gives an output file path.

- **Backgrounded bash** (`run_in_background`): `Read` the output file, or tail it, for real progress.
- **Async agents** (`Agent` tool): use the result from its completion notification. **Never `Read` an agent's `.output` file** — it's a symlink to the full JSONL conversation transcript and will blow up your context, which for a skill whose entire job is a quick glance is a self-inflicted wound.
- A task that notified completion *earlier in this conversation* is done. Don't re-check it, and don't report it as running.

## Report format

Use this structure. **Omit any section that's empty.** Keep each section to 1–3 lines max.

```
## Sitrep

**Branch:** `branch-name` · **Last commit:** `short message`

**⚠ Needs you:** Anything stalled on a decision, a permission prompt, or an action only you can take. Name the session and what would unblock it. Omit this section entirely when nothing is blocked — never pad it with "nothing blocked".

**In progress:** What we were working on and how far we got.

**Your lane:** The top open item in `ASKS.md` and its status — is anyone on it? Omit if the project has no requests lane.

**Inbox:** Requests from other projects (`request.py inbox`): count, and the blocking ones by title. **Sent:** what this project is waiting on elsewhere, and anything that turned `done` since last time (with its ref). Omit either when empty.

**Background:** Agents/sessions currently working, one line each — name and what it's on. Collapse idle/offline ones to counts. Note anything that finished since the last check.

**Unpushed:** the `--check` line — `11 commits, reader-ready`, or `56 → 41: run /consolidate before pushing`. Omit when nothing is unpushed.

**Uncommitted changes:** Brief summary of dirty files — group by intent (e.g. "new feature in X, test updates in Y") not just file names.

**Todos:** Open tasks from this session (from conversation context).

**Gaps:** Things that look unfinished — e.g. TODO/FIXME/HACK added this session, temp debug code, tests that were skipped or commented out, docs not updated to match code changes, half-done refactors.

**Not done:** What was explicitly skipped, deferred, or left out this session, and why — the omissions list. Reporting completions while omitting omissions is how a designed-and-approved feature once sat unbuilt for twelve hours.

**Next steps:** 1–3 concrete actions to resume work.
```

**"Needs you" goes first, above everything.** A blocked agent is the only part of a sitrep that is actively costing something while the human reads it. Everything else is history; this is the bill still running.

## Rules

- Be *brief*. This is a glance, not a report. One sentence per item.
- Don't explain what a sitrep is. Jump straight to the output.
- Don't read file contents unless something looks suspicious in the diff — just use filenames and git output.
- If the session is fresh with no history, say so and summarize repo state instead.
- For gaps, scan `git diff` output for obvious markers: `TODO`, `FIXME`, `HACK`, `console.log`, `debugger`, `binding.pry`, `print(`, commented-out test assertions, `.only` / `.skip` in tests.
- **Report agent status, don't infer it.** "Still running" means the roster says `busy` — not that you haven't heard otherwise. If a task notified completion earlier in this conversation, it is done. Never guess at or predict a pending agent's results.
- **Don't let the roster crowd out the repo.** A sitrep in a working directory is about that directory. Other projects' sessions are filtered out entirely (see *Scope to this project first*) — the only thing that crosses over is a one-line count of `waiting` sessions elsewhere.
