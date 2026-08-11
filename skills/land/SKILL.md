---
name: land
description: Verify a feature branch and fast-forward it onto main, re-checking everything that has changed since this session last looked. For solo-project FF-to-main landing — no PR, no deploy. Use when asked to "land it", "land <branch>", "merge this to main", "is it safe to merge", "/land". Distinct from gstack's /ship and /land-and-deploy, which are PR-and-deploy shaped.
argument-hint: "[branch] [? = verify only]"
---

# /land — verify, then fast-forward

> "Land it — but check things haven't moved unexpectedly."

The failure this skill exists to prevent: **you verified a branch, then landed it, and main moved in between.** Verification has a timestamp; landing happens later. On a busy repo with parallel sessions that gap is where the bug gets in — and the gap is invisible unless something goes looking for it.

Everything else here is ordinary git. The re-check is the point.

## When to use vs. skip

Use for: landing a feature branch onto main in a solo project — the fast-forward-and-push flow, no PR, no deploy. Especially when other sessions or worktrees are active in the same repo.

Skip if: the project uses PRs and CI (that's gstack's `/ship` → `/land-and-deploy`), or you want a read-only survey of what's queued to land (`/landing-report`).

## Modifier

Follows the shared decisiveness dial:

| Form | Behavior |
| --- | --- |
| `/land ?` | **Verify only.** Run phases 1–4, report the verdict, land nothing. |
| `/land` | Verify, then land on a clean verdict. Stop and report on any finding. |

## Sequence

### 1. Re-check — has anything moved?

Before anything else, establish what changed since the last look. **Never trust a verification from earlier in the session.**

```bash
git fetch origin --prune          # sandbox-off; a sandboxed fetch fails like an outage
git log --oneline -1                                  # main now
git log --oneline -1 <branch>                         # branch now
git rev-list --left-right --count main...<branch>     # divergence
git status --short                                    # must be clean
```

Compare both tips against what was verified before. If either moved, **every prior conclusion is void** — re-run from here, don't patch up the old one.

Then look at what main gained, and whether it touches the same files:

```bash
git log --oneline <last-verified>..main
git diff --name-only <last-verified>..main
comm -12 <(git diff --name-only <last-verified>..main | sort) \
         <(git diff --name-only main...<branch> | sort)
```

**File overlap is the signal that matters.** Two branches editing one file can merge textually clean and still be semantically wrong — that's what phase 3 is for.

### 2. Conflict check — without touching anything

```bash
git merge-tree --write-tree main <branch>
```

Prints the merged tree's OID on success, fails on conflict. It writes no refs, moves no HEAD, and touches no worktree — so it is safe to run against a branch a live session is sitting on.

Keep the tree OID. Phase 3 needs it.

### 3. Verify the *result*, not the branch

The load-bearing step, and the one nothing else does. A branch's own green test run proves the branch works — not that the branch works **on top of current main**. Materialise the merged tree and test that:

```bash
D=$SCRATCH/landtrial; rm -rf $D; mkdir -p $D
git archive <tree-oid> | tar -x -C $D
ln -sfn "$PWD/node_modules" $D/node_modules    # or the project's dep equivalent
cd $D && <test command> && <typecheck command>
```

This gives the post-landing answer *before* landing, with no branch moved and no live worktree disturbed. Report the number — and compare it to what the branch reported. **A mismatch is information**: it usually means main gained tests the branch never saw.

### 4. Assert survivals

Tests do not notice a deleted paragraph. Name the specific things that must survive the merge and check each in the materialised tree — a deliberate ordering in a backlog file, a link repair, a config line, a comment that carries a decision. Anything this session changed in a file the branch also touches goes on the list.

### 5. Land — fast-forward, cherry-pick, or stop

| Situation | Move |
| --- | --- |
| Branch is strictly ahead of main | `git merge --ff-only <branch>` |
| Main has moved, branch not checked out anywhere | `git cherry-pick <base>^..<tip>` |
| Main has moved, branch checked out in a live worktree | **Stop and ask** — a rebase is the tidy fix and needs per-instance confirmation |

**Never rebase without asking.** `git rebase` is on the destructive list; cherry-pick reaches the same linear main without it and without touching a worktree someone is working in. Prefer cherry-pick over asking for a rebase when both would work.

A cherry-picked commit lands under a **new SHA**. Say so — the branch's copy is superseded, not lost, and whoever owns it must not push the old ref.

### 6. Verify on main, then push

Re-run tests and typecheck **on main after landing**, not only on the materialised tree. Then push. If the project has a running dev server and the landing touched server code, restart it and confirm the change is actually served rather than merely committed.

### 7. Tell whoever was blocked

Landing usually unblocks someone. Name what landed, the new SHA, the verified numbers, and anything they should not do (push a superseded branch, tune against a number that just moved).

## Rules

- **A verification has a timestamp.** Re-check before landing, every time, even when it was minutes ago.
- **Verify the merged tree, not the branch.** The branch's green run answers a question nobody asked.
- **`merge-tree` over checkout.** Never move a branch a live session is sitting on to find out whether it merges.
- **Cherry-pick beats asking for a rebase**, when both reach a linear main.
- **A patch-id `+` from `git cherry` after a cherry-pick is an artifact, not a loss.** Confirm by content — compare the files — before raising an alarm.
- **Report the test count, not "green".** A count that changed since the branch reported it is a finding.

## Companions

- **gstack `/ship` → `/land-and-deploy`** — the PR-and-deploy flow (creates a PR, merges it, waits on CI, canary-checks production). Different shape entirely; this skill is the no-PR fast-forward one. Note that `/land-and-deploy` also claims the phrase "land it" as a trigger, so type `/land` explicitly when you mean this one.
- **`/landing-report`** — read-only view of what's queued to land.
- **`/code-review`** — for reviewing the diff itself; `/land` checks that it *merges and passes*, not that it's *good*.

## Help

When invoked as `/land help`, print the following block verbatim:

```
land — Verify a feature branch and fast-forward it onto main, re-checking
everything that changed since this session last looked.

Usage: /land [branch] [?]

Arguments:
  (none)            Infer the branch from context (the one just discussed,
                    or the only feature branch ahead of main).
  <branch>          The branch to land.
  help              Show this message.

Modifiers:
  ?                 Verify only — run the checks, report the verdict, land
                    nothing.

Sequence:
  1. Re-check       Have main or the branch moved since last verified?
                    Any prior verification is void if so.
  2. Conflicts      git merge-tree — no refs moved, no worktree touched.
  3. Verify result  Materialise the merged tree into scratch and test THAT,
                    not the branch. The branch's own green run answers a
                    different question.
  4. Survivals      Assert the specific things that must survive the merge.
  5. Land           ff-only, or cherry-pick when main moved. Never rebase
                    without per-instance confirmation.
  6. Verify + push  Re-run on main. Restart the dev server if it serves
                    changed code.
  7. Notify         Tell whoever was blocked; name the new SHA.

Not this skill:
  /ship, /land-and-deploy   PR-and-deploy flow (gstack).
  /landing-report           Read-only queue view.

See SKILL.md for full reference.
```
