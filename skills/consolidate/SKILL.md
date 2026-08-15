---
name: consolidate
description: Bring every lane in a project to one baseline — land whatever is outstanding, then pull each clean worktree forward to the remote default branch, and prove it with `lane --state`. Use when asked to "consolidate the lanes", "get everyone to a baseline", "are all lanes on the same code — make it so", "regroup before we fan back out", "/consolidate". Companion to /lanes (which decides the domains) and /land (which lands one branch); this is the whole-project sweep across all of them.
argument-hint: "[? = report only, change nothing]"
---

# /consolidate — get every lane onto one commit

`lane --state` answers _"is everyone on the same code?"_. This answers _"make them so."_

**The distinction that makes this buildable.** `session-teams/DESIGN.md` requirement 3 rules out teardown-after-collapse ceremonies, and rightly — but that objection is about protocols other sessions must participate in. **This asks nothing of any other session.** Their work is in git whether they are awake or asleep, and a clean worktree can be pulled forward without their involvement. Consolidation is something the landing lane does *to* the checkouts, not a ritual the lanes perform.

## Modifier

- `/consolidate ?` — run the read half only. Report what would land, what would be pulled forward, and what would be skipped. Change nothing.
- `/consolidate` — do it.

## Sequence

### 1. Read the board

```bash
lane --state
```

Per lane: ahead of the remote default branch, behind it, uncommitted files. Stop here if it already says **all lanes at baseline** — say so and stop; there is nothing to do and pretending otherwise wastes a turn.

### 2. Land what is outstanding, one lane at a time

For each lane with `AHEAD > 0`, run the `/land` checks rather than trusting the count:

- Measure against `origin/main`, **never local `main`** — `git fetch` moves the remote ref and leaves the local one where it was.
- `git merge-base --is-ancestor origin/main <branch>` for fast-forwardability; `git merge-tree --write-tree` when you need to know a merge is clean without performing it.
- `git grep -nE '^(<{7}|>{7}) ' <branch> -- .` across the **whole tree**, not the file someone named.
- Lint and the suite in a scratch worktree at the tip, with the primary's `node_modules` symlinked in if the tree has none.
- Re-fetch immediately before the push — races happen in the gap between verifying and pushing, not during either.

**Never chain a push behind a merge that can fail.** Write it as separate steps and check each. A `git merge && npm test && git push` one-liner runs the push when the merge conflicts and the tests pass on the pre-merge tree — which is how conflict markers reach `origin`. This has bitten twice in one day on warball2, in two different sessions, including the one writing this down.

Conflicts are normal here and usually in append-at-top files (`DIARY.md`, `NEXT.md`) where two lanes each added an entry. **Keep both sides** unless the content genuinely contradicts; a diary is not a merge target, it is two facts.

### 3. Pull each worktree forward

For each lane, in the worktree's own directory:

```bash
git merge --ff-only origin/main
```

**Only when both are true: `AHEAD == 0` and the tree is clean.** Otherwise skip it and say why — a lane with unlanded commits or uncommitted files is holding work that is not yours to discard, and the whole value of this pass is that it never loses anything.

Exclude `design/` from the dirty check where the project runs the design-sync watcher: that tree is committed within seconds of every save, so counting it blocks a consolidation on ambient churn. Report it separately rather than dropping it silently.

Pulling a clean worktree forward is safe even when a session is live in it — there is no local work to lose — but **name every checkout that moved**, because a session that had files open deserves to know its ground shifted.

### 4. Prove it

```bash
lane --state
```

Ending on the readout rather than on a claim is the point. If it does not say **all lanes at baseline**, the remaining rows are the report — name them and why each was skipped.

## What this deliberately does not do

- **It does not ask lanes to stop, park, or confirm.** Any barrier built out of messages reaches only the sessions that are awake, which is the population that least needs reaching.
- **It does not force anything.** A dirty or ahead worktree is skipped and reported. No `reset`, no `checkout --force`, no discarding.
- **It does not harvest.** Writing down what a lane learned is `/wrapup`'s job, per lane, and a consolidation that also tried to journal four sessions' thinking would do both badly. If lanes are wrapping because they are out of context, `/wrapup` each of them **first** — this pass moves commits, not knowledge.
- **It does not re-carve the roster or reorder the backlog.** `/lanes` and `/pm` are their own passes on their own cadence.

## Related

- `lane --state` — the readout this acts on; `--json` for machines, exit 1 when anything differs.
- `/land` — the per-branch verification this reuses in step 2.
- `/lanes` · `/pm` — the re-baseline passes that pair with a consolidation but are not part of it.
- `groot-claude-coord` `design/stories/consolidate-and-fan-out.md` — why this is a sweep rather than a ceremony.
