---
author: claude
priority: medium
---

# /groot-project as a state-aware conformance sweep

**Status:** draft · filed 2026-06-20 · Opus 4.8 (1M context)

## Problem

Derek's coding setup evolves continuously — new conventions, new color schemes, new
review cadences, new skills, new CLAUDE.md rules land almost every week. Bootstrapped
projects then *drift*: a repo set up two months ago is missing whatever's been codified
since. There's no single action that sweeps an existing project against the *current*
state of the setup and catches it up. The drift is invisible until something breaks or a
fresh-eyes pass happens to notice.

Concretely, the kinds of things that go stale in an existing project:

- design docs/dir no longer streamlined after months of revisions
- terminal background color missing, or on an older scheme
- Obsidian colors not matching the current convention
- no independent code review in a long time (or ever) — now that `/wrapup` suggests one
- the project's `CLAUDE.md` missing convention blocks added globally since bootstrap
  (diary sharding, the lanes block, the diary-worthiness heuristic, …)
- … the list only grows

## Existing infrastructure (scan before building)

This capability is **mostly an orchestrator over pieces that already exist** — the value
is the *sweep + the checklist*, not new audit logic. What's already there:

- **`/cleanup-design`** already grew a *conformance* mode — "check a project against the
  canonical design-corpus model / catch a drifted project up on conventions" /
  "/cleanup-design conformance". The design-docs bullet is already a delegate.
- **`/groot-project`** is already re-runnable + idempotent ("detects what's there, only
  adds what's missing") — but currently checks *structural presence*, not *currency*.
- **`/terminal-setup`** owns terminal color + `.groot-project.toml` migration.
- **`groot-project/obsidian-setup.py`** (Obsidian baseline, Phase 7C) configures a
  project's Obsidian vault to the federation baseline. Crucially, it **derives the vault
  accent from `.groot-project.toml [terminal].background`** — the *same* source the
  terminal color uses. It's re-runnable and ships `--dry-run`. A delegate (see decision 4).
- **`last-codex-review` (dotfiles) + `/wrapup`'s review-cadence nudge** already own
  "independent review is stale": `last-codex-review --nudge` reads `~/.codex` rollouts
  keyed by repo cwd (no state file), silent unless >21d since a non-Claude Codex review
  *and* non-doc code changed since. `/wrapup` already surfaces it. A delegate.
- **`/beginners-mind`** is the closest cousin — a stateful, periodic project audit that
  surfaces improvements — but it's the **wrong home**: its identity is the *under-briefed
  fresh observer*, deliberately NOT told the conventions. This sweep is the opposite — a
  *maximally-briefed conformance check*. They should cross-reference, not merge.
- The **`self-check` GitHub-issue broadcast** (global CLAUDE.md) is the *push* variant —
  "audit every repo for concern X." This sweep is the *pull* variant — "sweep THIS
  project against everything." Complementary.

## Design decisions

### 1. One state-aware entry point — no separate verb

`/groot-project` reads the project's state and does the appropriate thing. Fresh/empty
repo → bootstrap (unchanged). Already-scaffolded project → the **conformance/currency
sweep becomes the primary behavior**. Same command, no `update` flag to remember. This is
the natural extension of the existing "detects what's there" design: not just *is it
present* but *is it current*.

### 2. Bootstrap auto-adds; the sweep proposes (but `go` is trivial)

- **Bootstrap layer** stays auto-add-missing — presence is binary and safe.
- **Sweep layer** is *propose-and-confirm* — currency findings are judgment calls
  ("design docs have drifted, here's a restructure"; "no code review in N commits"). It
  surfaces a findings report rather than silently mutating, the way `/sup` proposes.
- **But `go` is the one-keystroke default.** Derek expects to say `go` ~99% of the time,
  so the report must make that trivial: a bare `go` applies the **safe/recommended set**
  in one shot (decisiveness-dial convention, shared with `/sup`/`/next`/`/wrapup`).
  Findings that are genuinely judgment-heavy or destructive are called out separately and
  excluded from the blanket `go`.

### 3. Orchestrator, not monolith

The sweep delegates to each domain owner's conformance mode and aggregates one report. It
must **not** reimplement design-audit (cleanup-design owns it) or color-setup
(terminal-setup owns it). This respects the federation's one-owner-per-mechanism rule.

**Implementation shape — detect/dry-run → aggregate → `go` applies live.** Each delegate
ideally exposes a *detect* mode that reports drift without mutating; the sweep runs all of
them to build the findings report, and a bare `go` (decision 2) re-runs the safe set for
real. `obsidian-setup.py`'s `--dry-run` is the validating precedent — it "prints what
would change; writes nothing." The convention to push onto delegates as they're wired in:
a `--dry-run`/`--check` mode and an exit/stdout contract the sweep can parse. (`last-codex-review --nudge`
already fits — it's read-only and emits one line or nothing.)

### 4. Checklist = pointers to owners, not copies of values

The sweep checks the project against a **checklist of "what a current project should
have/be."** The governing principle (Derek): **a single source of truth per convention**
— the checklist *checks/references* each convention's owner; it never *duplicates* the
expected value. So:

- terminal-color check → *delegates to `/terminal-setup`* (owns the truth)
- **Obsidian-vault check → *delegates to `obsidian-setup.py --dry-run`*** — and this is
  the cleanest worked example of the principle: the Obsidian accent is *derived from*
  `.groot-project.toml [terminal].background`, the **same single source** the terminal
  color reads. Terminal and Obsidian aren't two color conventions — they're two *views*
  of one source (`.groot-project.toml`), each with its own owner/applier. The sweep never
  knows "the expected color"; it asks each owner "are you in sync with the source?"
- design-streamlined check → *delegates to `/cleanup-design conformance`*
- CLAUDE.md-blocks check → *compares the project CLAUDE.md against groot-project's own
  skeleton* (the source of that truth)
- review-staleness check → *delegates to `last-codex-review --nudge`* (dotfiles; owns the
  "is an independent review overdue" signal — 21d + code-changed)

**Why this matters for rot:** because each check reads its owner live, a check's expected
value *can't* go stale. The only remaining rot risk is "we forgot to add a check for a
brand-new convention" — which is what decision 5 covers. This shrinks the maintenance
burden from "keep every expected value current" (impossible by hand) to "remember to
register new conventions" (a discipline rule).

### 5. Anti-rot: inline checklist + a discipline rule (option 1, registry deferred)

The checklist lives inline in the `/groot-project` skill (a list of pointer-checks). New
conventions get onto it via a **discipline rule** — the same pattern already trusted
elsewhere ("when behavior changes, update the doc in the same commit"; the diary-worthiness
rule):

> When you codify a convention that projects should conform to, add its
> (pointer-)check to the `/groot-project` sweep in the same change.

This rule belongs in the global `~/.claude/CLAUDE.md` (where conventions are codified) so
it fires at the moment of codification.

**Deferred alternative — a conventions registry** (option 2): a single living doc
(`dot-claude` or `groot-claude-coord`) as the source of truth, fed by the cross-project
capture QUEUE, read by the sweep. More robust against rot, but it requires *building and
maintaining the registry first*, and conventions are scattered across many homes today.
Graduate to this only if the discipline rule visibly fails.

## Initial checklist seed

| Check | Owner / source of truth | Kind |
| --- | --- | --- |
| design/ streamlined & conformant | `/cleanup-design conformance` | delegate |
| terminal bg color set + current scheme | `/terminal-setup` (source: `.groot-project.toml`) | delegate |
| Obsidian vault on baseline (accent from project color) | `obsidian-setup.py --dry-run` (source: `.groot-project.toml`, shared w/ terminal) | delegate |
| independent review not stale (>21d + code changed) | `last-codex-review --nudge` (dotfiles) | delegate |
| CLAUDE.md carries current convention blocks | groot-project's CLAUDE.md skeleton | bespoke (compare) |
| diary sharded per host | groot-project diary convention | bespoke (presence) |
| gbrain registered / synced | `/sync-gbrain` | delegate |

(Seed only — grows via decision 5. Note how many rows resolved to *delegate* once the
owners landed — reinforces decision 3: this is an orchestrator, not an audit engine.)

## Resolved since drafting (Phase 7C landed)

- **Code-review staleness — resolved.** `last-codex-review --nudge` (dotfiles) is the
  owner: reads `~/.codex` rollouts keyed by repo cwd, no state file, threshold 21d +
  non-doc-code-changed. `/wrapup` already consumes it. The sweep delegates to the same
  helper.
- **Obsidian colors source of truth — resolved (and it's not a separate convention).**
  The vault accent derives from `.groot-project.toml [terminal].background` via
  `obsidian-setup.py` — the same single source as the terminal color. No new home
  needed; the check delegates to `obsidian-setup.py --dry-run`.

## Open questions

- **`go` apply-safe-set boundary.** Precisely which finding classes are auto-safe under a
  bare `go` vs. held back for explicit per-item confirmation. Destructive or
  restructuring fixes (design-doc moves, deletions) are clearly held back.
- **Report shape.** Grouped by drifted/conformant/needs-you, à la `/sup`'s sections;
  conformant items collapse to a count.
- **Delegate detect-mode contract.** Not every owner has a `--dry-run`/`--check` yet
  (`obsidian-setup.py` and `last-codex-review` do; `/cleanup-design`, `/terminal-setup`
  may need a detect-only path). Define the stdout/exit contract the sweep parses.
- **Ordering / prerequisites.** `obsidian-setup.py` requires `.groot-project.toml` to
  exist (it errors and points at `/terminal-setup`). The sweep must run the color-source
  checks before the views that derive from them.
- **beginners-mind boundary.** Keep the under-briefed-fresh-eyes pass and the
  maximally-briefed-conformance pass clearly separate; cross-reference, don't overlap.

## Next

- Define the delegate detect-mode contract + the `go` safe-set boundary (the two
  remaining design dependencies).
- Draft the discipline rule for `~/.claude/CLAUDE.md` (decision 5).
- Then extend `/groot-project` SKILL.md: state detection → run delegates' detect modes →
  findings report → `go`-applies-safe-set. **Collision caveat:** `groot-project/SKILL.md`
  is under active development (Phase 7C). Implementing the sweep there wants a worktree or
  coordination — not a parallel edit.
