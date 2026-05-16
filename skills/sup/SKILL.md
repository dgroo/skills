---
name: sup
description: Personalized situation report — mirrors /sitrep's full output, actively scans for queued work and recommends a specific pick, then issues a high-confidence new-session recommendation in bold yellow when warranted. Use when resuming a session, asking "where were we?", or when the chunk of work feels finished.
allowed-tools: Read, Glob, Grep, Bash, Agent, TaskList
---

# Sup — Situation Report (Derek's flavor)

`/sup` is a **strict superset of `/sitrep`** with two additions: (1) it actively scans the repo for queued work and recommends a specific pick, and (2) it evaluates whether to recommend a fresh Claude session.

`/sitrep` itself is upstream-tracked (joewalnes/skills) and intentionally left untouched. Use `/sup` instead.

## Sequence

1. **Produce the full sitrep output** (see "Sitrep mirror" below). Never drop sections that sitrep would include — especially **Next steps**.
2. **Scan the backlog and recommend a pick** (see "Backlog scan & pick" below). Run only when current work is parkable; otherwise skip.
3. **Evaluate the new-session recommendation** (see "New-session check" below). Most of the time, emit nothing. Only fire when the bar is genuinely cleared.

## Sitrep mirror

Gather context in parallel:

1. `git status` — uncommitted changes, untracked files, current branch
2. `git diff --stat` — what's been modified
3. `git log --oneline -5` — recent commits for context
4. `git stash list` — anything stashed
5. Check for running background tasks (TaskList tool)
6. If `scripts/upstream-check.sh` exists at repo root, run it — surfaces unpulled upstream commits. (Only meaningful in the skills repo; silently skip elsewhere.)
7. Scan conversation history for what was last discussed

Report structure (omit empty sections, keep each to 1–3 lines max):

```
## Sup

**Branch:** `branch` · **Last commit:** `short message`

**State:** Combined snapshot — clean/dirty tree, stashes, background tasks, todos, "fresh session" or "mid-task." If there's enough going on, split into the longer fields below.

**In progress:** What we were working on and how far we got. (Omit if "State" already covered it.)

**Uncommitted changes:** Brief summary of dirty files — group by intent ("new feature in X, test updates in Y") not by filename. (Omit if "State" already covered it.)

**Background:** Any tasks/processes still running. (Omit if none.)

**Todos:** Open tasks from this session (TaskList or conversation context). (Omit if none.)

**Gaps:** Half-finished things — TODO/FIXME/HACK added this session, `console.log`/`debugger`/`print(`, `.only`/`.skip` in tests, commented-out assertions, docs not updated to match code. (Omit if none.)

**Upstream:** N commit(s) ahead, paths touched. (Only when in skills repo AND `upstream-check.sh` returned output. Omit otherwise.)

**Next steps:** 1–3 concrete actions to resume work. **Always include this section** — it's the most useful single line in the whole report.

**Backlog:** One-line inventory of queued work surfaced by the scan (see "Backlog scan & pick"). Only when current chunk is parkable.

**Pick:** One specific recommendation with one-line reasoning. Only when current chunk is parkable.
```

Same rules as /sitrep: brief, one sentence per item, don't read file contents unless something in the diff looks suspicious, scan diffs for obvious unfinished markers.

## Backlog scan & pick

Run **only when the current chunk is parkable** — clean tree, or one obvious commit away from clean. If there's substantive in-flight work (mid-refactor, uncommitted changes spanning multiple files, half-applied feature), **skip this entire section**. Sitrep's Next steps already says what to resume; piling on a backlog pick is noise.

### Where to scan (parallel, skip non-existent paths)

Common surfaces, in roughly the order they tend to matter:

- `TODO.md`, `design/TODO.md` — open entries (use `/todo` and `/bug-bash` if present).
- `design/stories/ready/*.md` — stories explicitly marked ready to work on (Derek's groot-project convention). Outranks `drafts/`.
- `design/stories/drafts/*.md` — drafted but not yet promoted.
- `design/helping-hands/*.md` — items needing user action (often unblock other work).
- `gh pr list --state open --limit 10` — open PRs (skip if `gh` not installed or no GitHub remote).
- `git branch --no-merged main | head` — stale branches with unmerged work.

Project-specific patterns to recognize if they exist: `BACKLOG.md`, `ROADMAP.md`, `NOTES.md`, plus anything obvious in the working directory. **Glance briefly — don't deep-read.** Counts and titles are enough.

### What to render

Add two lines to the sitrep report, right after Next steps:

- **Backlog:** Compact inventory. Example: `TODO.md (5 open), stories/ready (3), helping-hands (2), no open PRs, 1 stale branch (refactor-auth).` Skip surfaces with zero items.
- **Pick:** One specific recommendation with one-line reasoning. Example: `Start stories/ready/payment-retry.md — ready, unblocks 2 downstream items, ~2 hours.`

If nothing's queued anywhere, render: `**Backlog:** Nothing obvious queued — what would you like to work on?` and skip the Pick line.

### Picking criteria (tiebreakers in order)

1. **Unblocks downstream work.** Helping-hands often gate other items; ready stories may be prerequisites for drafts.
2. **Removes risk.** Security, data loss, broken main, compliance.
3. **Matches session capacity.** If context is already getting full (but you're not recommending a new session), prefer something small. If fresh, can be ambitious.
4. **Continuity with current context.** If files just touched relate to a queued item, that's a strong pull.
5. **Tied?** Smaller concrete item over larger ambiguous one.

### Rules for this section

- Only recommend something you've actually seen in a file or command output. **No imagined options.**
- If you read a story/helping-hands file to check it, surface a *one-line* characterization — don't paste contents.
- Don't pad with detailed pros/cons. One pick, one reason. The user will ask if they want more.
- If you genuinely can't pick (everything looks equally good or equally unclear), say so and list the top 2–3 options for the user to choose from. Don't force a fake recommendation.

## End-of-session check

After the sitrep output, decide whether to recommend that *this* session be ended and a fresh one started for the next task.

**This signal is about the health of THIS conversation, not about where the next task happens to run.** Don't conflate the two. If your recommended pick lives in a different directory or a different repo, that's normal — *you* are not the one who would run it; the user starts a new terminal/CC instance for it whenever they're ready. The end-of-session signal fires only when continuing this same conversation for the next task would be measurably worse than starting fresh.

**Default: silence.** New sessions have real cost — the user has to re-establish context, re-orient Claude, possibly re-read files. Don't suggest that cost unless the current session has a *visible, concrete problem* that a fresh session would actually solve.

### The test

The bar is **not** "is this an OK time to stop?" (true after almost any completed task — meaningless signal). The bar is **"would continuing this conversation for the next task be measurably worse than starting fresh?"**

Recommend ending this session **only when at least one of these is observably true**:

- **Context pressure is real.** The Claude Code context indicator shows ≥50% used, OR the system has already auto-compacted, OR you (Claude) have noticed yourself re-reading files you read earlier, losing details from earlier in the conversation, or otherwise behaving like you're context-starved.
- **The conversation has drifted across multiple unrelated subtasks** *and* the next requested work is again unrelated to anything currently in cache. (Three distinct topics, with a fourth pivot incoming, is a clear case.)
- **The user has explicitly signaled a fresh-context-friendly transition** — switching projects, switching repos, "I want to start fresh on this," etc.

### Explicit non-signals

These are **not sufficient reasons** by themselves. If these are all you have, stay silent:

- Tree is clean. (That's the prerequisite, not the reason.)
- A commit was just made or a milestone was just completed. (Normal end-of-task state — default is to wait for the next task in the same session.)
- "This feels like a natural stopping point." (Most stopping points are *fine* to continue from. Naturalness is not a signal.)
- The session is short or just started. (Short sessions especially should not trigger this — the warm context is the asset.)
- **The recommended pick lives in a different working directory, repo, or terminal.** That's a property of the task environment, not of this session's health. The user runs the pick in its own session whenever they pick it up; this one stays useful for whatever comes next here. Stay silent unless one of the bullets above also fires.
- **The session has accomplished substantial work / covered a lot of ground.** Volume of completed work is not impairment. The trigger is observable loss of recall or coherence, NOT "feels like the session has been productive enough." A session that just shipped a slice + three drafts + a debug detour is doing exactly what a session is supposed to do — that's not a fresh-context signal. Don't conflate "done a lot" with "running out of room." Check the actual recall-loss signals; if none fire, stay silent.

### How to emit

When the bar is genuinely cleared, emit as a final Bash call so it renders in real terminal yellow. Phrase it so the reader can't mistake it for "you'll need another session for the next task" — it's specifically *end this one*:

```bash
# Replace <reason> with the specific observable signal — not a generic "good time to stop."
# Good: "context >70%, next slice is unrelated."
# Bad: "tree is clean, milestone shipped." (← that's just the prerequisite.)
# Bad: "the pick runs in a different scratch dir." (← that's a non-signal.)
printf '\n\033[1;33m⚠ THIS SESSION IS USED UP — start a fresh Claude session for the next task. Reason: <reason>\033[0m\n'
```

Optional prep line first, only if commits/notes/etc. are actually needed before stopping:

```bash
printf '\n\033[1;33mBefore stopping: <prep>\033[0m\n'
printf '\033[1;33m⚠ THIS SESSION IS USED UP — start a fresh Claude session for the next task. Reason: <reason>\033[0m\n'
```

If you're tempted to soften with "you could…" or "consider…" — don't. Either you have observable evidence the current session is impaired (fire), or you don't (silent). Hedged recommendations are noise.

## Rules

- The sitrep portion is non-negotiable. **Always show Next steps** when work is non-trivial.
- The new-session line is a high-confidence signal, not a hedge. If you're not sure, omit it.
- Use the `printf` commands above for the recommendation — ANSI yellow makes it impossible to miss. Don't substitute markdown bold; it doesn't pop.
- Be *brief* everywhere. This is a glance, not a report.
- Don't explain what a sitrep is or what /sup adds. Jump straight to the output.
