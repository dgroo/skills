# CLAUDE.md

## First-time setup

If skills are not yet installed (check with `make list`), prompt the user to run:

```bash
make install
```

Ask if they have existing skills they'd like to import into this repo using `/import-skill`.

## Upstream provenance

This repo is a fork of `joewalnes/skills`. Three classes of files, two rules:

- **Skills tracked in upstream** — list with `make upstream-skills`. **Hard rule: never edit in place.** Fork into a new local skill with a distinct name. The pre-commit hook (`scripts/check-upstream-edits.sh`) blocks commits that modify upstream-tracked `skills/<name>/`; override with `SKIP_UPSTREAM_GUARD=1` only for an actual upstream contribution.
- **Top-level files** (`CLAUDE.md`, `README.md`, `Makefile`) — also upstream-tracked, but **soft rule**: local edits are fine. Expect to resolve merge conflicts on upstream pulls.
- **Local-only skills** — anything else under `skills/`. Edit freely.

Before editing any skill, confirm provenance:

```bash
git log upstream/main -- skills/<name>/
```

Empty output = local-only, safe to edit. Non-empty = upstream-tracked, fork instead.

Check for upstream updates with `make upstream-check` (also surfaced by `/sup`). Run periodically — pulling stays cheap when you do it often.

## Bug tracking

Bugs and tasks are tracked in `TODO.md`. Use `/todo` to add entries and `/bug-bash` to work through them.

## Engineering diary

Maintain `DIARY.md` — add an entry when making significant changes, architectural decisions, or non-obvious tradeoffs. Latest entries at top. Write in narrative form, not bullet dumps. Focus on *why* and *context*, not *what* (that's in the commits).

## Code quality

Run `/scorecard` periodically — after completing a feature, before major PRs, or when onboarding to assess health. Address critical findings before moving on.

## Documentation

Update `README.md` (and any relevant docs) before committing if the change affects:
- Public API, CLI interface, or configuration
- Setup/installation steps
- Feature behavior visible to users

## When adding a new skill

After creating a new skill in `skills/<name>/SKILL.md`:

1. Update `README.md` — add the skill to the right table (dev loop or on-demand)
2. Run `make install` to symlink it
3. Commit both the skill and the README update together

### Writing the skill — routing and context cost

Every skill's description is loaded into every session's context and competes for a fixed listing budget; the whole `SKILL.md` is loaded on invocation. So:

- **Description ≤ 120 characters, and it says *when*.** One clause on what it does, one narrow clause on when to use it ("use before merging a branch"), never a keyword net ("use for anything to do with code quality"). No method, no mechanism — that's body text.
- **State the boundary with neighbours.** If two skills could both plausibly fire (`scorecard` vs `slop`), each description names what distinguishes it.
- **Root as router past ~150 lines.** Keep the process and output format in `SKILL.md`; move rubrics, worked examples, scripts' docs, and anything needed in only one phase to `references/*.md`, and say when to read each. A skill invoked repeatedly (on a `/loop`) gets the strictest budget.
- **No handholding.** Don't tell the model which tools to use, to read the task carefully, or to run the tests — current models do that unprompted, and the instruction causes *unnecessary* testing. Say what *done* means and where the boundaries are; give explicit permission for known-safe workflows so a careful model doesn't stop early.
- **Mechanisms over nags.** A rule the model must follow gets a hook, a script, or a file the gate reads — not a bolded sentence. The 48-hour fleet retro found rules violated by their own authors within hours; the fixes that held were mechanisms.
- **Write for the weakest model that will run it.** `go-team` briefs reach haiku; a skill shared with other people's agents reaches unknown models. Prescription is justified by evidence, not habit — where you keep it, say why.
- **Delete skills that don't earn their listing slot.** A demo or test fixture costs every session a little context, forever.

### Scripts

When a skill needs a helper script (not a one-off command in a Bash tool call), write it in **Python or Perl, not bash**. Both are always installed; bash is not portable — macOS ships `/bin/bash` 3.2 (no associative arrays, various POSIX-only gaps), which has caused real bugs (a `declare -A` skill script silently failed on this exact machine). Reserve bash for short inline commands, not committed script files.

### Skill frontmatter

Every SKILL.md must have `name` and `description` (≤ 120 chars, says when — see *Writing the skill*). Add `argument-hint` if the skill accepts arguments — it shows in autocomplete.

`allowed-tools` is optional and **enforced** — it restricts which tools Claude can use without asking permission while the skill is active. Use it for read-only or limited-scope skills (e.g. sitrep). Omit it to use normal permission settings.

Don't use `user_invocable: true` — it's the default. Only use `user_invocable: false` for background-knowledge skills that shouldn't appear in the `/` menu.

## Evolving preferences (project-specific)

Cross-session *personal* preferences (style, taste, habits) belong in auto-memory — that system captures them automatically. This section is for *project-specific* conventions that apply only inside this skills repo: naming patterns for skill files, tone choices for skill descriptions, etc. When such a convention emerges, offer to encode it here.
