# CLAUDE.md

## First-time setup

If skills are not yet installed (check with `make list`), prompt the user to run:

```bash
make install
```

Ask if they have existing skills they'd like to import into this repo using `/import-skill`.

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

1. Update `README.md` — add the skill to the Skills table (keep alphabetical order)
2. Run `make install` to symlink it
3. Commit both the skill and the README update together

### Skill frontmatter

Every SKILL.md must have `name` and `description`. Add `argument-hint` if the skill accepts arguments — it shows in autocomplete.

`allowed-tools` is optional and **enforced** — it restricts which tools Claude can use without asking permission while the skill is active. Use it for read-only or limited-scope skills (e.g. sitrep). Omit it to use normal permission settings.

Don't use `user_invocable: true` — it's the default. Only use `user_invocable: false` for background-knowledge skills that shouldn't appear in the `/` menu.

## Evolving preferences (project-specific)

Cross-session *personal* preferences (style, taste, habits) belong in auto-memory — that system captures them automatically. This section is for *project-specific* conventions that apply only inside this skills repo: naming patterns for skill files, tone choices for skill descriptions, etc. When such a convention emerges, offer to encode it here.
