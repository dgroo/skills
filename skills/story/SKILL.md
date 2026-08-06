---
name: story
description: Capture a story-shaped work item mid-session with near-zero derail — file the user's text verbatim as a stub in `design/stories/drafts/<slug>.md`, marked "captured, not yet pondered", queue an in-session task to resurface it once the current block of work wraps (fresh-context elaboration beats cold pickup), then return to whatever the session was doing. No exploration, no elaboration, no questions at capture time. The rung between /idea (one-line spark) and /ponder (does the design thinking now). Triggers on "/story <text>", "file this as a story", "capture this as a story", "story for later".
argument-hint: <text to capture> | help
---

# Story — verbatim story capture, zero derail

Capture for work that's bigger than a spark but not ready to think about *now* — a paragraph of intent typed mid-session while the session is busy with something else. The mechanic is **file verbatim and get out of the way**. Structure and design thinking come later, via `/ponder`.

The capture tier: `/idea` (a sentence) → `/story` (a paragraph, story-shaped) → `/ponder` (do the thinking now).

## How to Invoke

```
/story I want to add to the holdings table a little menu with quick ways to
       do certain tasks for a given instrument - e.g., add a capital call...
/story help
```

The argument is the story text itself. If invoked with no argument, ask exactly one question: *"What's the story?"* — then file the answer.

---

## Where it lands

`design/stories/drafts/<slug>.md` — `drafts/` is load-bearing: the stories convention (see `/groot-project`) says never implement from `drafts/` without promotion, which is exactly the protection an unpondered stub needs. **Never file to `ready/`.**

- If `design/stories/drafts/` doesn't exist, create the path. If the project has no `design/` at all, still create `design/stories/drafts/` and mention `/groot-project` fills out the rest of the convention.
- Slug: derive a short kebab-case slug from the content (you title it; the body stays theirs).

---

## The stub format

Honor the project's `design/stories/STORY_TEMPLATE.md` frontmatter if present; default:

```markdown
---
author: user
priority: medium
---

# <Concise Title You Derive>

> **Captured via `/story` — not yet pondered.** Verbatim capture below; no
> exploration or design thinking has happened. Run `/ponder <slug>` to develop
> it. Don't implement from this stub.

<the user's text, verbatim>
```

- `author: user` — the words are theirs; the stories convention reads that field as "intention likely correct, spec likely incomplete," which is exactly right.
- `priority:` — take an explicit cue from the text ("critical", "someday") if present; otherwise `medium`. Don't ask.

---

## Workflow

1. **Dup scan, filenames only.** `ls design/stories/*/` — if an existing story obviously covers this, append the capture to that story under a `## Captured addition (/story, unreviewed)` heading instead of creating a twin, and say which file. Don't read story bodies hunting for matches; the filename scan is the whole check.
2. **Write the stub.** Verbatim body — don't rewrite, summarize, expand, or fix their grammar. Your only authored contributions are the title, slug, frontmatter, and marker block.
3. **Commit.** If the design-sync watcher is running (`launchctl list 2>/dev/null | grep -q design-sync-watch`), just save — the watcher owns `design/` commits and lands it within seconds. Otherwise commit the stub yourself — stage the one file explicitly (`git add <path>`, commit with a pathspec) — and push.
4. **Queue the fresh follow-up.** Add an in-session task (TaskCreate/TodoWrite): *"When the current block of work completes: offer to flesh out `<slug>` while it's fresh."* The point: the story is on the user's mind *right now*, and for a human, elaboration works best close to the moment of thinking it. The stub file is the persistent truth; this task is just the orchestration view that makes it resurface at the natural boundary (per the global todo-list-is-a-view rule).
5. **Ack in one line and get out:** `Story stub filed → design/stories/drafts/<slug>.md · will resurface when this block wraps` — then resume whatever the session was doing, without recapping the capture.

---

## The fresh follow-up

When the current block of work completes, surface the stub and offer — don't auto-run — to flesh it out:

- **Default offer: work it up together, interactively.** The user just typed the capture, so they're at the keyboard with hot context — ask them the questions `/ponder` would have to guess at (scope, examples, what "done" looks like), then grow the stub into a real story and, if it clears the bar, promote it to `ready/` with the answers recorded.
- **Alternatives:** hand it to `/ponder <slug>` (autonomous, they're stepping away), or leave the stub for later — their call, one line each.
- **Best-effort, honestly.** If the session ends before the boundary, the in-session task evaporates — the stub survives and the `/sup`/`/next` backlog scans are the fallback, but the freshness window is lost. Don't pretend otherwise; that's the accepted trade for zero-derail capture.

---

## Guidelines

- **Verbatim is the contract.** The user typed a paragraph because the richness matters; every word you "improve" is signal lost. If the text seems to contradict itself, file it anyway — `/ponder` is where tensions get worked out.
- **Near-zero derail.** No exploring the codebase, no clarifying questions, no "here's how I'd approach it." A `/story` queued mid-turn should cost the working session one file write and one line of output.
- **Not a tracker entry, not a spark, not a think.** Concrete bug/task with a priority → `/todo`. One-line thought → `/idea`. Ready to think now → `/ponder`. `/story` exists precisely for "story-shaped, but not now."
- **Promotion is `/ponder`'s job.** The stub's marker names the next step; this skill never takes it.

## Help

When invoked as `/story help`, print the following block verbatim:

```
story — Verbatim story capture, zero derail. Files a "not yet pondered" stub
        to design/stories/drafts/ and returns to the work at hand.

Usage: /story [<text> | help]

Arguments:
  <text>            File the text verbatim as design/stories/drafts/<slug>.md
                    with an author:user / not-yet-pondered stub header, and
                    queue an in-session task to resurface it once the current
                    block of work wraps (flesh out while fresh; maybe promote).
  (none)            Ask "What's the story?" and file the answer.
  help              Show this message.

Tier: /idea (a sentence) -> /story (a paragraph) -> /ponder (think now).
Follow-up: offered at the block boundary, interactive by default; /ponder
<slug> is the autonomous alternative. Never implement from drafts/.

See SKILL.md for full reference.
```

## Related

- **`/idea`** — one-line spark capture to the sparkfile; its `iterate` elaborate-path promotes sparks into the same `drafts/` lane `/story` files to directly.
- **`/ponder`** — the developer of these stubs: explore, think in options, write the real story. `/story` is deliberately the un-`/ponder`: capture without thinking.
- **`/todo`** — concrete bugs/tasks with priorities; different lane.
- **`/groot-project`** — owns the `design/stories/` convention (readiness-by-directory, `STORY_TEMPLATE.md`) this skill files into.
