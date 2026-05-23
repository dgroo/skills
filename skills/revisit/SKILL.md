---
name: revisit
description: Add or work through entries in a project's `REVISIT.md` — the queue of items to resurface in a future session, either at a future date or when a specific event happens. Mirrors `/todo` (entry-style filing) and `/helping-hands` (walk-with-attempted-self-resolution flow), but the trigger is *time-or-event*, not *as-soon-as-possible*. Use when asked to "revisit this later", "check back in N weeks", "remind me when we work on X", "/revisit", "/revisit walk", "/revisit add ...".
argument-hint: <text> [--in 6w|--when "<event>"] | walk | <slug>
---

# revisit

Project-local queue of pending revisits in a single `REVISIT.md` at the project root. Each entry has a trigger (a date or a named event), a "Why" (context), and a "How to resolve" (what to check / how to know it's done).

The point: the LLM resurfaces due items at the start of a future session, attempts to close any it can resolve unattended, and surfaces the rest to the user. Same posture as helping-hands — Claude exhausts what it can do before pulling Derek in.

## When to use vs. skip

Use for: "revisit this in 6 weeks", "check back when X ships", "remind me when we get to story Y", "/revisit", "/revisit walk", "/revisit add ...".

**Skip when an entry has a better home.** If the revisit is bound to a specific story ("when we implement `story-Z`, reconsider X"), put the note in `story-Z`'s Open Questions or Implementation Notes section instead. REVISIT.md is for items that _don't_ have a natural home in an existing artifact — primarily date-triggered checks of external state (Anthropic docs, upstream issues, third-party feature releases) and event-triggered notes whose triggering event doesn't already live in a story.

Skip when the project doesn't have a `REVISIT.md` and the item being filed is the _first_ one — instead, propose creating the file and the CLAUDE.md convention line, then file.

## Routing

| Invocation                               | Action                                                                                                                                |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `/revisit` (bare)                        | List due items (date ≤ today, not resolved) with one-line summaries. Event-triggered items shown as a count only.                     |
| `/revisit walk`                          | Run the single-item flow on each due item in turn. Attempt self-resolution where possible; surface what can't be closed.              |
| `/revisit <slug>`                        | Focus the single-item flow on one entry by its slug.                                                                                  |
| `/revisit add "<text>" --in <duration>`  | File a new time-triggered entry. `<duration>` accepts `6w`, `2mo`, `30d`, or `YYYY-MM-DD`. **Run the dedup check first** (see below). |
| `/revisit add "<text>" --when "<event>"` | File a new event-triggered entry.                                                                                                     |

## Auto-discovery

`REVISIT.md` lives at the project root (sibling of `TODO.md`, `DIARY.md`). If absent and the user is asking to file, propose creating it. Don't silently scaffold into a different convention.

If multiple roots are in play (worktrees, nested repos), use the nearest enclosing root (walk up from `$PWD` to the first directory containing `.git/`).

## Entry format

Single file, newest-first within trigger category (date entries chronologically by `when`, event entries below them).

```markdown
## 2026-07-02 — auto-mode-in-remote-control

**Created:** 2026-05-21
**Priority:** medium

**Why:** `design/stories/drafts/roci-permission-tiers-and-approval-queue.md` open
question — Anthropic docs currently say Auto mode is unavailable in Remote
Control sessions. That caveat shapes the story's Layer 1 recommendation.

**How to resolve:**

1. Read https://code.claude.com/docs/en/permission-modes — search for "Remote Control".
2. If Auto is now supported in Remote Control: update the story's "Caveat"
   paragraph and mark this entry resolved with the doc snippet.
3. If still not: push the `when:` date out 6 weeks and re-check then.
```

Frontmatter-style bold fields (not YAML — keeps the file scannable as prose):

- `**Created:** YYYY-MM-DD` — required.
- `**Priority:** high|medium|low` — mirrors helping-hands. Default `medium`.
- `**Resolved:** YYYY-MM-DD — <one-line decision>` — appended at closure. Won't re-surface but stays for audit.

## Single-item flow

Same five-phase shape as helping-hands: Orient, Validate, Extend, Present, (Closure).

### 1. Orient

- Read the entry.
- Check `git log --oneline -20` for recent commits whose subjects mention the slug or its key terms — a sibling commit may have already resolved the question.
- For entries that reference a story, **also read the referenced story file** before acting — the story may have been updated since the revisit was filed.

### 2. Validate

- **Trigger still live.** Date passed? Event happened? If neither, this isn't actually due — flag and skip.
- **References still valid.** If the entry points at a story / URL / doc section, confirm the target still exists. Surface stale references but don't auto-disqualify.
- **Already resolved elsewhere.** Grep recent commits and the referenced story (if any) for the slug or its decision terms. The same patterns helping-hands uses ("now-resolvable-without-user", "possibly-already-decided") apply.
- **LLM-resolvable.** The whole point of the "How to resolve" section is to make this answerable: a doc to read, a grep to run, a fact to check. If the steps are unambiguous and don't require credentials/taste/physical access, **attempt them** before surfacing. Gate on tool availability: WebFetch/WebSearch denied → mark `would-be-resolvable-with-web-access` and surface with that context.

### 3. Extend

If the entry is going to surface to the user (not auto-closable), push the "How to resolve" further before doing so. Pre-read referenced material, draft the diff the user would write, surface the side-by-side comparison they'd otherwise have to build. Same scaffolding rule as helping-hands — the user's part should be 30 seconds, not 10 minutes.

### 4. Present

- **Auto-closable:** propose closure. Show the diff (the `**Resolved:**` line + any cascading edits to referenced stories). Get per-item approval before writing.
- **Truly user-blocked:** surface the ask. Use `AskUserQuestion` only when the decision reduces to 2–4 options; otherwise prose.
- **Stale / decided elsewhere:** propose disposition (resolved citing the existing decision, or update the references).
- **Not yet due (false positive in the date check):** surface as such; don't ask the user to re-decide an entry that hasn't ripened.

### 5. Closure

Same closure shape as helping-hands:

- Append `**Resolved:** YYYY-MM-DD — <one-line decision>` to the entry.
- Optionally a short `**Notes:**` line if the decision needs more than the one-liner.
- If the resolution cascades — story update, doc change — file those edits as separate commits per the project's atomic-commit rule.

**Never mutate the entry without per-item approval.** Surface the proposed diff; ask; edit on yes.

## Filing flow (add)

Run for `/revisit add "<text>" --in <duration>` or `--when "<event>"`.

### 1. Dedup check (load-bearing)

Before writing to `REVISIT.md`, check whether the item has a better home:

- **If the text references a specific story / plan / helping-hand:** read that file. Propose appending to its Open Questions / Implementation Notes section instead of filing here. Surface the proposed diff; ask. Only fall through to REVISIT.md filing if the user says "no, file in REVISIT".
- **If REVISIT.md already has an entry covering this:** propose extending the existing entry's "How to resolve" rather than creating a sibling. Get approval.
- **If the text describes work to do now, not later:** push back — this looks like a `/todo`, not a `/revisit`. Suggest the right verb.

### 2. Parse the trigger

- `--in 6w` → resolve to a concrete `YYYY-MM-DD` (today + 6 weeks). Accept `Nd`/`Nw`/`Nmo`/`Ny` shorthand or a literal date.
- `--when "<event>"` → event-triggered. Quote the event verbatim in the heading.

If both flags are missing, ask which trigger applies. Don't default; the trigger shape is the whole point.

### 3. Compose and write

- Heading: `## YYYY-MM-DD — <slug>` (slug = kebab-case of the first few meaningful words) or `## (when: <event>) — <slug>`.
- Body: `**Created:** <today>`, `**Priority:** medium` (default), `**Why:** ...`, `**How to resolve:** ...`.
- Insert in the right place in the file (date entries sorted chronologically by `when`; event entries grouped below).
- Show the proposed insertion as a diff; get approval; write.

### 4. Commit

```
git add REVISIT.md
git commit -m "revisit: <slug> (when: <date or event>)"
```

### 5. Confirm

One line: `Filed: <slug> — REVISIT.md (resurfaces <when>)`. No body recap.

## `walk` flow

Iterate over due items in order. For each: run the single-item flow. After each item closes (or surfaces an ask), pause for the next user direction before moving on — don't run the whole queue silently.

If the queue is empty (no due items), say so and exit.

## Bootstrap (first entry in a project)

If `REVISIT.md` doesn't exist and the user is filing the first entry:

1. Propose creating `REVISIT.md` at the project root with a short header explaining the convention.
2. Propose adding a one-line lane entry to the project's CLAUDE.md "Project conventions" section pointing at the file and this skill.
3. On approval, write both, then file the entry per the normal flow.

## Common mistakes

- **Filing in REVISIT.md when the entry belongs in a story.** Dedup check is load-bearing; not a formality.
- **Auto-closing without approval.** Surface diffs, ask, edit on yes — even when "obviously decided." Mirror helping-hands' rule.
- **Skipping the Orient step.** Closing an entry that a sibling commit already resolved, without checking recent commits, is the equivalent of helping-hands skipping NEXT.md.
- **Reading deprecated/ or archived/.** Surface that a referenced file is in a read-with-permission directory; don't load contents per the global CLAUDE.md rule.
- **Surfacing event-triggered items by date.** Event triggers aren't time-triggers. The SessionStart hook counts them but doesn't surface them as "due."
- **Defaulting the trigger.** No silent "let's say 4 weeks" — ask if both `--in` and `--when` are absent.

## Quick reference

| Verb                                 | Output                                             | When                     |
| ------------------------------------ | -------------------------------------------------- | ------------------------ |
| `/revisit` (bare)                    | List of due items + count of event-triggered items | Default invocation       |
| `/revisit walk`                      | Single-item flow on each due item in turn          | Queue review             |
| `/revisit <slug>`                    | Single-item flow on one entry                      | User already knows which |
| `/revisit add "<text>" --in 6w`      | Filing flow → new entry → commit                   | Filing date-triggered    |
| `/revisit add "<text>" --when "..."` | Filing flow → event-triggered entry → commit       | Filing event-triggered   |

| Phase (single item) | Output                                                       |
| ------------------- | ------------------------------------------------------------ |
| Orient              | Internal context (recent commits, referenced story state)    |
| Validate            | Trigger live? Refs valid? Decided elsewhere? LLM-resolvable? |
| Extend              | Push "How to resolve" further before surfacing               |
| Present             | Ask, closure proposal, or stale-disposition proposal         |
| Closure             | `**Resolved:**` line + cascading edits (with approval)       |

## Help

When invoked as `/revisit help`, print the following block verbatim:

```
revisit — Project-local queue of items to resurface at a future date or
when a specific event happens. Mirrors /todo (filing) and /helping-hands
(walk-with-attempted-resolution flow).

Usage: /revisit [verb] [args]

Verbs:
  (none)            List due items (date ≤ today). Event-triggered shown
                    as count only.
  walk              Single-item flow on each due item in turn.
  <slug>            Single-item flow on one entry by slug.
  add "<text>" --in <duration>     File a new time-triggered entry.
                                   <duration>: 6w, 2mo, 30d, or YYYY-MM-DD.
  add "<text>" --when "<event>"    File a new event-triggered entry.
  help              Show this message.

Single-item flow phases:
  Orient            Recent commits; referenced story state if any.
  Validate          Trigger still live? Refs valid? Decided elsewhere?
                    LLM-resolvable? (with tool-availability gating)
  Extend            Push "How to resolve" further before surfacing.
  Present           Ask / closure proposal / stale-disposition.
  Closure           **Resolved:** line + cascading edits, with approval.

Filing dedup check (load-bearing):
  References a story/plan/helping-hand   → propose appending there.
  Existing revisit covers it             → propose extending that entry.
  Looks like "do it now"                 → push back; suggest /todo.

File location: REVISIT.md at project root.

Bootstrap: first entry in a project proposes creating REVISIT.md + a
CLAUDE.md conventions line.

See SKILL.md for full reference.
```

## Related

- `todo` — Joe's skill. Same filing shape (enrich → assign priority → commit) for items to do _now_. `/revisit` is `/todo` with a future trigger.
- `helping-hands` — same walk-with-attempted-resolution posture. The revisit queue diverges from helping-hands in two ways: single file (not directory), and the trigger is part of the entry (not implicit "as soon as someone gets to it").
- `bug-bash` — autonomous queue-walker. The `/revisit walk` mode borrows the "step through items, attempt close, surface what can't" shape.
