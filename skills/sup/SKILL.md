---
name: sup
description: Personalized situation report — mirrors /sitrep's full output, actively scans for queued work and ranks the top candidates (#1 go-able, non-blocking — no AskUserQuestion), then issues a high-confidence new-session recommendation in bold yellow when warranted. Also routes a stated intent to the right workspace (proceed here / join a live session / provision an isolated worktree) so parallel threads don't collide; the `wt` modifier forces the worktree placement (act-unless-overkill). Use when resuming a session, asking "where were we?", when the chunk of work feels finished, or when starting a new thread with "/sup <what I want to do>" (or "/sup wt <intent>" when you already know it wants isolation).
allowed-tools: Read, Glob, Grep, Bash, Agent, TaskList
---

# Sup — Situation Report (Derek's flavor)

`/sup` is a **strict superset of `/sitrep`** with these additions: (1) a **Session recap** that answers "wait, what the hell was I doing in this terminal window?" for cold returns, (2) actively scanning the repo for queued work and ranking the top candidates (#1 go-able, non-blocking), (3) evaluating whether to recommend a fresh Claude session, and (4) **intent routing** — when invoked with a stated intent (`/sup <what I want to do>`), placing that new thread where it won't collide with work already in flight.

`/sup` answers three questions: "where are we with this project, what's next?", "what was happening in this window when I walked away?", and — when you hand it an intent — "where should this new thread actually run so it doesn't trip over my other sessions?" The Last-commit line carries a relative timestamp so the reader can gauge staleness at a glance — the longer it's been, the more the Session recap is doing the work.

`/sitrep` itself is upstream-tracked (joewalnes/skills) and intentionally left untouched. Use `/sup` instead.

## Sequence

1. **Produce the full sitrep output** (see "Sitrep mirror" below). Never drop sections that sitrep would include — especially **Next steps**.
2. **Surface sibling sessions and relay state** (see "Sibling sessions & relay" below). Always runs — independent of whether current work is parkable. If a hot sibling matches what the user just typed `/sup` to find, it outranks anything in the backlog scan.
3. **Branch on whether an intent was supplied:**
   - **Intent supplied** (`/sup <what I want to do>`) → **route it** (see "Intent routing" below) instead of scanning the backlog. The user already declared the work; the job is to place it so it doesn't collide — proceed here / join a live thread / provision an isolated worktree. Skip the backlog scan.
     - **Strip a leading `and`.** Derek habitually writes `/sup and <intent>` — the `and` is a grammatical lead-in meaning "do the don't-collide check *and* here's what I want to work on," not part of the intent. Drop a single leading `and` (and surrounding whitespace) before routing, so `/sup and roci --newc` routes the intent `roci --newc`. It's a politeness particle, not a separate mode — the collision check already runs in this branch regardless. (A bare `/sup` with no intent stays the situation-report; `and` only ever appears alongside a real intent.)
   - **No intent** ("where am I / what's next") → **scan the backlog and rank the top candidates** (see "Backlog scan & pick" below). Run only when current work is parkable; otherwise skip. If a hot sibling already covers the top candidate's topic, defer to the sibling instead of recommending fresh work here.
4. **Evaluate the new-session recommendation** (see "New-session check" below). Most of the time, emit nothing. Only fire when the bar is genuinely cleared. (Runs in both branches.)

## Modifier — `!` (report, then act)

`/sup` participates in the decisiveness-dial convention shared with `/wrapup` and `/next`: **`?` = assess, minimize mutation · `!` = act decisively, minimize interruption.** `/sup`'s default is _already_ a read-only report, so plain `?` would be a no-op — it isn't implemented here. Only `!` adds behavior:

- **`/sup !`** — produce the full report exactly as below (sequence steps 1–4, including the Pick), **then act on it**: don't stop at recommending the Pick — proceed to start that work, bugs first, with the same autonomy as `/next !`. In effect `/sup !` = `/sup` followed by `/next !` on the resulting top candidate.
- **Defer to the same guards `/sup` already honors.** If a hot sibling session or an active relay turn outranks the Pick (steps 2–3), surface that and **do not** auto-start — the whole point of those guards is "don't start parallel work to something already in flight." `!` raises decisiveness; it does not bulldoze the don't-collide checks.
- **The new-session check (step 4) still runs first.** If `/sup` would recommend bouncing to a fresh session, `!` honors that — it surfaces the recommendation rather than starting work in an impaired session.
- **`/sup ! <intent>`** — route the intent (see "Intent routing"), then act on the placement without waiting for a `go`: if placement is "provision a new worktree," create it and start the work there; if "proceed here," just start. Still defers to placement "join an existing home" — never auto-starts a parallel thread over a live sibling.

Plain `/sup` is unchanged: report and recommend, never auto-start.

## Modifier — `wt` (force a worktree)

`/sup wt <intent>` is a **placement override**, the inverse of the default router's "_might_ suggest a worktree." Here the user has pre-decided that this thread wants isolation; the skill's job flips from "should this be isolated?" to "isolate it — unless you, the agent, think that's overkill." Requires an intent (it's an intent-routing variant); bare `/sup wt` with no intent is meaningless — treat it as plain `/sup`.

- **Act, don't ask.** Route the intent as usual, but treat **a worktree in the owning repo as the presumed placement**, and act on it with the same autonomy as `!`: provision the worktree and start the work without waiting for `go`. `wt` therefore _subsumes_ `!` — no need to type both (`/sup ! wt` is harmless but redundant).
- **Push back when it's genuinely overkill.** The user explicitly delegates this veto. Don't provision — surface the objection and the cheaper placement, and let a bare `go` override — when the intent is **purely additive** (a new doc/file with nothing to collide with) or when **no parallel work touches the target files** (isolation buys nothing). A worktree's whole cost is setup + a later merge; if there's nothing to be isolated _from_, say so.
- **Hard carve-out — not a judgment call.** If the owning repo is the **dotfiles bare repo** or **`~/.claude`** (the `$HOME`-spine carve-out), a worktree is _impossible_, not merely unwise — there's no per-thread tree to branch into. Don't provision; fall back to single-writer-in-place and say why. This overrides the "act" default.
- **Same don't-collide guards.** `wt` defers to placement "join an existing home" exactly as `!` does — if a live sibling or topic-matching worktree already owns the intent, surface that and switch rather than provisioning a _parallel_ worktree over in-flight work. And it provisions in the **owning repo** (federated-aware), not the hub cwd you typed it in.

Provision via `git worktree add ~/code/worktrees/<repo>/<short-slug> -b <branch>` (the `~/.claude/CLAUDE.md` location convention) or `superpowers:using-git-worktrees`, then launch/cd a session there.

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

**Picks:** The top 2–3 ranked candidates, one line each, with **#1 rendered as the `Recommended next` block** (see Rules) so a bare `go` acts on it; #2–3 let you see the ranking and name another without running `/next`. Non-blocking — no AskUserQuestion (that's `/next`). Only when current chunk is parkable. In the intent-routing branch this collapses to a single block — the placement decision _is_ the Recommended next.
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
- **Same-checkout siblings — the real risk is data loss, not duplicate work.** A sibling sharing *this checkout* (not a worktree) can't be footprint-orthogonal: they share one index, working tree, and branch, regardless of topic. For just-me repos the *cosmetic* collisions — interleaved commits, one session sweeping another's staged edits into its commit, messy merge history — are **fine and not worth flagging or blocking on**. What *is* worth flagging is the narrow set that can actually lose work or wedge the tree: when the sibling block is non-empty and a sibling shares this checkout, **never force-push**, and before any destructive or history-rewriting git op (`reset --hard`, branch switch / `checkout`, `rebase`, `stash`, `clean`) confirm `git status` shows only your intended changes — those ops can silently clobber a sibling's uncommitted or unpushed work. A rejected (non-fast-forward) push is resolved by `fetch` + **merge** (never force, never rebase over commits a sibling may be holding), after verifying the tree is clean and the changed-file sets are disjoint. This is the only sibling concern that rises to "stop and check"; everything else is ambient awareness.

If `sibling-sessions.py` is missing or errors, silently skip the section. The skill should never block on it.

### Relay (cross-host)

Source: `relay-status` when `design/relay/STATE.md` exists. Relay is the cross-host mechanism for two CC instances on different hosts handing work back and forth via git commits (canonical design in `~/code/groot-claude-coord/design/relay/`).

- When `active: none` in `STATE.md`, render one line: `⚪ Relay parked since <date>`. Low-importance — relegate to a single line.
- When `active: <host>`, render: `🟢 Relay active on <host>` plus the cycle summary from the body if short. Higher importance — if the active host **is not** the current host, the ball is elsewhere and starting unrelated work here may step on a pending handoff; surface that explicitly.

This is the cross-host analogue of sibling sessions: same "don't start parallel work to something already in flight" goal, different transport.

## Intent routing

Triggered when `/sup` is invoked **with a stated intent** — `/sup <what I want to do here>` (a leading `and` is stripped first; see Sequence step 3). This is the front door for "I just had an idea and want to start working on it _now_," which is exactly when collisions happen: the user opens a fresh session in a hub repo and starts a thread that trips over another live session in the same files. The job here is **not** to recommend _what_ to do (the user said) — it's to **place** the work so it doesn't collide. It reuses the sibling-session + worktree data already gathered in steps 1–2; it adds no new scanning to the bare-`/sup` hot path.

The underlying model: work has a **divergent** phase (thinking-by-working — usually additive, low-collision) and a **convergent** phase (landing the conclusion into shared files — high-collision, serial). Isolation makes the divergent phase safe to wander; landing becomes a deliberate merge.

Classify the intent into one of three placements:

1. **Proceed here.** No live sibling overlaps the intent, and the intent is additive (a new doc/file) or touches only files no other session is in. Just start — this is the common case. Don't manufacture isolation that isn't needed.

2. **Join an existing home.** A sibling session (from `sibling-sessions.py`) or a topic-matching worktree/branch (`git worktree list`) already owns this intent. Recommend switching to that window/worktree rather than starting a parallel thread. This is the collision `/sup` exists to prevent — surface it loudly; it outranks "proceed here."

3. **Provision a new worktree.** The intent will touch _existing shared files_ (not purely additive) **and** another session is live — so wandering into those files here would collide. Recommend an isolated branch and, on confirmation, provision it: `superpowers:using-git-worktrees` is the canonical path, or directly `git worktree add ~/code/worktrees/<repo>/<short-slug> -b <branch>` (the location convention from `~/.claude/CLAUDE.md`). Then launch/cd a session there.

### Repo ownership (the federated case)

The intent's owning repo may not be the cwd. A skills-behavior change belongs in `dgroo/skills`; a global-config change in `~/.claude` (`dot-claude`); a shell/script change in the dotfiles bare repo; a self-contained feature in its own project repo (the easy case — same-repo worktree, e.g. Changer). **Name the owning repo and provision the worktree _there_**, not in the hub repo you happen to be sitting in. `rcs` and other hubs are the _cockpit_ you launch from, not necessarily where the work lands. When the owning repo is ambiguous, ask before provisioning.

### The `$HOME`-spine carve-out

Two homes **can't** be meaningfully worktree-isolated:

- The **dotfiles bare repo** (work-tree is `$HOME`) — there's no per-thread tree to branch into.
- **`~/.claude`** — it's a normal repo, but the _checked-out_ copy is the live config the running agent reads; an edit in a worktree wouldn't take effect.

For an intent landing in either, the placement opinion is **"you're the single writer for this config right now"** — check the sibling block and proceed only if no other session is editing it — _not_ "here's a worktree." The design/thinking for such a change can still live in an isolated doc; only the final config write serializes.

### How to close

End with the structured **Recommended next** block (see Rules) so a bare `go`/`yes` acts on the placement — provision-and-start for (3), start-in-place for (1), or "switch to `<window>`" for (2). With `!` (`/sup ! <intent>`), skip the confirmation and act, honoring the same guards.

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

Add these lines to the sitrep report, right after Next steps:

- **Backlog:** Compact inventory. Example: `TODO.md (5 open), stories/ready (3), helping-hands (2), no open PRs, 1 stale branch (refactor-auth).` Skip surfaces with zero items. **Exclude the `HUMAN-REVIEW (open)` count from this line** — it's not pickable work.
- **Picks:** The top 2–3 candidates as a compact ranked list — same ranking the [picking criteria](#picking-criteria-tiebreakers-in-order) define (the ranking `/next` also uses), each one line with its leverage/dependency reason. Render **#1 as the `Recommended next` block** (see Rules) so a bare `go` acts on it; #2–3 are listed so you can see the ranking and name another without having to run `/next` afterward. **Non-blocking** — do _not_ open an AskUserQuestion here (that interactive chooser is `/next`'s job; `/sup` stays a glance). Example: `1. stories/ready/payment-retry.md — unblocks 2 downstream items (Recommended next — reply go) · 2. helping-hands/rotate-keys.md — gates the deploy story · 3. TODO: prune done-log — small, self-contained.`
- **Human-review:** Only when `backlog-scan`'s `HUMAN-REVIEW (open)` count is >0 _and_ something survives the confidence filter (see Rules). Render as a **gentle gate**, never do-now pressure and never as the Pick — e.g. `👀 N item(s) waiting for your eyes (non-blocking) — want the list, or skip?`. Omit entirely when 0 or when nothing survives.

If nothing's queued anywhere, render: `**Backlog:** Nothing obvious queued — what would you like to work on?` and skip the Picks list.

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
- **HUMAN-REVIEW items are never Pick candidates, and get a confidence filter first.** `backlog-scan`'s `HUMAN-REVIEW (open)` surface is _Derek's to eyeball, not Claude's to do_ — never recommend one as the Pick or fold it into the Backlog line. Before rendering the **Human-review** gate, run the confidence pass from `design/HUMAN-REVIEW.md` (rule 2): for each open item, decide whether it still needs a human. **Plain `/sup` filters from display only** (read-only) — show only survivors, and if any were filtered, you may note `(N look already-resolved — say "prune" to clean them up)`. **Only with `!` or on explicit confirmation** perform the earned auto-cleanup _write_ (rule 1: move stale items to `## Reviewed` with a `**Reviewed:** … — auto: <reason>` line). Items older than ~3 weeks: present as `still worth a look? [keep/drop]` rather than a bare re-list.

## End-of-session check

After the sitrep output, decide whether to recommend that _this_ session be ended and a fresh one started for the next task.

**This signal is about the health of THIS conversation, not about where the next task happens to run.** Don't conflate the two. If your recommended pick lives in a different directory or a different repo, that's normal — _you_ are not the one who would run it; the user starts a new terminal/CC instance for it whenever they're ready. The end-of-session signal fires only when continuing this same conversation for the next task would be measurably worse than starting fresh.

**Default: silence.** New sessions have real cost — the user has to re-establish context, re-orient Claude, possibly re-read files. Don't suggest that cost unless the current session has a _visible, concrete problem_ that a fresh session would actually solve.

### The test

The bar is **not** "is this an OK time to stop?" (true after almost any completed task — meaningless signal). The bar is **"would continuing this conversation for the next task be measurably worse than starting fresh?"**

Recommend ending this session **only when at least one of these is observably true**:

- **Context is verifiably low — read the real number, don't guess.** The statusline writes the percent of context _remaining_ to `~/.claude/state/context-remaining` on every render (the same value `~/.claude/hooks/context-low-check.py` trusts). Read it: `cat ~/.claude/state/context-remaining 2>/dev/null`. This is a turn-local observable — the **authoritative** one — so it beats any hunch. Fire **only when it's genuinely low (under ~30% remaining)**. A clean tree at 85% remaining is _not_ a reason — suggesting a fresh session there is the exact false-positive this gate exists to prevent. If the file is missing or unreadable, fall back to the weaker turn-local observables: a `<context-pressure>` reminder that fired **this turn** (an earlier-turn one is stale), the system having auto-compacted this session, or you actually catching yourself re-reading files / having lost earlier detail. Never infer fullness from how much work you've done, how many chunks the session covered, or how long it feels — those are explicit non-signals below.
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
# Good: "22% context remaining, next slice is unrelated."
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
with five additions: Session recap; sibling-session + relay awareness;
backlog scan + pick recommendation; new-session check; intent routing.
Answers "where are we, what's next?", "what was I doing in this terminal?",
"is something already in flight elsewhere that I should join instead?",
and — given an intent — "where should this new thread run so it doesn't
collide?"

Usage: /sup [! | wt] [<intent>]

Argument:
  <intent>  A description of the thread you're about to start. Switches
            step 3 from backlog-scan to intent routing: classify as
            proceed-here / join-existing-session / provision-new-worktree
            (in the OWNING repo, federated-aware), then close with a
            one-word-actionable Recommended-next block. dotfiles + ~/.claude
            can't be worktree-isolated — there it's single-writer-in-place.
            A leading "and" is stripped, so "/sup and <intent>" == "/sup
            <intent>" (the "and" is just a grammatical lead-in).

Modifiers:
  !    Report as usual, THEN act on the Pick / intent placement (bugs
       first), same autonomy as /next !. Defers to hot-sibling / relay /
       new-session guards — won't auto-start work already in flight
       elsewhere. Plain ? is a no-op here (/sup is already read-only), so
       it isn't implemented.
  wt   Placement override (needs an intent): presume a worktree in the
       OWNING repo and act on it (provision + start, subsumes !) — the
       inverse of the router's "might suggest a worktree." Pushes back
       instead when it's overkill (purely additive / nothing to isolate
       from); falls back to single-writer-in-place for dotfiles + ~/.claude
       (no tree to branch). Honors the same join-existing guard.

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
  3. Branch on intent:
     • no intent  →    Backlog scan (parkable only). Runs the shared
                         ~/bin/backlog-scan (same machinery as /next): TODO.md,
                         stories/ready, stories/drafts, helping-hands, pending
                         REVISIT, open PRs, stale branches.
     • <intent>   →    Intent routing. Classify proceed-here /
                         join-existing / provision-worktree (owning repo,
                         federated-aware; dotfiles + ~/.claude are
                         single-writer-in-place). Skips backlog.
  4. Picks / placement   Top 2-3 ranked candidates (non-blocking list, no
                         AskUserQuestion — that's /next); #1 is a Recommended-
                         next block a bare `go` executes. Ranked by: unblocks-
                         downstream → removes-risk → session-capacity →
                         continuity → smaller-concrete-wins. Defers to a
                         topic-matching hot sibling. Intent branch collapses
                         to a single placement block.
  5. New-session check   Default silence. Fires only when continuing THIS
                         conversation would be measurably worse than starting
                         fresh. Authoritative signal: the real number in
                         ~/.claude/state/context-remaining (fire under ~30%
                         remaining). Fallbacks: auto-compacted / drift across
                         unrelated subtasks / explicit fresh-context signal.
                         Emits as ANSI-yellow Bash printf (not markdown).

Non-signals (do NOT trigger new-session by themselves):
  Clean tree, recent commit, "natural stopping point", session has been
  long-running, pick lives in a different dir, "feels productive".

Use /sitrep (upstream) for the unembellished base report.

See SKILL.md for full reference.
```

## Rules

- **Close with a one-word-actionable recommendation.** Whether the recommendation is the backlog **Pick** (no-intent flow) or an **Intent routing** placement, render it as a structured **Recommended next** line a bare `go` / `yes` executes without re-typing — e.g. `**Recommended next:** start `stories/ready/payment-retry.md` — reply \`go\` to begin, or name another.` or `**Recommended next:** provision a worktree in `dgroo/skills` for this — reply \`go\`, or \`here\` to work in place.` This collapses the old two-turn ceremony (`/sup` → "ok, pick up what's next") into one: a bare affirmative is equivalent to having run `/sup !` on that recommendation, and honors the same don't-collide guards. (Cold-resume legibility: the recommendation should be executable, not just prose.)
- The sitrep portion is non-negotiable. **Always show Next steps** when work is non-trivial.
- **Always show Session recap**, even on a fresh session — render `_Fresh session — no prior activity in this window._` if there's nothing yet. The "what was I doing here" failure mode is what the recap exists to fix; making it conditional defeats that.
- The new-session line is a high-confidence signal, not a hedge. If you're not sure, omit it.
- Use the `printf` commands above for the recommendation — ANSI yellow makes it impossible to miss. Don't substitute markdown bold; it doesn't pop.
- Be _brief_ everywhere. This is a glance, not a report.
- Don't explain what a sitrep is or what /sup adds. Jump straight to the output.
