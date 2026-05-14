---
name: sup
description: Personalized situation report — mirrors /sitrep's full output (Branch, State, Next steps, etc.), then issues a high-confidence new-session recommendation in bold yellow when warranted. Use when resuming a session, asking "where were we?", or when the chunk of work feels finished.
allowed-tools: Read, Glob, Grep, Bash, Agent, TaskList
---

# Sup — Situation Report (Derek's flavor)

`/sup` is a **strict superset of `/sitrep`**: it produces the full sitrep output first (never drops sections, especially Next steps), then evaluates one additional thing — whether to recommend a fresh Claude session.

`/sitrep` itself is upstream-tracked (joewalnes/skills) and intentionally left untouched. Use `/sup` instead.

## Sequence

1. **Produce the full sitrep output** (see "Sitrep mirror" below). Never drop sections that sitrep would include — especially **Next steps**.
2. **Then evaluate the new-session recommendation** (see "New-session check" below). Most of the time, emit nothing. Only fire when both conditions are clearly met.

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
```

Same rules as /sitrep: brief, one sentence per item, don't read file contents unless something in the diff looks suspicious, scan diffs for obvious unfinished markers.

## New-session check

After the sitrep output, decide whether to recommend a fresh Claude session.

**Default: silence.** New sessions have real cost — the user has to re-establish context, re-orient Claude, possibly re-read files. Don't suggest that cost unless the current session has a *visible, concrete problem* that a fresh session would actually solve.

### The test

The bar is **not** "is this an OK time to stop?" (true after almost any completed task — meaningless signal). The bar is **"would continuing this session be measurably worse than starting fresh?"**

Recommend a new session **only when at least one of these is observably true**:

- **Context pressure is real.** The Claude Code context indicator shows ≥50% used, OR the system has already auto-compacted, OR you (Claude) have noticed yourself re-reading files you read earlier, losing details from earlier in the conversation, or otherwise behaving like you're context-starved.
- **The conversation has drifted across multiple unrelated subtasks** *and* the next requested work is again unrelated to anything currently in cache. (Three distinct topics, with a fourth pivot incoming, is a clear case.)
- **The user has explicitly signaled a fresh-context-friendly transition** — switching projects, switching repos, "I want to start fresh on this," etc.

### Explicit non-signals

These are **not sufficient reasons** by themselves. If these are all you have, stay silent:

- Tree is clean. (That's the prerequisite, not the reason.)
- A commit was just made or a milestone was just completed. (Normal end-of-task state — default is to wait for the next task in the same session.)
- "This feels like a natural stopping point." (Most stopping points are *fine* to continue from. Naturalness is not a signal.)
- The session is short or just started. (Short sessions especially should not trigger this — the warm context is the asset.)

### How to emit

When the bar is genuinely cleared, emit as a final Bash call so it renders in real terminal yellow:

```bash
# Replace <reason> with the specific observable signal — not a generic "good time to stop."
# Good: "context >70%, next slice is unrelated."
# Bad: "tree is clean, milestone shipped." (← that's just the prerequisite.)
printf '\n\033[1;33m⚠ NEW SESSION RECOMMENDED — <reason>\033[0m\n'
```

Optional prep line first, only if commits/notes/etc. are actually needed before stopping:

```bash
printf '\n\033[1;33mBefore stopping: <prep>\033[0m\n'
printf '\033[1;33m⚠ NEW SESSION RECOMMENDED — <reason>\033[0m\n'
```

If you're tempted to soften with "you could…" or "consider…" — don't. Either you have observable evidence the current session is impaired (fire), or you don't (silent). Hedged recommendations are noise.

## Rules

- The sitrep portion is non-negotiable. **Always show Next steps** when work is non-trivial.
- The new-session line is a high-confidence signal, not a hedge. If you're not sure, omit it.
- Use the `printf` commands above for the recommendation — ANSI yellow makes it impossible to miss. Don't substitute markdown bold; it doesn't pop.
- Be *brief* everywhere. This is a glance, not a report.
- Don't explain what a sitrep is or what /sup adds. Jump straight to the output.
