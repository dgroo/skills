---
name: statusline-explain
description: Explain what each segment of the Claude Code statusline means, with the current value and a note when the value is in an unusual state. Use when asked "what does that thing in the statusline mean", "explain the statusline", "what's on my statusline", `/statusline-explain`, or whenever the statusline is the subject of the question.
allowed-tools: Read, Bash
---

# Statusline Explain

Render a Markdown table that answers three questions for every segment currently on the Claude Code statusline:

1. **What does the segment mean?**
2. **What's the current value?**
3. **Is the value in a state worth noticing?**

Source of truth is the live statusline script. Don't hardcode segment lists — parse what's actually wired up so the skill stays in sync as the statusline evolves.

## Gather

Run in parallel:

1. **Read** `~/.claude/statusline-command.sh` — the segment definitions, jq filters, color rules, and "show when" conditions all live here. Section markers `# ROW 1` / `# ROW 2` group segments.
2. **Read** `~/.claude/state/statusline-input.json` — the most recent JSON the harness sent the statusline. Every segment's current value derives from this. If the file is missing, tell the user the statusline hasn't rendered since the dump line was added (or the dump line is missing); don't fabricate values.
3. **Bash** `bash ~/.claude/statusline-command.sh < ~/.claude/state/statusline-input.json` — gives the exact rendered text. Useful for sanity-checking that your value column matches what's on screen (strip ANSI with `sed 's/\x1b\[[0-9;]*m//g'`).
4. **Bash** when the segment depends on git state (branch, ahead/behind, dirty, worktree, no-remote, PR), shell out to the same git command the statusline uses.

## Output

```
## Statusline

### Row 1 — machine / git

| Segment       | Current             | Means                                            | Note                               |
| ------------- | ------------------- | ------------------------------------------------ | ---------------------------------- |
| dir           | `~/code/foo`        | Working directory, `~` for $HOME.                |                                    |
| branch        | `master`            | Current git branch.                              |                                    |
| ^N vN         | `^0 v0`             | Commits ahead / behind upstream.                 |                                    |
| ±N            | `±3`                | Dirty + untracked file count.                    | 3 uncommitted — wrap up soon.      |
| 🔄 alerts     | `dotfiles+1`        | Watched repos behind upstream (SessionStart).    | Pull `dotfiles` when convenient.   |

### Row 2 — Claude

| Segment       | Current             | Means                                            | Note                               |
| ------------- | ------------------- | ------------------------------------------------ | ---------------------------------- |
| ctx:%         | `92%`               | Context window remaining.                        |                                    |
| 5h/7d         | `5% / 20%`          | Rate-limit windows used (Max plan).              |                                    |
| model         | `Opus 4.7 (1M)`     | Current model. `(1M context)` = extended tier.   |                                    |
| 🧠 effort     | `xhigh`             | Reasoning effort (token budget for reasoning).   | xhigh = max; expensive but careful.|
| 💭            | on                  | Extended thinking — reasoning is exposed.        |                                    |
| cache:%       | `99%`               | Prompt cache hit rate.                           | Excellent — context staying warm.  |
| +N -N         | `+119 -43`          | Lines added/removed this session.                |                                    |
| $X.XX         | `$2.48`             | Implied API spend this session.                  |                                    |

_(only segments currently rendered appear; skip empty rows.)_
```

End with a **tl;dr** line _only if_ one or more Note cells flagged something. Examples:

```
**tl;dr:** xhigh effort + thinking is on — every response is expensive. Cache stays warm if you keep iterating quickly (5-min TTL).
```

```
**tl;dr:** Nothing unusual.
```

## Notes column: when to write something

A Note isn't a description of the segment — that's the Means column. Only write a Note when the _current value_ warrants attention. Rough guide:

| Trigger                            | Note                                                                  |
| ---------------------------------- | --------------------------------------------------------------------- |
| `ctx:%` ≤ 50                       | Yellow — context-pressure hook fires here; start eyeing a wrap point. |
| `ctx:%` ≤ 25                       | Bold red — auto-compaction territory; wrap up soon.                   |
| `ctx:%` ≤ 10                       | Reverse red — imminent compaction; wrap up now.                       |
| `5h:` or `7d:` ≥ 75                | Yellow — approaching rate-limit ceiling.                              |
| `5h:` or `7d:` ≥ 90                | Bold red — close to cap.                                              |
| `5h:` or `7d:` ≥ 95                | Reverse red — about to hit cap; throttle.                             |
| `±N` > 0                           | Uncommitted state — name the surface count.                           |
| `🔄 <repo>+N` present              | Name what to pull.                                                    |
| `🧠 effort` ≠ `medium` / `default` | Note the level + cost implication.                                    |
| `💭` on                            | Reasoning is exposed; mention if combined with high effort.           |
| `cache:%` < 50                     | Cache underused — likely paused too long (5-min TTL).                 |
| `cache:%` ≥ 90                     | Excellent — context staying warm.                                     |
| `$X.XX` ≥ 5                        | Note the spend (useful even on Max — relative cost signal).           |
| `🚀` fast mode                     | Fast mode active — Opus with faster output.                           |
| `style:<name>` non-default         | Output style is non-default; name it.                                 |
| `⚠️ 200k` present                  | Context exceeded 200k — performance/cost cliff.                       |
| Linked worktree (🌲/🌳/🌴)         | Note the worktree name so it's not mistaken for main.                 |
| `⚠️` no-remote marker on row 1     | Project has no git remote — not backed up.                            |
| PR state `changes_requested`       | Reviewer pushed back; PR needs attention.                             |

Skip the Note when the value is unremarkable. Empty cell is fine.

## Non-obvious commentary

Worth surfacing when relevant (don't repeat unprompted every run):

- **`(1M context)` suffix on model** — separate extended-context tier vs the standard 200k. Means a different request path and pricing.
- **Effort vs thinking are independent** — effort = _how many_ reasoning tokens; thinking = whether those tokens are _exposed_. xhigh + thinking off = expensive but invisible.
- **Cache TTL is 5 minutes** — high hit rates depend on quick back-and-forth. Walking away and coming back nukes the cache.
- **5h / 7d are rolling windows on Max plan**, not calendar windows. They drain continuously, not at midnight.
- **`$X.XX` is implied API spend, not what you're billed.** On Pro/Max the cost is absorbed; the number is still useful as a relative "how expensive was this session" signal.

## Rules

- Be terse. Table + optional tl;dr line. No preamble, no "here's a breakdown", no closing summary.
- Don't render segments that aren't currently on screen. If `🎮` isn't lit, omit the row.
- If a Note depends on a comparison (e.g., effort vs default), explicitly state the default in the Note — don't assume the reader remembers.
- If the JSON dump file is missing or stale (>5 min old), say so and ask the user to trigger a fresh render (any conversational turn does it).
- Don't invent segments. If the statusline has a new segment the skill doesn't recognize, render it with the value, an empty Means cell, and a "new — not yet documented in /statusline-explain" Note.

## Help

When invoked as `/statusline-explain help`, print the following block verbatim:

```
statusline-explain — Explain what each statusline segment means, with current value and notes when unusual.

Usage: /statusline-explain [verb]

Verbs:
  (none)            Render the current statusline as a table:
                    segment | current value | meaning | note (if unusual).
  help              Show this message.

Data source:
  ~/.claude/statusline-command.sh           — segment definitions (parsed).
  ~/.claude/state/statusline-input.json     — current values (raw JSON dump).

See SKILL.md for full reference.
```

## Related

- **statusline-command.sh** (in `dgroo/dot-claude`, not a skill) — owns the actual rendering. Edit it to add/remove segments; the skill reads the result.
- **`/sitrep`, `/sup`** — session-state reports, different domain. The statusline is _UI state_; sitrep/sup are _project state_.
