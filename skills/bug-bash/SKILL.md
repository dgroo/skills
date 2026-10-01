---
name: bug-bash
description: Work through a project's bug list autonomously, fixing bugs in priority order
argument-hint: [P0-P1 | --max N | --dry-run]
---

# Bug Bash

Autonomously work through a project's bug/issue list, fixing bugs in priority order. Reproduce each bug, fix it, test it, commit it, and move on — without waiting for human input.

## When to Use

- Clearing a backlog of known bugs
- Hardening before a release
- Focused cleanup sprint

## How to Invoke

```
/bug-bash                     # Fix all bugs, highest priority first
/bug-bash P0-P1               # Only fix P0 and P1 (or critical/high) bugs
/bug-bash --max 5             # Fix at most 5 bugs, then stop
/bug-bash --dry-run           # Triage only — report what you'd fix, don't change code
```

---

## Phase 0: Discover the Bug List

Find the project's bug/issue tracker. Check these sources in order:

1. **Local files**: Look for `bugs.md`, `BUGS.md`, `TODO.md`, `todo.md`, `ISSUES.md`, or similar in the repo root and `docs/` directory
2. **GitHub Issues**: Run `gh issue list --state open --limit 100` to check for a GitHub-based tracker
3. **Project instructions**: Read `CLAUDE.md`, `CONTRIBUTING.md`, `README.md` for pointers to where bugs are tracked
4. **Inline markers**: `grep -r "TODO\|FIXME\|HACK\|BUG\|XXX" --include="*.{py,js,ts,rb,go,rs,java,pm,pl}" -l` as a last resort

If no bug list is found, tell the user and stop.

Once found, read the entire bug list. Parse out:
- Each bug's **priority** (P0/P1/P2/P3, critical/high/medium/low, or whatever scheme the project uses)
- Each bug's **status** (open, fixed, won't-fix, etc.)
- Each bug's **description**

Filter to open bugs only. Sort by priority (highest first), then by order of appearance. If the user specified a priority range or max count, apply those filters.

---

## Phase 1: Pre-flight Check

**Work in your own worktree, never the shared checkout.** `git worktree add <path> -b bug-bash/<date> main` and do everything there. Other agents may be working the same repo; the shared checkout is touched only to merge. Never `git stash` — `refs/stash` is shared across every worktree of a repo, and a sibling's `stash pop` can cross-apply into yours. And never edit another project's repository: if a bug's fix belongs in a dependency, file it with `/request` and mark this one blocked.

Before touching any code, verify the project builds and tests pass in its current state.

1. **Identify build/test commands**: Read `Makefile`, `package.json`, `Cargo.toml`, `pyproject.toml`, `build.gradle`, etc. Look for the project's documented build and test commands (often in README, CONTRIBUTING, or CLAUDE.md).
2. **Run the build**: Execute the build command. If it fails, STOP — tell the user the baseline is broken and list the failures.
3. **Run the test suite**: Execute the test command. Record the results as the **baseline**.
   - If tests fail, note which ones. These are **pre-existing failures** — do not count them against your fixes later.
   - Record the exact test output for comparison after each fix.

If there is no build system or test suite, note this and proceed with extra caution — you'll rely on interactive testing and code review.

---

## Phase 2: Work Through Bugs

For each bug, in priority order:

### Step 1: Understand

Establish expected versus actual behaviour and the code involved. Understand the current implementation before changing it.

### Step 2: Reproduce

Before writing any fix, confirm the bug exists:
- **Write a failing test** that demonstrates the bug, OR
- **Reproduce interactively** if it's a UI/behavioral issue (use tmux for TUI apps, curl for APIs, etc.), OR
- **Read the code and confirm** the logical error if the bug is evident from inspection (e.g., wrong variable name, off-by-one)

**Proof of bite.** A test that demonstrates the bug must actually fail against the unfixed code — run it *before* the fix and keep the failure output for the commit message. A guard that was never seen to fail is decoration: several have shipped that would have passed either way. If you prove it by tampering (reverting the fix, swapping in the old file), **commit the fix first** — an agent lost all its work to `git checkout --` mid-tamper — and the tampered build must compile and run, or you've proven nothing. Also write the case that must *not* trigger: a predicate tested only on the input its author wrote is unproven.

If you cannot reproduce the bug or confirm it exists in the current code:
- It may already be fixed. Check recent commits.
- It may be environment-specific. Note this.
- Mark as "Could not reproduce" in the bug tracker and move on.

### Step 3: Fix

Implement the fix:
- **One thesis per fix.** Fix the cause, not the symptom — a fix that only adds a guard should say in its commit body why the case was genuinely missing. Don't refactor the neighbourhood unless the fix requires it; if it does, the commit says so. Size isn't the measure; whether it shrinks or holds the learning surface is.
- **Match existing patterns** for style, naming, and error handling.
- **No drive-by changes.** If you spot another bug, add it to the tracker — don't fix it inline.

### Step 4: Test

Verify the fix thoroughly:

1. **Confirm the failing test now passes** (or the interactive repro no longer reproduces)
2. **Run the full test suite**: Compare against the baseline from Phase 1. If any previously-passing test now fails, your fix introduced a regression.
   - If regression: **revert your changes**, note the conflict in the bug tracker ("Fix attempted but caused regression in X — needs more careful approach"), and move on.
3. **Add or update tests** for the fixed behavior if a test didn't already exist
4. **Drive the real thing** if the project has a recipe for it (`CLAUDE.md`'s verification recipe) — especially for UI bugs. Tests exercise the mechanism; this exercises the integration.

### Step 5: Clean Up

While the fix is fresh:
- **Update documentation** if the bug or fix affects documented behavior
- **Update the bug tracker** — mark the bug as fixed with a description of:
  - What the root cause was
  - What the fix was
  - What tests were added
  - Any decisions you made and why

### Step 6: Commit

Create a commit for this bug fix:
- Use a clear commit message referencing the bug (e.g., "Fix P2: Shift+Tab cycles scope backward in find-in-files palette")
- Only include files related to this fix
- Do NOT batch multiple bug fixes into one commit — one bug, one commit

### Step 7: Next Bug

Move to the next bug. Do not wait for human input between bugs. Keep going until:
- All bugs in scope are processed, OR
- The `--max` limit is reached, OR
- You've hit a bug that is unsafe to fix without human guidance (see Phase 3)

---

## Phase 3: Skipping Bugs

Skip a bug and move on if any of these apply:

- **Ambiguous requirements**: The bug description is unclear and multiple interpretations lead to different fixes. Log: "Skipped — ambiguous requirements. Needs clarification on [specific question]."
- **Too large**: The fix would require a major refactor or architectural change. Log: "Skipped — fix requires [description of scope]. Not suitable for a bug bash."
- **Conflicting requirements**: The fix would break another documented behavior or contradict another bug's resolution. Log: "Skipped — conflicts with [other bug/requirement]."
- **Cannot reproduce**: The bug doesn't manifest in the current code or your environment. Log: "Skipped — could not reproduce as of [commit hash]."
- **Dangerous**: The fix touches security-critical code, data migration, or deployment infrastructure in ways that need human review. Log: "Skipped — needs human review for [reason]."
- **Blocked**: The fix depends on another bug being fixed first. Log: "Skipped — blocked by [other bug]. Fix that one first."

Always log the reason in the bug tracker entry. Never silently skip.

---

## Phase 4: Session Summary

After all bugs are processed (or the limit is reached), produce a summary:

```
# Bug Bash Summary

**Date**: [date]
**Scope**: [all / P0-P1 / max 5 / etc.]
**Baseline**: [commit hash at start]

## Results

| # | Priority | Bug | Result | Commit |
|---|----------|-----|--------|--------|
| 1 | P1 | Shell injection in Git.pm | FIXED | abc1234 |
| 2 | P1 | Stale TODO.md references | FIXED | def5678 |
| 3 | P2 | Shift+Tab broken in palette | FIXED | ghi9012 |
| 4 | P2 | God object decomposition | SKIPPED | — |
| 5 | P3 | Junk files not gitignored | FIXED | jkl3456 |

**Fixed**: 4 | **Skipped**: 1 | **Regressed**: 0

## Skipped Bugs
- **P2: God object decomposition** — Too large. Fix requires architectural refactor across Editor.pm, Commands.pm, and Palette.pm. Not suitable for a bug bash.

## Not Done
- [Anything left out of a fix, deliberately or not: the second call site you didn't reach, the edge case you didn't cover, the test you couldn't make fail. An honest omissions list is worth more than the fixes — ask for it explicitly and it arrives; omit it and it never does.]

## Decisions Made
- [Any judgment calls you made during the bash, with reasoning]

## Test Suite Status
- Baseline: 927 tests, 926 passed, 1 pre-existing failure (syntax_samples.t)
- Final: 934 tests, 933 passed, 1 pre-existing failure (syntax_samples.t)
- New tests added: 7
```

Push the branch if on a feature branch. Report the summary to the user.

---

## Decision-Making Guidelines

You are working unassisted. When a decision is required:

1. **Prefer the option you can explain.** If unsure between two approaches, pick the one whose thesis fits in a sentence and doesn't grow the public surface — not simply the one with the smaller diff.
2. **Follow existing patterns.** If the codebase does X one way everywhere, do it the same way — even if you think another way is better.
3. **Don't gold-plate.** Fix the bug as described. Don't add features, extra configurability, or "while I'm here" improvements.
4. **When in doubt, skip.** It's better to skip a bug and let a human decide than to make a bad fix that introduces a regression.
5. **Log everything.** Every decision, every skip reason, every judgment call goes in the bug tracker and commit message. A human will review your work later.

---

## Important Safety Rules

- **Never force-push.** Always use regular `git push`.
- **Never `git stash`, never edit another project's checkout.** See Phase 1.
- **Never modify git config.** Don't change user.name, user.email, or any git settings.
- **One commit per bug.** Don't squash or amend across bugs.
- **Revert on regression.** If your fix breaks something, revert it — don't try to fix the fix.
- **Respect pre-commit hooks.** If a hook fails, fix the issue and create a new commit (don't `--no-verify`).
- **Don't delete test files.** Even if they seem broken or outdated.
- **Don't touch CI/CD config** unless a bug specifically calls for it.
