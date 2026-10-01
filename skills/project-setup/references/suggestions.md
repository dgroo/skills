# project-setup — the thirteen suggestions in full

Part of the `/project-setup` skill; read the accepted ones when implementing. The process is in `SKILL.md`.


Work through these in whatever order makes sense for the project. Skip any that are already in place.

### 1. Bug Tracker / Todo List

**Pitch:** A single place to track bugs, tasks, and feature requests so nothing falls through the cracks. AI agents can read and update it autonomously.

**Implementation:**
- If the project already uses GitHub Issues, Linear, Jira, or similar — use that. Note the convention in `CLAUDE.md`.
- Otherwise, create a `TODO.md` in the repo root with this format:

```markdown
# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

- [ ] **P2** (bug) Sidebar flickers on window resize
  Fix: Debounce the resize handler in `src/layout.ts`

- [ ] **P1** (feature) Add keyboard shortcuts for navigation
  See discussion in #42

## Done

- [x] **P1** (bug) Login fails silently on expired token — 2026-03-28
  Resolved: Added token expiry check in `auth.ts:validateSession()`, shows error toast
```

**Key points:**
- Visually scannable — status/priority/category on one line, details indented below
- "Done" entries include date and brief resolution note (what was done, not just "fixed")
- Keep it flat and simple — no YAML frontmatter, no complex metadata
- Compatible with the `/todo` and `/bug-bash` skills

Add to `CLAUDE.md`:
```
## Bug tracking
Bugs and tasks are tracked in `TODO.md`. Use `/todo` to add entries and `/bug-bash` to work through them.
```

---

### 2. Engineering Diary

**Pitch:** A narrative log of how the project evolved — the *why* behind changes that isn't obvious from code or commit messages. Useful context for AI agents resuming work and for humans onboarding.

**Implementation:** Create `DIARY.md` in the repo root:

```markdown
# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-03-31 — Initial project setup

Set up the project with [brief description]. Key decisions:
- Chose X over Y because...
- Structure follows...
```

Add to `CLAUDE.md`:
```
## Engineering diary
Maintain `DIARY.md` — add an entry when making significant changes, architectural decisions, or non-obvious tradeoffs. Latest entries at top. Write in narrative form, not bullet dumps. Focus on *why* and *context*, not *what* (that's in the commits).
```

---

### 3. Changelog

**Pitch:** A simple, human-readable log of what changed and when. Unlike git log, it's curated — only meaningful changes, no merge commits or fixups. Easy for anyone to scan without touching git.

**Implementation:** Create `CHANGELOG.md` in the repo root:

```markdown
# Changelog

## 2026-03-31

- Add keyboard shortcuts for navigation
- Fix sidebar flicker on window resize

## 2026-03-28

- Initial release
```

**Key points:**
- Grouped by date (newest first), one bullet per change
- Short descriptions — what happened, not how
- No commit hashes, no authors, no version numbers unless the project does releases
- Update it with every commit

Add to `CLAUDE.md`:
```
## Changelog
Update `CHANGELOG.md` with every commit. Format: grouped by date (newest first), one bullet per change with a short description. Keep it human-readable — no commit hashes, no authors.
```

---

### 4. Regular Scorecard

**Pitch:** Periodic code quality audits catch problems before they accumulate. The `/scorecard` skill grades your codebase across 14 code dimensions and 5 agent-readiness ones.

Add to `CLAUDE.md`:
```
## Code quality
Run `/scorecard` periodically — after completing a feature, before major PRs, or when onboarding to assess health. Address critical findings before moving on.
```

---

### 5. Atomic Commits

**Pitch:** Small, focused commits are easier to review, revert, and understand. AI agents naturally batch work — this rule keeps commits clean.

Add to `CLAUDE.md`:
```
## Commits
Break work into small atomic commits — one logical change per commit. Don't bundle unrelated changes. A bug fix, a new feature, and a refactor are three commits, not one.
Commit often while working; before pushing, run `/consolidate` so the fix-the-fix trail lands as the changes it was.
```

---

### 6. Lint and Tests as Mechanisms, Not Reminders

**Pitch:** Catch breakage before it enters the history — with something that refuses, not a sentence asking nicely. Current models run tests unprompted; a "remember to test" rule adds noise and *unnecessary* testing. What they can't do is make a failing state uncommittable. A hook can.

**Implementation:** Identify the project's lint and test commands (`package.json` scripts, `Makefile`, CI config). Install a pre-commit hook that runs the lint command, and a `check` script that runs every instrument and writes `.verdict` (see step 13 for the template). Then add to `CLAUDE.md`:

```
## Pre-commit checks
Lint runs in the pre-commit hook; `scripts/check.py` runs the full suite and writes `.verdict`.
Never bypass the hook (`--no-verify`) and never commit over a failing `.verdict` — fix first.
```

If there's no test or lint setup at all, flag that as a gap and offer to set one up.

---

### 7. Test-First Development

**Pitch:** Writing a failing test before implementing forces clear thinking about expected behavior and gives you a definitive "done" signal. Balance fast unit tests with thorough end-to-end tests.

Add to `CLAUDE.md`:
```
## Test-first
Before implementing a feature or fix:
1. Write a test that captures the expected behavior
2. Run it — verify it **fails** (if it passes, the test isn't testing the right thing)
3. Implement until the test passes
4. Keep a healthy mix: fast unit tests for logic, end-to-end integration tests to validate it actually works in context

Don't skip step 2 — a test that never failed never caught anything.
```

---

### 8. Keep README Current

**Pitch:** Stale docs are worse than no docs — they mislead. Updating docs at commit time costs 30 seconds; fixing confused users costs hours.

Add to `CLAUDE.md`:
```
## Documentation
Update README.md (and any relevant docs) before committing if the change affects:
- Public API, CLI interface, or configuration
- Setup/installation steps
- Feature behavior visible to users
```

---

### 9. Encode Preferences into Rules

**Pitch:** When you correct the AI or express a preference during a session, capture it permanently so it doesn't need to be repeated.

Add to `CLAUDE.md`:
```
## Evolving preferences
When the user expresses a coding preference, convention, or correction during a session, offer to encode it into this CLAUDE.md file so it persists across sessions. Examples: naming conventions, preferred libraries, architecture patterns, things to avoid.
```

---

### 10. Mistake Retrospectives

**Pitch:** When the AI makes a mistake — especially "I forgot to do X" — treat it as a process problem, not a one-off. A quick retrospective and a rule change prevents recurrence.

Add to `CLAUDE.md`:
```
## Mistake retrospectives
When you make a mistake (especially forgetting something the user asked for):
1. Acknowledge it directly
2. Identify the root cause — why did this happen? (e.g. no checklist, unclear convention, missing rule)
3. Suggest a concrete project change to prevent recurrence (add a rule to CLAUDE.md, add a pre-commit check, create a checklist in the relevant skill)
Don't just apologize — fix the system.
```

---

### 11. Multiple Request Organization

**Pitch:** Allow user to batch up ideas and braindump quickly, but Claude to work through in an organized and diligent manner.

Add to `CLAUDE.md`:
```
## Completing requests

When the user gives multiple requests:
1. Queue them mentally but complete ONE fully before starting the next
2. "Complete" means: built, run, and verified working end to end by the project's own verification recipe — not "the tests pass"
3. If a request involves UI: screenshot the result and confirm it matches what was asked
4. Never mark something done until you've verified it works end-to-end
5. If you can't complete a request in one go (e.g., blocked by data issues), say so explicitly rather than half-doing it and moving on
6. If multiple requests conflict or depend on each other, state the dependency and ask which to prioritize

Anti-patterns to avoid:
- Starting 4 things, finishing 0
- Saying "let me commit this and move on to..." when the current thing isn't verified
- Adding code that changes behavior without testing the behavior changed
- Reacting to new user messages mid-task instead of finishing current work first
- Saying "let me ignore X for now" — either fix it or explicitly tell the user it's queued
```
---

### 12. Unattended Agent Permissions

**Pitch:** An overnight agent run that hits a permission prompt at minute three sits there until morning. The work isn't hard — it's just waiting on a keypress nobody is awake to make.

Check `.claude/settings.json` for a `permissions` block covering the commands this project's own build, test, and run recipe actually invokes. A global baseline in `~/.claude/settings.json` covers common tooling (cargo, npm, go, make, git); this step is about the project-specific commands that baseline can't know about — a custom script, an unusual test runner, a device harness.

Derive the list rather than guessing: read the build/test commands out of the project's `Makefile`, `package.json` scripts, `CONTRIBUTING.md`, or CI workflow, and allow those.

```json
{
  "askUserQuestionTimeout": "10m",
  "inputNeededNotifEnabled": true,
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(./scripts/e2e.sh:*)",
      "Bash(<this project's test runner>:*)"
    ]
  }
}
```

`inputNeededNotifEnabled` pushes a mobile notification when a permission prompt or question is waiting — a stalled fleet then interrupts the human instead of waiting for them. `askUserQuestionTimeout` makes a question the human isn't there to answer auto-continue with its recommended default after ten minutes, instead of holding an unattended run all night — one fleet's first preflight question sat for fourteen hours.

Two things worth flagging when you suggest this:

- **Don't allow `git push` globally.** Whether an agent may push is a per-project autonomy decision (see `/go-team`'s autonomy policy), not a blanket default. Add it to a project's allowlist only when the human has said that project's agents may push.
- **A `PreToolUse` hook that exits non-zero blocks the call.** That's correct for a guard (a personal-data or shared-checkout guard should block), but check the project doesn't have one that blocks on something an agent will legitimately hit all night.

---

### 13. Agent Operations Scaffolding

**Pitch:** `/go-team` and `/bug-bash` depend on a handful of files and one `CLAUDE.md` section. Without them the fleet either can't verify (and falls back to trusting reports) or can't tell the human's asks from its own. This step establishes all of it at once; it's what makes the difference between an overnight run that ships and one that stalls or stomps.

Add to `CLAUDE.md`:
```
## Agent operations

- **Verification recipe:** <how to drive the real thing — build, run, curl/click/drive; not just the test suite>
- **Autonomy policy:** merge-and-push | merge-locally-only
- **Shared singletons:** <devices, ports, session pools, databases agents must not share, and how to get a private one>
- **Do-not-touch:** <settled decisions, parked proposals, accepted limits>
- **Global-blast-radius files:** <the short list where any change has global effect; each has a tripwire test>
- **Requests lane:** ASKS.md
- **Setup version:** 2026-09
```

Then scaffold the files:

- **`ASKS.md`** — the human's own requests, one per entry with a status **and a `Done:` line** stating the verifiable completion condition. Seed it with the format:
  ```
  - [ ] **A1** <what Joe asked for>
    Done: <what must be true, checkable by an agent — "the docs site builds and every page in the plan exists", not "docs are better">
  ```
  Agents rank this above everything they find for themselves, and `/go-team` refuses to dispatch an ask without a `Done:` line — "build the complete application" is not a task.
- **`.claude/agents/foreman.md`** — the go-team foreman's agent definition (template in `~/.claude/skills/go-team/references/foreman-agent.md`). Its tool list has no `AskUserQuestion`, so the fleet cannot block on the human.
- **`LESSONS.md`** — the ledger. Seed it with the entry template from `/go-team` (what happened / what it cost / the rule / **the mechanism** / scope) and the rule that you sharpen an existing lesson before adding a new one.
- **The verdict file.** A `check` target or script that runs every instrument the recipe names and writes `.verdict` in the worktree root — one line per instrument `name=<exit code>`, plus `head=<full sha>` and `at=<iso8601>`. Merge paths read the file, never the worker's report. Add `.verdict` to `.gitignore`. Template (Python, per this repo's script rule):

  ```python
  #!/usr/bin/env python3
  import subprocess, datetime
  instruments = {"build": ["<build cmd>"], "lint": ["<lint cmd>"], "test": ["<test cmd>"]}
  lines = [f"head={subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()}",
           f"at={datetime.datetime.now().astimezone().isoformat(timespec='seconds')}"]
  for name, cmd in instruments.items():
      lines.append(f"{name}={subprocess.run(cmd).returncode}")
  open(".verdict", "w").write("\n".join(lines) + "\n")
  ```
- **A pre-commit hook** that runs the lint instrument, so a failing lint state is uncommittable — there's nothing to misreport. Optionally also refuse a commit whose subject says "fix" and whose diff deletes nothing unless the body names a `Cause:` — the cheapest mechanical check against fix-by-addition.
- **Leases.** Nothing to create; just note in `CLAUDE.md` that dispatch writes `$(git rev-parse --git-common-dir)/leases/<branch>` and merge removes it by name.
- **The push gate.** Nothing to create per repo: `/consolidate` installs a machine-wide pre-push hook via `core.hooksPath` that refuses a range that isn't one commit per feature or fix. On a new machine: `git config --global core.hooksPath ~/.claude/skills/consolidate/hooks`. It chains to this repo's `.git/hooks/*`, so the pre-commit lint hook above keeps running.
- **The foreign-repo guard.** Add to `.claude/settings.json` (merge, don't replace):
  ```json
  {"hooks": {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit",
    "hooks": [{"type": "command", "command": "python3 ~/.claude/skills/request/scripts/guard_foreign_repo.py"}]}]}}
  ```
  It denies edits into a *different* git repository and points at `/request`. Referenced by path so it never goes stale; if the skills aren't installed the hook errors and the call proceeds, which is the right failure mode.

The **setup version** is how `/go-team` knows to offer this project the delta when the scaffolding evolves. Bump it here when this step changes.

---

