---
name: idea
description: Capture a quick spark to the project's sparkfile (default `design/IDEAS.md`). One line per entry, optional bracketed tags inferred only when an obvious cue is present. `/idea <text>` to add, `/idea review` to show the list, `/idea iterate` to walk each entry with elaborate / delete / skip. Triggers on "/idea …", "spark", "add to sparkfile", "save this idea", "jot this down".
argument-hint: <text to capture> | review | iterate
---

# Idea

Low-friction capture for project sparks — half-formed thoughts that aren't yet bugs, tasks, or stories. The file is a sparkfile, not a tracker. The bar is "would I lose this if I didn't write it down somewhere I'd actually look later."

Three subcommands: **add** (default), **review**, **iterate**.

## How to Invoke

```
/idea login screen should show last-used email           # add
/idea what if we lazy-load the design tab                # add
/idea review                                              # show the list
/idea iterate                                             # walk each entry
```

The argument after `/idea` is the spark itself, unless it's exactly `review` or `iterate`.

---

## Sparkfile location

Since 2026-10-19 the sparkfile is the **`## Someday` section of `design/TODO.md`** (grootPM `design/stories/ready/work-model-contract.md`, D1/D4: a spark is a task with no priority yet, not a file of its own). Detect in this order; first hit wins:

1. `design/TODO.md` with a `## Someday` heading — append under it.
2. `design/TODO.md` without one — add `## Someday` above `## Done` (or at the end) and append.
3. A legacy `design/IDEAS.md`, `IDEAS.md`, `SPARKFILE.md` or `design/SPARKFILE.md` that still exists — append there; the fleet sweep folds these in.
4. Nothing — create `design/TODO.md` from `/groot-project`'s template (Open / Someday / Done) and append.

Entries under `## Someday` go in append order, newest at the bottom.

---

## Subcommand: add (default)

The mechanic is **append one line**. Format (a checkbox, so the reader counts it as an open task with no priority):

```
- [ ] <text> [tag, tag]
```

Tags are bracketed, lowercase, comma-separated. **Only attach tags when an obvious cue is present in the text** — a named UI surface, a named feature, a clear domain word. If you'd be guessing, omit the brackets. Speed matters more than tags; a one-line entry with no tags is fine.

Cue examples (tag) — _don't_ generalize beyond this kind of obviousness:

| Spark text                                 | Tag                     |
| ------------------------------------------ | ----------------------- |
| "login screen should show last-used email" | `[login]`               |
| "lazy-load the design tab"                 | `[perf, design-tab]`    |
| "the API client should retry on 429"       | `[api-client]`          |
| "we should talk to ops about this"         | (no tag — context-free) |

Workflow:

1. Find or create the sparkfile (see "Sparkfile location" above).
2. Decide whether tags apply. **Don't ask the user.** If unsure, no tags.
3. Append the line under the existing entries.
4. Confirm in **one line**: `Spark filed → design/TODO.md § Someday` (no recap, no quoting back what they typed).

**Don't commit.** Sparks are noisy by design — let them pile up until the user wants to review.

---

## Subcommand: review

Show the current sparkfile contents to the user. No analysis, no grouping unless explicit. Just:

```
design/IDEAS.md (12 entries):

- entry text [tag]
- entry text
- ...
```

If entries share a tag and there are 6+ in a tag, lightly group by tag at the bottom: "_Tagged: `[login]` x3, `[perf]` x2_" — but don't reorder the file.

If the sparkfile doesn't exist yet, say so and offer `/idea <text>` as the next step.

---

## Subcommand: iterate

Walk entries one at a time, oldest first. For each, present the entry and ask:

```
[3/12] - login screen should show last-used email [login]

  [e] elaborate   [d] delete   [s] skip   [q] quit
```

**Elaborate** — the spark deserves more than a line. Offer to:

- Expand it inline (a 2–4 line block under the original entry — still in the sparkfile).
- Promote it to `design/stories/drafts/<slug>.md` using the project's story template if present (see `/groot-project`'s `STORY_TEMPLATE.md`). On promotion, mark the sparkfile entry with `→ stories/drafts/<slug>.md` and leave it in place (don't delete — the breadcrumb is useful).
- Hand off to `/office-hours` for a real design conversation. (Suggest, don't auto-invoke.)

**Delete** — remove the line outright. No archive, no soft-delete. The sparkfile is meant to lose entries; that's the point.

**Skip** — move on. Don't track skips; the next iterate walks the same entries.

**Quit** — stop. Show how many were elaborated / deleted / skipped.

Don't auto-batch — one decision at a time, fast.

---

## Guidelines

- **Speed > everything.** A spark that takes 5 seconds to file is the product. If you find yourself drafting prose, you've already broken it.
- **Don't ask, don't recap.** No "should I tag this?", no "got it, I'll add the following entry to…". Just file it and confirm in one line.
- **Someday is not Open.** If something is concrete enough to have a priority and a fix, it is a task under `## Open` with a priority word (`/todo` or `/pm`). If it has design weight, it belongs in `design/stories/`. Sparks are the pre-stage to both; "promote" is moving the line up and giving it a priority.
- **Drift is fine.** Old sparks rot. `/idea iterate` is the cleanup tool — use it when the file feels heavy, not on a schedule.
- **Tag inference is lossy on purpose.** A spark without tags is a feature, not a failure. The user's text is the ground truth.

## Help

When invoked as `/idea help`, print the following block verbatim:

```
idea — Spark capture. Append-one-line sparkfile for half-formed thoughts.

Usage: /idea [verb-or-text]

Verbs:
  <text>            (default) Append "- <text> [tags]" to the sparkfile.
                    Tags are LLM-inferred only when an obvious cue is present.
  review            Show the current sparkfile (no analysis).
  iterate           Walk entries one-by-one: elaborate / delete / skip / quit.
  help              Show this message.

Sparkfile location (first hit wins):
  design/TODO.md "## Someday" → a legacy design/IDEAS.md / IDEAS.md /
  SPARKFILE.md → creates design/TODO.md with a Someday section.

Bar: "would I lose this if I didn't write it down?"
If concrete enough for a priority and fix → /todo.
If design weight → design/stories/ (via /groot-project's STORY_TEMPLATE).

See SKILL.md for full reference.
```

## Related

- `/todo` — for concrete bugs and tasks with priorities. Different lane.
- `/story` — for a capture that's already a paragraph of story-shaped intent: files it verbatim to `design/stories/drafts/` instead of squeezing it into a spark line.
- `/office-hours` — for ideas that have grown past sparkfile-shape and want a design conversation. `/idea iterate` can hand off.
- `design/stories/drafts/` (via `/groot-project`) — where elaborated sparks land if they graduate into spec work.
