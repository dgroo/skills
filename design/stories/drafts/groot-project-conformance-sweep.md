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

### 4. Checklist = pointers to owners, not copies of values

The sweep checks the project against a **checklist of "what a current project should
have/be."** The governing principle (Derek): **a single source of truth per convention**
— the checklist *checks/references* each convention's owner; it never *duplicates* the
expected value. So:

- terminal-color check → *delegates to `/terminal-setup`* (owns the truth)
- design-streamlined check → *delegates to `/cleanup-design conformance`*
- CLAUDE.md-blocks check → *compares the project CLAUDE.md against groot-project's own
  skeleton* (the source of that truth)
- code-review-staleness → *bespoke check* (git log + a recorded marker)

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
| terminal bg color set + current scheme | `/terminal-setup` + `.groot-project.toml` | delegate |
| Obsidian colors current | *TBD — needs a source of truth* | bespoke |
| independent code review within N | git log + a recorded marker | bespoke |
| CLAUDE.md carries current convention blocks | groot-project's CLAUDE.md skeleton | bespoke (compare) |
| diary sharded per host | groot-project diary convention | bespoke (presence) |
| gbrain registered / synced | `/sync-gbrain` | delegate |

(Seed only — grows via decision 5.)

## Open questions

- **Code-review staleness signal.** How is "last independent review" recorded —
  a marker file, a git trailer, a `.groot-project.toml` field? And what's `N`
  (commits? calendar? since-last-review-marker)?
- **Obsidian colors source of truth.** Where does "current Obsidian color convention"
  live so a check can read it? Today it may not have a single home — may need one created
  first (which is itself a single-source-of-truth fix).
- **`go` apply-safe-set boundary.** Precisely which finding classes are auto-safe under a
  bare `go` vs. held back for explicit per-item confirmation. Destructive or
  restructuring fixes (design-doc moves, deletions) are clearly held back.
- **Report shape.** Grouped by drifted/conformant/needs-you, à la `/sup`'s sections;
  conformant items collapse to a count.
- **beginners-mind boundary.** Keep the under-briefed-fresh-eyes pass and the
  maximally-briefed-conformance pass clearly separate; cross-reference, don't overlap.

## Next

- Resolve the code-review-staleness marker question (smallest concrete dependency).
- Decide the Obsidian-color source of truth (may be a prerequisite single-source fix).
- Draft the discipline rule for `~/.claude/CLAUDE.md`.
- Then extend `/groot-project` SKILL.md: state detection → sweep → findings report →
  `go`-applies-safe-set.
