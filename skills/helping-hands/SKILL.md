---
name: helping-hands
description: Use when asked to work through a project's helping-hands items — the things filed in `design/helping-hands/` (or equivalent) that need the user's hands, eyes, credentials, or paid access ("work my helping-hands", "what's open in helping-hands", "let's knock out a helping-hand", "/hhands", "/helping-hands"). Validates each item is still live, extends the LLM-side scaffolding as far as it can go, and surfaces a single concrete ask. User-invoked on demand; does not replace citation-by-path JIT surfacing for in-flight work.
---

# helping-hands

Work through items in a project's `helping-hands/` directory (the user-must-do queue). For each item: re-check it's still live, push the "what I already did" further, then surface a single concrete ask. Optionally record closure when the user gives the answer.

## When to use vs. skip

Use for: "work my helping-hands", "what's open in helping-hands", "let's pick a helping-hand", "knock one out", "/hhands", "/helping-hands <slug>".

Skip if: the user is mid-task on a story and a helping-hand is *cited* in that story's `Related:` — that's the citation-by-path JIT path described in `helping-hands/README.md`. Surface the cited blocker inline; don't pull this skill for it.

## JIT-citation compatibility

This skill is **user-invoked, on-demand**. It deliberately scans the whole directory because the user asked it to. That's a different mode from rule 3 in the helping-hands README ("surface JIT, not at session start"), which forbids *passive* full-directory scans. Both modes coexist: citation-by-path stays the default for in-flight work; this skill is the explicit "let's do queue work" entry point.

## Routing

| Invocation | Action |
|---|---|
| `/helping-hands` (bare) | List open items with one-line summaries (cheap validation only). Pick one via `AskUserQuestion`. Then run the single-item flow. |
| `/helping-hands all` | Full validation on every open item. Present a table grouped by readiness category. Then `AskUserQuestion` for which to dive into. |
| `/helping-hands <slug>` | Skip listing; run the single-item flow on the slug match. Slug = filename without date prefix or `.md`; full filename also accepted. Ambiguous (e.g., two dates with the same slug) → ask which. |

## Auto-discovery

First existing path wins:

1. `design/helping-hands/`
2. `helping-hands/`
3. `docs/helping-hands/`

If none, ask the user where the queue lives. Don't guess into a different convention.

## Single-item flow

Run for the bare/slug paths, and after the user picks from `all`.

### 1. Orient

- Read the item file.
- Read the project's resume pointer (`design/NEXT.md` or equivalent) if present, as a **hint, not authority**. NEXT.md sometimes lists "open helping-hands" in its body; if its list disagrees with the directory's frontmatter, the directory wins and the disagreement is itself a finding to surface (NEXT.md is stale; propose a cleanup).
- Note `git log --oneline -20` to see what's landed recently. Helping-hands sometimes get resolved by sibling work without their `status:` being updated.

### 2. Validate

The interesting phase. For the selected item, check each:

- **Status still `open`** (or `in-progress`). If `done` or `dropped`, stop and tell the user.
- **Referenced files still exist** at the paths the item cites. Flag dead links (file moved, renamed, moved to `deprecated/`). A stale path doesn't auto-disqualify the item, but the user should know before acting.
- **Decision possibly captured elsewhere.** Grep for the item's slug, key terms, and cited story names in: recent commits (`git log --all -S` or `--grep`), the canonical design doc (`DESIGN.md` / equivalent), sibling helping-hands' `## Decision` sections, and `NEXT.md`. If a related decision exists, surface it — the item may be partially or fully moot.
- **Sibling synergy.** Are 2+ open items obviously co-batchable (same external source, same user trip, same decision)? Note it so the user can choose to batch.
- **Already-LLM-resolvable.** Can a quick read-only action close the loop without the user? E.g.: a web search for a referenced article, a grep for a referenced symbol, reading a referenced file the LLM hasn't seen, opening cited URLs. Try those before surfacing. If the loop closes, propose marking the item resolved and skip the ask. **Gate on tool availability in the current session:** if WebSearch/WebFetch are denied, mark such items `would-be-resolvable-with-web-access` and surface to the user with that context — don't burn a turn discovering the denial mid-flow.

### 3. Extend

Before surfacing, push "What I already did" further. The artifact's whole point is that the user's part is 30 seconds, not 10 minutes. For the selected item, ask:

- Is there scaffolding that would shrink the user's step? (E.g., draft the file they'd write into; pre-fill the form; produce the side-by-side comparison they'd otherwise have to construct.)
- Is there a decision pre-frame? (E.g., a 2-3 option `AskUserQuestion` with each option's tradeoffs.)
- Is there a parallel artifact the LLM can pre-populate so the user just confirms? (E.g., a draft Decision section ready to commit on yes.)

**Surface the proposed `## What I already did` extension as a diff in chat, alongside the Present step — don't write to the helping-hands file before the user sees the ask.** The helping-hand file is the source-of-truth artifact; the rule "never mutate without per-item approval" (see Closure) applies to scaffolding edits too. The lightweight approval form is fine: "I'll add this Extension block when I save — ok?" — but ask, don't pre-commit.

### 4. Present

Surface the ask:

- If the item is now truly user-blocked: show the file path, the one-paragraph ask, and the concrete steps. Use `AskUserQuestion` **only** when the ask is a 2–4 option pick. For yes/no permission grants, single-input asks (paste this link, share this list), or open-ended taste calls, surface in prose — don't manufacture multiple-choice.
- If the item became LLM-resolvable in step 2: skip the ask. Propose marking resolved with a Decision section. Get per-item approval before editing.
- If the item is stale (dead refs / decided elsewhere / clearly obsolete): propose disposition (close as `dropped`, close as `done` citing the existing decision, or update the references). Get approval.

## `all` flow

**Cheap filter first.** Read frontmatter only — `grep -H '^status:' <dir>/*.md` or equivalent — to separate `open`/`in-progress` from `done`/`dropped`. Don't load closed items' bodies; that pollutes context with already-decided content for no gain.

Run validate on the open set. Group by readiness:

| Bucket | Meaning |
|---|---|
| **actionable** | Open, fresh, well-scaffolded, genuinely needs the user. |
| **now-resolvable-without-user** | The LLM can close it with a read-only action. Propose closure. |
| **stale-references** | References dead files or paths that moved. Needs cleanup or update. |
| **possibly-already-decided** | A sibling artifact (commit, DESIGN.md section, sibling helping-hand) looks like it already settled this. Needs human confirmation to close. |
| **blocked-on-user** | Same as actionable but the LLM has exhausted scaffolding — pure user-side work (paid signup, physical access, taste call). |

Present as a single table: `# | slug | bucket | one-line summary | suggested next step`. Then `AskUserQuestion` for which to dive into, with options derived from the table (top 3-4 candidates plus "other / just show me the table again").

## Closure

When the user gives the answer in chat, do the synthesis work the item promises, then **propose** an edit:

- Set `status: done` (or `dropped` if cancelled).
- Add `resolved: YYYY-MM-DD` to frontmatter.
- Append `## Decision (YYYY-MM-DD)` with the choice and any extra direction the user added.
- List follow-ups filed/updated (other files touched, new stories drafted, sibling helping-hands).

**Never mutate the helping-hands file without per-item approval.** Show the proposed edit; ask. The artifact is the source of truth — surface, don't silently update.

## Common mistakes

- **Skipping the orient step.** Recommending an item that NEXT.md has already deprioritized, or that a recent commit already resolved. Read NEXT.md and recent commits before triaging.
- **Treating "open" as authoritative without re-checking.** `status: open` ages. Validate before surfacing.
- **Pulling the item to chat without extending scaffolding.** If the LLM can pre-draft the comparison, the form, or the Decision section, do that first. The artifact template's "What I already did" section is meant to be non-empty by the time the user reads it.
- **Auto-closing or auto-extending.** Closing items, OR editing the `## What I already did` section, without per-item user approval — even when "obviously decided elsewhere" or "obviously additive." Surface diffs, ask, edit on yes.
- **Reading deprecated/.** If the project has `notes/deprecated/` or similar with a "read with permission" rule (Derek's global CLAUDE.md), surface that a referenced file is in `deprecated/` but don't load its contents into your reasoning.
- **Auto-scanning at session start.** Don't. This skill is explicit/user-invoked. Citation-by-path is still the rule for in-flight work.
- **Flat prose listings.** Use `AskUserQuestion` when picking between items, or when an item's ask reduces to 2-4 options. Don't ask in prose when the user has to scroll back to remember the options.

## Quick reference

| Verb | Output | When |
|------|--------|------|
| `/helping-hands` (bare) | One-line list → pick → single-item flow | Default invocation |
| `/helping-hands all` | Validated readiness table → pick → single-item flow | Periodic queue review |
| `/helping-hands <slug>` | Single-item flow directly | User already knows which |

| Phase (single item) | Output |
|---|---|
| Orient | Internal context (NEXT.md, recent commits) |
| Validate | Status, refs, decided-elsewhere, sibling-synergy, LLM-resolvable |
| Extend | Editable diff to the item's "What I already did" |
| Present | Ask (with `AskUserQuestion` when options reduce) OR closure proposal OR stale-disposition proposal |

| Readiness bucket | Disposition |
|---|---|
| actionable | Surface ask |
| now-resolvable-without-user | Propose closure with Decision draft |
| stale-references | Propose ref update or closure |
| possibly-already-decided | Surface evidence; ask whether to close |
| blocked-on-user | Surface ask; user-side work is the bottleneck |

## Related

- `walkthrough` — narrative production sister skill; reviewer-comment / iterate / follow-ups pattern.
- `cleanup-design` — design-corpus drift detection; complementary lens (does the *spec* still match recent decisions?).
- Project conventions: each project's `helping-hands/README.md` (or equivalent) is the authoritative source for status fields, closure shape, and the citation-by-path rule.
