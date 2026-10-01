---
name: project-setup
description: Walk through project setup improvements for efficient AI-assisted development
argument-hint: [status]
---

# Project Setup

Interactive walkthrough that suggests improvements to make a project more efficient to work on with AI. Each suggestion is optional — present them one at a time, explain the benefit, and let the user accept, skip, or customize.

## How to Invoke

```
/project-setup              # walk through all suggestions
/project-setup status       # show which suggestions are already adopted
```

## Process

Before starting, read the project's existing `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, and any config files to understand what's already in place. Don't suggest things the project already does.

Present **all** applicable suggestions at once as a numbered list with a one-line description each. Default all to **yes**. Tell the user to reply with the numbers they want to **skip**, or just confirm to accept all. Then implement everything that wasn't skipped in one pass.

This is faster than going one-by-one — the user can scan the full list and opt out of what they don't want rather than answering ten separate questions.

---

## Suggestions

Thirteen, each with a one-line pitch. The full text — templates, `CLAUDE.md` snippets, scaffolding — is in `references/suggestions.md`; read the ones the user accepts when implementing them, not all thirteen up front.

| # | Suggestion | Pitch |
|---|---|---|
| 1 | **Bug Tracker / Todo List** | A single place to track bugs, tasks, and feature requests so nothing falls through the cracks. |
| 2 | **Engineering Diary** | A narrative log of how the project evolved — the *why* behind changes that isn't obvious from code or commit messages. |
| 3 | **Changelog** | A simple, human-readable log of what changed and when. |
| 4 | **Regular Scorecard** | Periodic code quality audits catch problems before they accumulate. |
| 5 | **Atomic Commits** | Small, focused commits are easier to review, revert, and understand. |
| 6 | **Lint and Tests as Mechanisms, Not Reminders** | Catch breakage before it enters the history — with something that refuses, not a sentence asking nicely. |
| 7 | **Test-First Development** | Writing a failing test before implementing forces clear thinking about expected behavior and gives you a definitive "done" signal. |
| 8 | **Keep README Current** | Stale docs are worse than no docs — they mislead. |
| 9 | **Encode Preferences into Rules** | When you correct the AI or express a preference during a session, capture it permanently so it doesn't need to be repeated. |
| 10 | **Mistake Retrospectives** | When the AI makes a mistake — especially "I forgot to do X" — treat it as a process problem, not a one-off. |
| 11 | **Multiple Request Organization** | Allow user to batch up ideas and braindump quickly, but Claude to work through in an organized and diligent manner. |
| 12 | **Unattended Agent Permissions** | An overnight agent run that hits a permission prompt at minute three sits there until morning. |
| 13 | **Agent Operations Scaffolding** | `/go-team` and `/bug-bash` depend on a handful of files and one `CLAUDE.md` section. |

## Status Check

When invoked with `status`, read the project's `CLAUDE.md` and check which of the above are already in place. Present a simple checklist:

```
Project setup status:

  [x] Bug tracker — using TODO.md
  [x] Engineering diary — DIARY.md exists
  [ ] Changelog — no CHANGELOG.md
  [ ] Regular scorecard — not mentioned in CLAUDE.md
  [x] Atomic commits — rule in CLAUDE.md
  [x] Test before commit — rule in CLAUDE.md
  [ ] Test-first development — not mentioned
  [x] Keep README current — rule in CLAUDE.md
  [ ] Encode preferences — not mentioned
  [x] Mistake retrospectives — rule in CLAUDE.md
  [ ] Multiple Request Organization — not mentioned
  [ ] Unattended agent permissions — no .claude/settings.json allowlist
  [ ] Agent operations scaffolding — no `## Agent operations` section / ASKS.md / .verdict

6/13 adopted. Want to add any of the missing ones?
```

## Guidelines

- **Don't push.** Present each suggestion neutrally. If the user says no, move on without arguing.
- **Adapt to the project.** A tiny script doesn't need a diary. A mature project probably has most of this. Scale suggestions to the project's stage and complexity.
- **Implement immediately.** When the user accepts a suggestion, do it right then — create the file, update CLAUDE.md, etc. Don't defer.
- **Detect existing conventions.** If the project already has a `CHANGELOG.md`, don't suggest `DIARY.md` as something separate — suggest adapting what exists.
- **Keep CLAUDE.md clean.** When adding rules, integrate them with existing sections rather than appending disconnected blocks. Maintain a coherent document.
