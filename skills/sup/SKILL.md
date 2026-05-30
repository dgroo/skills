---
name: sup
description: Personalized situation report — mirrors /sitrep's full output, actively scans for queued work and recommends a specific pick, then issues a high-confidence new-session recommendation in bold yellow when warranted. Use when resuming a session, asking "where were we?", or when the chunk of work feels finished.
allowed-tools: Read, Glob, Grep, Bash, Agent, TaskList
---

# Sup — Situation Report (Derek's flavor)

`/sup` is a **strict superset of `/sitrep`** with three additions: (1) a **Session recap** that answers "wait, what the hell was I doing in this terminal window?" for cold returns, (2) actively scanning the repo for queued work and recommending a specific pick, and (3) evaluating whether to recommend a fresh Claude session.

`/sup` answers two questions equally: "where are we with this project, what's next?" _and_ "what was happening in this window when I walked away?" The Last-commit line carries a relative timestamp so the reader can gauge staleness at a glance — the longer it's been, the more the Session recap is doing the work.

`/sitrep` itself is upstream-tracked (joewalnes/skills) and intentionally left untouched. Use `/sup` instead.

## Sequence

1. **Produce the full sitrep output** (see "Sitrep mirror" below). Never drop sections that sitrep would include — especially **Next steps**.
2. **Surface sibling sessions and relay state** (see "Sibling sessions & relay" below). Always runs — independent of whether current work is parkable. If a hot sibling matches what the user just typed `/sup` to find, it outranks anything in the backlog scan.
3. **Scan the backlog and recommend a pick** (see "Backlog scan & pick" below). Run only when current work is parkable; otherwise skip. If a hot sibling already covers the candidate pick's topic, defer to the sibling instead of recommending a fresh pick here.
4. **Evaluate the new-session recommendation** (see "New-session check" below). Most of the time, emit nothing. Only fire when the bar is genuinely cleared.

## Sitrep mirror

Gather context in parallel:

1. `git status` — uncommitted changes, untracked files, current branch
2. `git worktree list` — sibling worktrees and their branches. Critical orientation step: a sibling whose branch name matches the current/upcoming task topic is almost always the right home for that work, and silently editing on `main` when a topic-named worktree exists is the bug this step prevents.
3. `git diff --stat` — what's been modified
4. `git log -5 --format='%h %s (%cr)'` — recent commits with **relative timestamps**. The most recent commit's `(Xh ago)` / `(3 days ago)` lands on the Branch/Last-commit line of the report; it's the cheapest staleness signal for "have I been away from this window?"
5. `git stash list` — anything stashed
6. Check for running background tasks (TaskList tool)
7. If `scripts/upstream-check.sh` exists at repo root, run it — surfaces unpulled upstream commits. (Only meaningful in the skills repo; silently skip elsewhere.)
8. `python3 ~/.claude/skills/sup/sibling-sessions.py` — surfaces other CC sessions active in this project's cwd within the last 2 hours, with a topic hint per session. Prints nothing when no siblings; just include verbatim.
9. If `design/relay/STATE.md` exists, run `relay-status` for a one-line relay state; silently skip if the file doesn't exist or `relay-status` isn't on PATH.
10. Scan conversation history for what was last discussed

Report structure (omit empty sections, keep each to 1–3 lines max):

```
## Sup

**Branch:** `branch` · **Last commit:** `short message` _(Xh ago)_

**Worktrees:** Only when `git worktree list` shows >1 entry. Render each as `path · branch · commit`. If any sibling's branch name plausibly matches the current task topic or what's about to be discussed, explicitly flag: `→ This work likely belongs on <branch> — confirm before editing on main.` Don't ask reflexively when siblings exist for unrelated topics; only flag when there's a topic match.

**Sibling sessions:** Verbatim block from `sibling-sessions.py` when non-empty. Omit when the script prints nothing. If any sibling's topic plausibly matches what the user just invoked `/sup` for (continuing recent work, post-`/clear` confusion), explicitly flag `→ Looks like that work is live in `<id>` — switch windows rather than restarting here.` See "Sibling sessions & relay" section.

**Relay:** One-line summary of `relay-status` output when in a project with `design/relay/STATE.md`. Examples: `⚪ parked since 2026-05-21` or `🟢 active on rocinante24, last handoff 2026-05-21T02:51Z`. Omit when no relay scaffolding.

**State:** Combined snapshot — clean/dirty tree, stashes, background tasks, todos, "fresh session" or "mid-task." If there's enough going on, split into the longer fields below.

**Session recap:** Short bulleted list of what THIS conversation accomplished — the "what was I doing in this terminal" answer. Always emit. 3–6 short bullets, one concrete action each (1–2 bullets fine for a tiny session — don't pad). Order: commits first (with explicit repo names, e.g. `Committed `58c2d81` to dgroo/dotfiles`), then decisions / drafts / discussed-but-not-shipped items. Source: conversation scrollback (what the assistant actually did this session), NOT `git log` alone — commits miss decisions and drafts, which are the things you don't remember. For a genuinely fresh session (no prior turns), render `_Fresh session — no prior activity in this window._` If session covered multiple distinct topics, focus on the most recent.

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

## Sibling sessions & relay

The `/sup` failure mode this section exists to prevent: user has multiple CC sessions open in the same project (common in hub-shaped repos like `remote-coding-setup` and split-workload projects like Changer), `/clear`s one, runs `/sup`, and gets a recommendation that ignores the active thread sitting in another window. Result: starts duplicate or conflicting work.

### Sibling sessions (local)

Source: `python3 ~/.claude/skills/sup/sibling-sessions.py`. The script reads `~/.claude/projects/<encoded-cwd>/*.jsonl` files, excludes the current session via `$CLAUDE_CODE_SESSION_ID`, filters to files modified within the last 120 minutes (configurable via `$SUP_SIBLING_WINDOW_MIN`), and emits a topic hint per sibling. Topic priority: latest `away_summary` content → `custom-title` → last user message.

When the block is non-empty:

- **Include the verbatim output** in the report under `**Sibling sessions:**`.
- **Read each topic hint and decide whether one matches the current invocation's context.** Strong signals: the user just `/clear`d and is asking "where were we," a sibling's topic mentions the same files/skills/stories you're about to recommend, the sibling is very recent (≤15 min) and the current session is freshly cleared.
- **When a match is plausible, elevate it.** Add an explicit `→ Looks like that work is live in `<id>` — switch windows rather than restarting here.` line. This outranks anything the Backlog scan would otherwise recommend.
- **When no match is plausible**, the block is still useful as ambient awareness ("there are 3 other windows in this project") — keep the verbatim emission, skip the elevation.

If `sibling-sessions.py` is missing or errors, silently skip the section. The skill should never block on it.

### Relay (cross-host)

Source: `relay-status` when `design/relay/STATE.md` exists. Relay is the cross-host mechanism for two CC instances on different hosts handing work back and forth via git commits (canonical design in `~/code/groot-claude-coord/design/relay/`).

- When `active: none` in `STATE.md`, render one line: `⚪ Relay parked since <date>`. Low-importance — relegate to a single line.
- When `active: <host>`, render: `🟢 Relay active on <host>` plus the cycle summary from the body if short. Higher importance — if the active host **is not** the current host, the ball is elsewhere and starting unrelated work here may step on a pending handoff; surface that explicitly.

This is the cross-host analogue of sibling sessions: same "don't start parallel work to something already in flight" goal, different transport.

## Backlog scan & pick

Run **only when the current chunk is parkable** — clean tree, or one obvious commit away from clean. If there's substantive in-flight work (mid-refactor, uncommitted changes spanning multiple files, half-applied feature), **skip this entire section**. Sitrep's Next steps already says what to resume; piling on a backlog pick is noise.

### Where to scan

Run the shared scanner — one command, one definition of "where queued work lives" (the same machinery `/next` uses, so the two skills never drift):

```bash
backlog-scan
```

It emits a grouped, counted inventory of `TODO.md` (open entries), `design/stories/ready` (outranks drafts), `design/stories/drafts`, `design/helping-hands`, pending `REVISIT.md` items, open PRs, and stale branches — surfaces with nothing are shown as `— 0`. Use its titles and counts directly. **Glance — don't deep-read;** read an individual file only if a candidate genuinely needs disambiguating.

If `backlog-scan` isn't on PATH (older host, dotfiles not yet pulled), fall back to a quick manual glance at `TODO.md`, `design/stories/ready/*.md`, `design/helping-hands/*.md`, and `gh pr list` — but the script is the intended path; surface the gap so it gets installed.

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
- If you read a story/helping-hands file to check it, surface a _one-line_ characterization — don't paste contents.
- Don't pad with detailed pros/cons. One pick, one reason. The user will ask if they want more.
- If you genuinely can't pick (everything looks equally good or equally unclear), say so and list the top 2–3 options for the user to choose from. Don't force a fake recommendation.
- **Defer to a hot sibling.** If the Sibling-sessions block already flagged an active thread whose topic overlaps your candidate pick, recommend continuing in that window instead. Don't compete with a live session.

## End-of-session check

After the sitrep output, decide whether to recommend that _this_ session be ended and a fresh one started for the next task.

**This signal is about the health of THIS conversation, not about where the next task happens to run.** Don't conflate the two. If your recommended pick lives in a different directory or a different repo, that's normal — _you_ are not the one who would run it; the user starts a new terminal/CC instance for it whenever they're ready. The end-of-session signal fires only when continuing this same conversation for the next task would be measurably worse than starting fresh.

**Default: silence.** New sessions have real cost — the user has to re-establish context, re-orient Claude, possibly re-read files. Don't suggest that cost unless the current session has a _visible, concrete problem_ that a fresh session would actually solve.

### The test

The bar is **not** "is this an OK time to stop?" (true after almost any completed task — meaningless signal). The bar is **"would continuing this conversation for the next task be measurably worse than starting fresh?"**

Recommend ending this session **only when at least one of these is observably true**:

- **Context pressure is real.** The Claude Code context indicator shows ≥50% used, OR the system has already auto-compacted, OR you (Claude) have noticed yourself re-reading files you read earlier, losing details from earlier in the conversation, or otherwise behaving like you're context-starved.
- **The conversation has drifted across multiple unrelated subtasks** _and_ the next requested work is again unrelated to anything currently in cache. (Three distinct topics, with a fourth pivot incoming, is a clear case.)
- **The user has explicitly signaled a fresh-context-friendly transition** — switching projects, switching repos, "I want to start fresh on this," etc.

### Explicit non-signals

These are **not sufficient reasons** by themselves. If these are all you have, stay silent:

- Tree is clean. (That's the prerequisite, not the reason.)
- A commit was just made or a milestone was just completed. (Normal end-of-task state — default is to wait for the next task in the same session.)
- "This feels like a natural stopping point." (Most stopping points are _fine_ to continue from. Naturalness is not a signal.)
- The session is short or just started. (Short sessions especially should not trigger this — the warm context is the asset.)
- **The recommended pick lives in a different working directory, repo, or terminal.** That's a property of the task environment, not of this session's health. The user runs the pick in its own session whenever they pick it up; this one stays useful for whatever comes next here. Stay silent unless one of the bullets above also fires.
- **The session has accomplished substantial work / covered a lot of ground.** Volume of completed work is not impairment. The trigger is observable loss of recall or coherence, NOT "feels like the session has been productive enough." A session that just shipped a slice + three drafts + a debug detour is doing exactly what a session is supposed to do — that's not a fresh-context signal. Don't conflate "done a lot" with "running out of room." Check the actual recall-loss signals; if none fire, stay silent.

### How to emit

When the bar is genuinely cleared, emit as a final Bash call so it renders in real terminal yellow. Phrase it so the reader can't mistake it for "you'll need another session for the next task" — it's specifically _end this one_:

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

## Help

When invoked as `/sup help`, print the following block verbatim:

```
sup — Personalized sitrep (Derek's flavor). Strict superset of /sitrep
with four additions: Session recap; sibling-session + relay awareness;
backlog scan + pick recommendation; new-session check. Answers "where
are we, what's next?", "what was I doing in this terminal?", and
"is something already in flight elsewhere that I should join instead?"

Usage: /sup

Sequence:
  1. Sitrep mirror       Full upstream /sitrep output (never drops sections,
                         especially Next steps). Last-commit line carries a
                         relative timestamp (Xh / 3 days ago) for staleness.
                         Includes Session recap — always emitted, bulleted
                         summary of what THIS conversation has done.
  2. Sibling + relay     Scans ~/.claude/projects/<cwd>/ for other CC
                         sessions active in the last 120 min (configurable
                         via $SUP_SIBLING_WINDOW_MIN). Topic hint per session
                         pulled from latest away_summary / custom-title /
                         last user message. Plus relay-status one-liner when
                         design/relay/STATE.md exists. Always runs.
                         A hot sibling outranks the Backlog pick.
  3. Backlog scan        Only when current chunk is parkable. Runs the shared
                         ~/bin/backlog-scan (same machinery as /next): TODO.md,
                         stories/ready, stories/drafts, helping-hands, pending
                         REVISIT, open PRs, stale branches.
  4. Pick                One specific recommendation with one-line reasoning,
                         chosen by: unblocks-downstream → removes-risk →
                         session-capacity → continuity → smaller-concrete-wins.
                         Defers to a topic-matching hot sibling.
  5. New-session check   Default silence. Fires only when continuing THIS
                         conversation would be measurably worse than starting
                         fresh: context ≥50% / auto-compacted / drift across
                         unrelated subtasks / explicit fresh-context signal.
                         Emits as ANSI-yellow Bash printf (not markdown).

Non-signals (do NOT trigger new-session by themselves):
  Clean tree, recent commit, "natural stopping point", session has been
  long-running, pick lives in a different dir, "feels productive".

Use /sitrep (upstream) for the unembellished base report.

See SKILL.md for full reference.
```

## Rules

- The sitrep portion is non-negotiable. **Always show Next steps** when work is non-trivial.
- **Always show Session recap**, even on a fresh session — render `_Fresh session — no prior activity in this window._` if there's nothing yet. The "what was I doing here" failure mode is what the recap exists to fix; making it conditional defeats that.
- The new-session line is a high-confidence signal, not a hedge. If you're not sure, omit it.
- Use the `printf` commands above for the recommendation — ANSI yellow makes it impossible to miss. Don't substitute markdown bold; it doesn't pop.
- Be _brief_ everywhere. This is a glance, not a report.
- Don't explain what a sitrep is or what /sup adds. Jump straight to the output.
