---
name: integrate-comments
description: Use when iterating on a markdown doc that has inline `<!-- @<user>: -->` review comments — integrate each comment's intent into the prose, rewrite the marker to `<!-- @<user>+seen: -->` in place (don't strip), and emit a tabular review-log sibling. Generic comment-driven iteration that works on any annotated markdown: walkthroughs, survey drafts, design docs, code-review notes. Triggers: "process my comments on X", "integrate the @<user> comments", "iterate on this doc's review", "/iterate", "/integrate-comments".
---

# Integrate-comments

Generic comment-driven iteration. The target doc has inline HTML-comment markers (`<!-- @<user>: ... -->`) left by a reviewer; this skill integrates each comment's intent into the surrounding prose, marks the comment processed in place, and records dispositions in a sibling review-log.

Content-type-agnostic: works on walkthroughs, survey drafts, design notes, code-review markdown, etc. **Framing rules** (what the doc is _for_, what scope to target) come from the doc itself, not the skill — see [Framing detection](#framing-detection).

## When to use vs. skip

Use when: the user has reviewed an existing markdown artifact and wants their `@<user>:` comments rolled into the prose; or when bare `/walkthrough` (or sibling content-generator skills) hands off to this skill because an artifact with markers exists.

Skip when: the user wants to _draft_ new content (use the appropriate content-generator skill), or strip already-processed markers (use `/walkthrough clean-comments` — the cleanup verb lives there).

## Routing

| Invocation                   | Action                                        |
| ---------------------------- | --------------------------------------------- |
| `/integrate-comments` (bare) | Auto-discover target (see below) → integrate. |
| `/integrate-comments <path>` | Integrate the named doc.                      |

`/iterate` is a recognized alias. Voice/typed phrases like "iterate on X", "process the @derek comments on X" route here.

**Auto-discovery (when no path given):**

1. Search order, first existing root wins: `design/notes/`, `notes/`, `docs/`.
2. Within that root, identify candidates by `<!-- @<user>:` markers (un-processed, recent-modified preferred).
3. Single match → use it. Multiple → `AskUserQuestion` listing candidates with last-modified date. Zero → ask the user for an explicit path.

## Preconditions

### Username discovery

Determine which `@<word>:` prefix to scan for:

1. **Scan the doc first.** Grep for any `@<word>:` markers; if a single distinct prefix appears, use it. The doc is authoritative — handles cases where `git config user.name` returns a system handle while the reviewer annotates with a different prefix (e.g. their first name).
2. Fall back to `git config user.name` (lowercased).
3. Then `git config user.email`'s local-part.
4. Then `$USER`.
5. Else ask.

If multiple distinct prefixes appear (genuine multi-reviewer doc), process all of them in one pass, attributing dispositions per-reviewer in the review-log.

### Uncommitted-artifact safety check (hard stop)

Before mutating the target, run `git status --porcelain <path>`. If the target has uncommitted changes, **stop and ask** the user to either commit or explicitly accept loss. Iterate rewrites prose; running it on dirty working state risks destroying unsaved work with no clean recovery path. This is non-negotiable.

### Framing detection

Read the doc's framing rule before integrating, so substantive comments get judged against the right scope. Detection order:

1. **`## Framing note` heading** in the doc body — read that paragraph. (Example: "This is not a v-infinity document. Target what would ship in v0.1.")
2. **First paragraph** if it reads like framing — phrases like "This walkthrough describes...", "This document targets...", "Not a spec — a draft of...".
3. **Frontmatter `iterate_framing:` field** if present (opt-in override).
4. **None found** → no special framing; integrate at face value.

The framing rule is _context for judgment_, not a script. Use it to decide e.g. whether a comment requesting expanded scope is in-bounds or should be deferred to follow-ups.

If the framing-note itself is the target of a `@<user>: ` comment (reviewer questioning the framing), surface that as a **framing-decision preamble** at the top of the review-log before integrating other comments — framing changes affect how everything else gets read.

## Integrate

### 1. Preserve-don't-strip

For each `<!-- @<user>: <comment> -->`:

1. **Integrate the comment's intent** into the surrounding prose.
2. **Rewrite the marker in place** from `@<user>:` to `@<user>+seen:` (preserve the comment text verbatim). The inline context stays visible — a reader can tell which paragraph each comment hung off — while the prefix signals the skill has processed it.
3. Record the disposition in the review-log (see below). Markers are not the disposition record; the log is. **One marker variant only** — no `+deferred:` / `+ack:` subtypes. Disposition richness lives in the log.

Stripping seen markers is a separate, explicit operation: `/walkthrough clean-comments <path>` (lives on the walkthrough skill but works on any markdown).

### 2. No fabrication

Don't invent facts to satisfy a comment. If a comment asks for content the surrounding source material doesn't settle:

- Prefer to **flag the gap inline** with a brief note ("[need source]" or similar), not invent.
- Or **defer** as a follow-up candidate in the review-log.
- Never quietly extrapolate past what the source supports.

This guardrail matters most in `current`-mode walkthroughs and similar dev-mode contexts where readers trust the doc as ground truth.

### 3. Review-log

Append a `<docname>-review-log.md` sibling to the target. Shape:

```markdown
# <docname> — review log (<date>)

<!-- Framing-decision preamble: any reframing decisions called out before the per-comment table. Mode/framing changes get noted here, not in the per-row table. -->

## Per-comment dispositions

| #   | Topic         | What changed                                 |
| --- | ------------- | -------------------------------------------- |
| 1   | <short topic> | <prose-level description of the integration> |
| 2   | …             | …                                            |

## Deferred

- <comments not integrated this pass; why; where to revisit>

## Follow-up candidates

- <comments that surfaced spec gaps or downstream work>

## Positive feedback

- <comments that validated existing prose; no change needed>

## Skill-level / meta-issues

- <comments about the doc's framing, the skill itself, etc.>
```

The framing-decision preamble is a free-text block above the table — short, narrative, and only present when reframing was on the table. Mode is preserved through iterate by default; explicit mode changes are a re-draft, not an iterate.

### 4. After integration

Show the diff and stop. **Don't auto-commit.** Surface anything that looks like a real spec gap as a follow-up candidate (defer to the content-generator skill's follow-ups verb when one exists — `/walkthrough follow-ups` for walkthroughs).

### 5. No markers, but doc was edited directly

If the doc has been edited since last iterate but no new `@<user>:` markers exist, surface the diff and ask whether to _learn from the edits_ (extract implicit feedback into the review-log) rather than mutating prose.

## Common mistakes

- **Strips markers during iterate.** Removes inline context a future reader (or future iterate pass) might want. Fix: rewrite `@<user>:` → `@<user>+seen:` in place; cleanup is a separate verb.
- **Iterates over dirty working state.** Destroys unsaved edits. Fix: hard-stop if `git status` shows the target dirty; ask the user to commit or accept loss.
- **Fabricates to satisfy a comment.** Reviewer asks "what about X?" and the skill invents an X-handling story. Fix: flag the gap, don't invent.
- **Ignores framing-note.** Treats every comment as in-scope. Fix: read framing first; defer out-of-scope asks to follow-ups.
- **Auto-files follow-ups.** Writes stories/todos into spec directories without approval. Fix: stage in the review-log; user files.
- **Renames `+seen:` to other variants.** `+deferred:`, `+ack:`, etc. Fix: one marker variant; richness in the log.
- **Auto-commits the integration.** Removes the user's chance to review. Fix: show diff and stop.

## Quick reference

| Phase         | Output                                                                      |
| ------------- | --------------------------------------------------------------------------- |
| Preconditions | Username, framing rule, clean working state confirmed                       |
| Integrate     | Prose rewritten; markers rewritten `@<user>:` → `@<user>+seen:` in place    |
| Review-log    | Sibling `<docname>-review-log.md` with framing preamble + per-comment table |
| Stop          | Diff shown; user decides whether to commit                                  |

**Marker states:**

| Marker                          | Meaning                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------ |
| `<!-- @<user>: <text> -->`      | Unseen, pending integrate                                                      |
| `<!-- @<user>+seen: <text> -->` | Processed; disposition in review-log; remove via `/walkthrough clean-comments` |

**Sibling skills:**

- `/walkthrough` — draft narrative walkthroughs (content generator). Hands off here when an existing walkthrough has unseen markers.
- `/walkthrough clean-comments [path]` — strip `+seen:` markers once the user is done with them.
- `/walkthrough follow-ups [path]` — triage `[extrap]` / `[planned]` tags + review-log resolved items into candidate stories. (Walkthrough-specific because of the tag set; other doc types can grow their own follow-ups verbs locally.)

## Help

When invoked as `/integrate-comments help`, print the following block verbatim:

```
integrate-comments — Iterate on annotated markdown by integrating
<!-- @<user>: --> review comments into the prose.

Usage: /integrate-comments [path]

Verbs:
  (none)            Auto-discover target → integrate.
  <path>            Integrate the named doc.
  help              Show this message.

Aliases:
  /iterate          Recognized alias.

Preconditions (hard stop):
  Username discovery   Scans doc for @<word>: prefixes; falls back to git
                       config user.name / user.email / $USER / ask.
  Uncommitted check    Stops if target has uncommitted changes.
  Framing detection    Reads doc's ## Framing note or first-paragraph
                       framing rule so comments are judged in scope.

Behavior:
  Preserve-don't-strip   Markers rewritten @<user>: → @<user>+seen: in place.
  No fabrication         Flag gaps inline; never invent to satisfy a comment.
  Review-log             Emits <docname>-review-log.md sibling with
                         per-comment dispositions + framing preamble.

Cleanup is a separate verb on the walkthrough skill:
  /walkthrough clean-comments [path]   Strip +seen: markers explicitly.

Content-type-agnostic: works on walkthroughs, survey drafts, design notes,
code-review markdown, etc.

See SKILL.md for full reference.
```
