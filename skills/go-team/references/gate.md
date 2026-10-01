# go-team — Verifying a worker's branch (before the gate)

Part of the `/go-team` skill; read before verifying or merging any branch. The loop itself is in `SKILL.md`.

## Verifying a worker's branch (before the gate)

**First, consolidate the branch.** `python3 ~/.claude/skills/consolidate/scripts/consolidate.py --repo "$REPO" "main..$BRANCH" --apply` — a worker's twelve checkpoints land as the two or three changes they were, and `Thesis:`/`Surface:` trailers survive in the first body. Do this before the verification worktree, because it changes the branch's HEAD and the verdict must be for the SHA that will merge; your own run of the check tool in the worktree below produces it.

Do this for every worker report, before you believe any of it — in its own throwaway worktree, never the shared checkout:

```bash
set -e
V="$SCRATCH/verify-$BRANCH-$$"
git worktree add -f "$V" "$BRANCH" >/dev/null 2>&1
cd "$V"
# Read the worker's verdict file FIRST. Missing = refusal. HEAD mismatch = stale.
[ -f .verdict ] || { echo "REFUSING: no .verdict — the worker never ran the check tool"; exit 1; }
grep -q "^head=$(git rev-parse HEAD)$" .verdict || { echo "REFUSING: .verdict is for a different HEAD"; exit 1; }
# Every non-metadata line is an instrument and must be exactly 0. (An earlier
# predicate, grep '=[1-9]', also matched the when=2026-... timestamp and refused every
# green branch. The first rewrite failed OPEN -- grep -v -q exits 1 on ugrep even with
# hits -- and would have merged red branches as verified. A gate that cannot go red is
# worse than no gate: it manufactures confidence. So prove any gate check on a known-good
# AND a known-bad input before trusting it; the fail-open case is the one that never
# announces itself.)
inst=$(grep -Ev '^(head|at|when)=' .verdict)
[ -n "$inst" ] || { echo "REFUSING: .verdict has no instrument results"; exit 1; }
bad=$(printf '%s\n' "$inst" | grep -Ev '=0$')   # test the text, not grep's exit: ugrep returns 1 for -v -q even with hits
[ -z "$bad" ] || { echo "REFUSING: an instrument failed:"; echo "$bad"; exit 1; }
# Everything from here down — build, test, drive the binary interactively,
# swap in an old file version for a pre-fix/post-fix contrast, whatever
# the claim requires — happens inside $V. Never `cd` back to the primary
# checkout to do any of this "for convenience." If a step needs the primary
# checkout's path specifically (e.g. a hardcoded state-dir in a test), copy
# what's needed into $V instead of operating on the original.
<build command>
<test command>
<interactive drive, if the change touches behavior a human would notice>
cd "$REPO"
git worktree remove --force "$V" 2>/dev/null || true
```

**A guard, not just an instruction: before running any build, test, or drive command as part of verification, confirm `$PWD` is not the primary checkout's path.** If it is, stop — you're about to verify a claim by mutating shared, live files. This one bit an unattended run (see the cycle's step 3 in `SKILL.md`): verification ran directly in the shared checkout, a pre-fix/post-fix comparison left several already-merged files reverted in the working tree while `HEAD` still had the fix, and it took real time to even recognize what had happened, let alone fix it. The fix isn't "be more careful" — it's "never run verification anywhere but an isolated worktree," enforced by checking the path, not by remembering to.

## The gate

Write this to a scratch directory at the start of a session and use it for every merge. Do **not** install it into the project. Substitute the project's own lint/test/structure commands.

```bash
set -e
cd "$REPO"
BR="$(git branch --show-current)"
[ "$BR" = "main" ] || { echo "REFUSING: checkout is on '$BR', not main"; exit 1; }
SHA="$(git rev-parse HEAD)"                # FULL sha. An abbreviation widened mid-gate was read as "HEAD moved".
# A UNIQUE dir per run. A fixed one failed to delete while a previous build
# still held files in it, and `set -e` then aborted the gate in its own
# cleanup -- silently, because the failure was after the verdict.
T="$SCRATCH/gate-$SHA-$$"
git worktree add -f --detach "$T" "$SHA" >/dev/null 2>&1
cd "$T"
<structure check>                       # parser / brace balance, if applicable
<lint command> 2>&1 | tee "$SCRATCH/lint-$SHA-$$.log" | tail -2
grep -qE '^error' "$SCRATCH/lint-$SHA-$$.log" && { echo "LINT FAILED"; exit 1; }
<test command> 2>&1 | tee "$SCRATCH/test-$SHA-$$.log" | tail -3
if grep -qE '^error|test result: FAILED' "$SCRATCH/test-$SHA-$$.log"; then
  echo "TESTS FAILED"; grep -E '^error|FAILED|panicked' "$SCRATCH/test-$SHA-$$.log" | head -20; exit 1
fi
# Prose and UI copy get a reader, not just a build. If the branch adds or rewrites
# user-facing text (docs pages, help output, error messages, UI copy), spawn a fresh
# agent with NO context to read it as the target reader and answer: what is this for,
# and what would I do next? If it can't, the branch goes back. Four docs pages
# shipped as development notes before anyone read them as a user.
# Shape, not just correctness. Exit 2 = return to the worker with the printed reasons; it is not a failure of the code.
python3 ~/.claude/skills/slop/scripts/slop_diff.py --repo "$REPO" "main..$BRANCH" --require-thesis \
  || { echo "RETURN TO WORKER: shape check did not pass (see reasons above)"; exit 2; }
echo "GATES PASS on $SHA in isolation"
cd "$REPO"
[ "$(git rev-parse HEAD)" = "$SHA" ] || { echo "REFUSING: HEAD moved during gating"; exit 1; }
git push -q origin main                 # omit if autonomy policy is merge-only; the pre-push gate refuses a main that isn't consolidated
rm -f "$(git rev-parse --git-common-dir)/leases/$BRANCH"   # release the lease BY NAME — you know which branch you merged
echo "PUSHED $(git rev-parse HEAD)"
git worktree remove --force "$T" 2>/dev/null || true   # last, and never fatal
```

Why each guard exists, all of them from real incidents:

- **Branch guard** — agents took the shared checkout off main *eight times* in one session, despite an explicit instruction in every dispatch.
- **A second platform checks the same SHA** — if the recipe has a Linux VM, a remote runner, or any second builder, it builds *the merge result*, the exact `$SHA` above: publish it as a throwaway ref (`git push <runner-remote> $SHA:refs/gate/$SHA-$$`, deleted after) or sync the gate worktree — never the branch tip. One fleet's Linux half synced the branch tip while the macOS half built the merge result; an old docs-only branch failed on two tests a later commit had already fixed. The symmetric case is worse: a branch green at its own tip while the merge result is not.
- **Isolated worktree at a specific SHA** — a gate that ran `git add -A` in the shared checkout nearly committed a stranger's half-finished refactor. It was caught by luck.
- **Unique temp dir, cleanup last and non-fatal** — see the comment.
- **`grep` for `^error` *and* test failures** — a lint that fails and a suite that fails do not report the same way, and one grep misses one of them.
- **HEAD-unchanged check** — between gating and pushing, another agent can move it.
- **Verification worktree, separate from the gate's own** — a pre-fix/post-fix comparison run directly in the shared checkout reverted several already-merged files' working-tree content back to their pre-fix state while `HEAD` still had the fix, and it was first misdiagnosed as a second agent colliding on the repo before the real cause (verification, not merging, done outside isolation) was found.
- **Verdict file, not report** — see the cycle's step 3 in `SKILL.md`. The gate is the first complete check.
- **Shape check** — the gate verified correctness and never shape, so a 600-line change fixing a 3-line bug passed, a function duplicating an existing one passed, six theses in one commit passed. `slop_diff.py` returns a branch to its worker when a fix deletes nothing and names no `Cause:`, when public surface grows with no `Surface:` line saying why, when there is no `Thesis:` trailer, or when a new function reinvents an existing one. Returned is not failed: the worker answers the question and resubmits. **Resubmitting by amending is history surgery: before asking a worker to amend a commit, run `git branch --contains <sha>`.** If another branch is based on it, either rebase that dependent in the same breath or fix forward with a new commit instead. One amended trailer reached main while a dependent branch kept the orphaned original — not an ancestor of main, so the shape check flagged it on every attempt and merging main could never clear it; the repair rebase then replayed fourteen absorbed commits before the worker aborted and cherry-picked.

**The instruction is advisory; the guard is the control.** This is the most-repeated lesson in the whole method. Agents were told in plain language, in every single dispatch, not to touch the shared checkout — and did it eight times anyway. What contained it every time was the branch guard refusing to run. When something must not happen, build the thing that refuses.

### Identifiers must identify

A fixed log path let a previous run's complete log be read as the current run's; a `pgrep` on a process *name* matched someone else's build; a TODO number allocated from "main's highest" collided four times in a day; an abbreviated SHA widened from 7 to 8 characters mid-gate and was reported as "HEAD moved". The shape is always the same — two runs, one name. Anything findable later carries a token unique to the run that created it: `$SHA-$$` in every log and temp path (as above), a PID not a process name, a full SHA never `--short`. Where the identifier is allocated from shared state — tracker entry numbers — allocate at the serialisation point: workers file placeholders (`#TBD-<branch>`), the foreman substitutes real numbers at merge. And a reference that *silently changes referent* is worse than a broken one: renumbering one entry required repointing ten citations across six files, every one of which still resolved — to an unrelated finding. Breakage announces itself; redirection doesn't. When you move or rename anything other things name, the job isn't done when the thing moves — sweep, and verify the sweep by re-running it with an asserted count of zero, not by reading output.

---

