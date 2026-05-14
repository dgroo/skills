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

Detect the sparkfile in this order. First hit wins.

1. `design/IDEAS.md`
2. `IDEAS.md` (repo root)
3. `SPARKFILE.md` (repo root)
4. `design/SPARKFILE.md`

If none exist, **create `design/IDEAS.md` by default** — the `design/` subtree (from `/groot-project`) is the right neighborhood. Fall back to `IDEAS.md` at the repo root only if there's no `design/` directory.

When creating for the first time, seed it with this header and nothing else:

```markdown
# Ideas

Spark capture. One line per entry. Tags in brackets are LLM-inferred and lossy — trust the text, not the tags. Use `/idea iterate` to walk and prune.

---
```

After the `---`, entries go in append order, newest at the bottom.

---

## Subcommand: add (default)

The mechanic is **append one line**. Format:

```
- <text> [tag, tag]
```

Tags are bracketed, lowercase, comma-separated. **Only attach tags when an obvious cue is present in the text** — a named UI surface, a named feature, a clear domain word. If you'd be guessing, omit the brackets. Speed matters more than tags; a one-line entry with no tags is fine.

Cue examples (tag) — *don't* generalize beyond this kind of obviousness:

| Spark text | Tag |
|---|---|
| "login screen should show last-used email" | `[login]` |
| "lazy-load the design tab" | `[perf, design-tab]` |
| "the API client should retry on 429" | `[api-client]` |
| "we should talk to ops about this" | (no tag — context-free) |

Workflow:

1. Find or create the sparkfile (see "Sparkfile location" above).
2. Decide whether tags apply. **Don't ask the user.** If unsure, no tags.
3. Append the line under the existing entries.
4. Confirm in **one line**: `Spark filed → design/IDEAS.md` (no recap, no quoting back what they typed).

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

If entries share a tag and there are 6+ in a tag, lightly group by tag at the bottom: "*Tagged: `[login]` x3, `[perf]` x2*" — but don't reorder the file.

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
- **The sparkfile is not the tracker.** If something is concrete enough to have a priority and a fix, it belongs in `TODO.md` (use `/todo`). If it has design weight, it belongs in `design/stories/`. Sparks are the pre-stage to both.
- **Drift is fine.** Old sparks rot. `/idea iterate` is the cleanup tool — use it when the file feels heavy, not on a schedule.
- **Tag inference is lossy on purpose.** A spark without tags is a feature, not a failure. The user's text is the ground truth.

## Related

- `/todo` — for concrete bugs and tasks with priorities. Different lane.
- `/office-hours` — for ideas that have grown past sparkfile-shape and want a design conversation. `/idea iterate` can hand off.
- `design/stories/drafts/` (via `/groot-project`) — where elaborated sparks land if they graduate into spec work.
