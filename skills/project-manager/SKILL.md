---
name: project-manager
description: Periodic backlog-stewardship pass for a project's design corpus — the "sit in the PM chair" ceremony. Delegates document hygiene to /cleanup-design, then adds the two layers cleanup-design won't: a judgment-heavy accuracy review of stories/notes (is this still true and still wanted?), durable reprioritization of the backlog (reorder TODO / story priority / NEXT.md on strong signal, ask on genuine tradeoffs), and grounded gap-proposal (file drafts for work the corpus clearly implies but nobody's filed). Stateless — the backlog files ARE the state. Use for "run a PM pass", "tidy and reprioritize the backlog", "is our backlog stale / correctly ordered / missing anything", "/pm". Trigger: /pm.
---

# /pm — Project-manager pass (Derek's flavor)

> "Sit in the PM chair for this project: tidy what's done, make sure the backlog is still _true_, put it in the right order, and tell me what's obviously missing."

`/pm` is a **periodic** backlog-stewardship ceremony, not a per-session tool. It's the deeper cousin of `/cleanup-design`: where cleanup-design does safe document hygiene (drift, dead links, move-to-done on strong signal), `/pm` **wraps** it and then makes the judgment calls cleanup-design deliberately declines — is this story still _wanted_, what's the right _priority order_, what work is _missing_. It's the `/sup`-wraps-`/sitrep` pattern: delegate the mechanical layer, add the opinionated one on top.

**Stateless by design.** There's no ledger, no last-run stamp, nothing to drift. The durable artifacts `/pm` writes — reordered `TODO.md`, `priority:` frontmatter on stories, a refreshed `design/NEXT.md`, newly-filed gap drafts — _are_ the state. Run it whenever the backlog feels stale; `/wrapup` will also nudge toward it when the corpus looks untended (see [Companions](#companions)).

## When to use vs. skip

Use for: "run a PM pass", "tidy and reprioritize the backlog", "is the backlog stale / in the right order / missing anything", a periodic stewardship sweep, or acting on a `/wrapup` staleness nudge.

Skip if: the project has no `design/` corpus (nothing to steward), or you want a single targeted edit (use Edit), or you just want "what do I do _this_ session" (that's `/next`) or a fresh-eyes/external-lens audit (that's `/beginners-mind`).

## Modifier — the decisiveness dial

`/pm` participates in the dial shared with `/wrapup`, `/sup`, `/next`: **`?` = assess, minimize mutation · `!` = act decisively, minimize interruption.**

| Form     | Posture             | Behavior                                                                                                                                                                                                                                                                    |
| -------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/pm ?`  | **Advise only.**    | Run the full pass read-only: report what it _would_ tidy, reorder, and propose. **Writes nothing.** The "just tell me the state of the backlog" form.                                                                                                                       |
| `/pm`    | **Default pass.**   | Do the hygiene (via `/cleanup-design`), the accuracy review, and **strong-signal** reprioritization directly. Present gap-proposals and any genuine priority tradeoffs for a decision — don't file/guess on those. Ask only where judgment is genuinely Derek's.             |
| `/pm !`  | **Autonomous pass.**| Raise autonomy: also file the grounded gap-drafts and act on more of the reprioritization without asking. **Still surfaces genuine priority _tradeoffs_** — relative priority between comparably-valuable items is Derek's call by nature, and `!` doesn't override that (same way it never overrides a destructive-op confirm). It removes friction on hygiene, gap-filing, and unambiguous reorders, not on real judgment. |

## Sequence

### 1. Orient

Discover the design layout (same as `/cleanup-design`'s Orient): `design/stories/{ready,drafts,done}/`, `design/helping-hands/`, `design/notes/`, canonical `design/DESIGN.md` / `README.md` / `NEXT.md`, root `TODO.md` / `REVISIT.md`, `CLAUDE.md` for conventions. If the layout is nonstandard or unclear, ask rather than guess.

### 2. Hygiene — delegate to /cleanup-design

**Run `/cleanup-design` first, don't reimplement it.** It owns the mechanical layer: drift (a decision one place the docs elsewhere haven't caught), dead cross-references, notes that should be `deprecated/`, and stories whose acceptance criteria are _obviously_ satisfied (move-to-done). Let it do its Scan → Triage → Present → Execute flow and land those findings.

You want a **clean corpus before you reorder it** — reprioritizing around stale/done entries is wasted work. If cleanup-design surfaces a big conformance drift (meta-files on the legacy root layout, etc.), note it but don't get pulled into a migration mid-PM-pass unless Derek opts in; that's cleanup-design's conformance mode, a separate errand.

### 3. Accuracy review — the judgment cleanup-design won't make

cleanup-design is deliberately conservative ("don't be aggressive", "only obvious satisfactions"). `/pm` is where the aggressive, _semantic_ review happens. Read the `ready/` and `drafts/` stories (and any active notes) and judge each against reality:

- **Is the problem still real?** A story written three weeks ago may describe a pain that a later decision already dissolved.
- **Has the approach been overtaken?** The premise or design may have been superseded by something shipped since — check recent commits / diary / done helping-hands.
- **Is a `ready/` story actually still ready?** "Ready" means design-baked; if its open questions have quietly reopened, it belongs back in `drafts/`.

Disposition each staler: **demote** (`ready/` → `drafts/`), **rewrite** (premise shifted but work still wanted), or **close** (overtaken — move to `done/` with a note, or delete a never-started draft). Strong signal → act; ambiguous → surface in the present step.

### 4. Reprioritize — durably

This is the core capability no other skill has. Judge relative priority **across the whole backlog** using the shared ranking model — read [`backlog-ranking.md`](../next/backlog-ranking.md) (installed at `~/.claude/skills/next/backlog-ranking.md`) §3: _unblocks-downstream → removes-risk → session-capacity → continuity → smaller-concrete-wins_. Same criteria `/next` and `/sup` rank by, so priorities don't drift between "what's next" and "what's important."

Then **write the order back** — this is durable, not a session-scoped ranking:

- **Reorder `TODO.md`** so the top is the highest-leverage open item.
- **Set / adjust `priority:` frontmatter** on stories where the corpus supports a clear level.
- **Refresh `design/NEXT.md`**'s do-next order if it's gone stale against the new ranking (overwrite; NEXT.md is the ephemeral "pick up here", its history lives in `DIARY.md`).

Split by confidence, mirroring cleanup-design's move-to-done discipline:

- **Strong signal → act.** Where the correct order is unambiguous (story A demonstrably blocks B and C; a stale draft clearly belongs at the bottom), just make the edit.
- **Genuine tradeoff → ask.** Where priority is a real judgment call — two items of comparable value, a tradeoff only Derek can weigh (user-facing polish vs. infra debt), a bet on direction — **present it as a compact option list and let Derek decide.** Never manufacture a confident reorder out of a genuine tie. This is the one place even `/pm !` still stops.

### 5. Gap-proposal — grounded, never imagined

Look for obvious holes: work the corpus clearly _implies_ but nobody's filed. **Every proposed gap must be evidenced** — borrow `/next`'s grounding rule (no imagined work):

- A `DESIGN.md` section that describes a mechanism with no story behind it.
- A shipped story whose natural follow-on was never filed.
- A `REVISIT.md` entry that's really a story in disguise (has design substance, not just a date trigger).
- A decision made in a helping-hand / diary with no implementing work queued.

Propose each as a one-line draft candidate with its evidence cited. **Do not invent plausible-sounding tasks** the project "should probably want" — a gap without a concrete in-corpus source is exactly the hallucinated-backlog failure mode to avoid. Default: present the gaps for confirmation; file the confirmed ones as `design/stories/drafts/` (with `/pm !`, file the well-evidenced ones directly and report what landed).

### 6. Present + verdict

Summarize the pass in one compact block, grouped:

- **Tidied:** what hygiene + accuracy review changed (delegated to cleanup-design + demotes/closes). Cite counts, not a wall of detail.
- **Reprioritized:** the durable reorders made (strong-signal), and — as a compact option list — any genuine priority tradeoffs awaiting a decision.
- **Gaps:** proposed drafts with their evidence, awaiting confirm (or filed, with `!`).

Keep it a glance. The corpus diff carries the detail; this block carries the _judgment_. On a genuinely tidy, well-ordered, non-gappy backlog, say so plainly — "backlog is clean, correctly ordered, no obvious gaps" is a valid and valuable outcome.

## Companions

- **Wraps `/cleanup-design`** (Step 2) — the mechanical hygiene layer. `/pm` adds judgment on top; it does not duplicate the drift/dead-link/move-to-done work.
- **Reuses `~/bin/backlog-scan`** — the shared queued-work scanner (`/next`, `/sup`), so there's one definition of "where work lives."
- **Adjacent to `/next`** — `/next` answers "what do I do _this session_" (ephemeral, forward, session-scoped, throws its ranking away). `/pm` answers "is the whole backlog healthy and correctly _ordered_" (durable, periodic, writes the order back). `/pm` sets the priorities `/next` then reads.
- **Adjacent to `/beginners-mind`** — that's a fresh-eyes audit through an external-corpus / behavioral lens (Recommendations, "why is it like this", cool things), stateful with a ledger. `/pm` is internal backlog stewardship, prioritization-framed, stateless. They complement; neither subsumes the other.
- **Nudged by `/wrapup`** — wrapup surfaces a skippable "backlog looks untended — consider `/pm`" line when the corpus is stale, the same silent-unless way it nudges toward an independent Codex review. Non-blocking; `/pm` is never auto-run.

## Rules

- **Delegate hygiene, don't reimplement it.** Step 2 is a `/cleanup-design` call. If you find yourself re-writing its drift/dead-link/move-to-done logic, stop and just invoke it.
- **Reprioritization is durable — write the order back.** The whole reason `/pm` exists over a two-step `/cleanup-design` → `/next` is that it _persists_ priority into `TODO.md` / story frontmatter / `NEXT.md`. A pass that only _reports_ a better order has skipped its core job.
- **Genuine priority tradeoffs are always Derek's call.** Strong-signal reorders act; real ties ask — even under `!`. Don't manufacture confidence to avoid a question; a surfaced tradeoff is a useful output, a wrong-but-confident reorder is a trust cost.
- **No imagined work.** Every gap-proposal cites an in-corpus source. A plausible-sounding task with no evidence is a hallucinated backlog item — don't file it.
- **Stateless.** Don't create a ledger or a last-run stamp. The backlog files are the state; the nudge keys on their staleness, not on a timer.
- **It's a glance, not a report.** The present block carries judgment; the corpus diff carries detail. Don't narrate every edit.

## Help

When invoked as `/pm help`, print the following block verbatim:

```
pm (project-manager) — Periodic backlog-stewardship pass. Wraps
/cleanup-design for hygiene, then adds accuracy review, durable
reprioritization, and grounded gap-proposal. Stateless — the backlog
files are the state.

Usage: /pm [? | !]

Verbs:
  (none)            Default pass: hygiene (via /cleanup-design) + accuracy
                    review + strong-signal reprioritization written back to
                    TODO/story-frontmatter/NEXT.md. Present gaps + genuine
                    priority tradeoffs for a decision.
  help              Show this message.

Modifiers (decisiveness dial):
  ?                 Advise only — run the full pass read-only, write nothing.
  !                 Autonomous — also file grounded gap-drafts and act on more
                    reorders without asking. Still surfaces genuine priority
                    TRADEOFFS (those stay Derek's call even under !).

Sequence:
  1. Orient         Discover the design layout.
  2. Hygiene        Delegate to /cleanup-design (drift, dead links, move-to-done).
  3. Accuracy       Semantic review cleanup-design won't do: is each story still
                    true / still wanted / still ready? Demote / rewrite / close.
  4. Reprioritize   Rank the whole backlog (shared backlog-ranking.md model) and
                    write the order back. Strong signal acts; real ties ask.
  5. Gaps           Propose drafts for work the corpus IMPLIES but nobody filed —
                    every one evidenced, never imagined.
  6. Present        One glance: Tidied / Reprioritized / Gaps.

Companions:
  Wraps /cleanup-design; reuses ~/bin/backlog-scan; adjacent to /next
  (ephemeral session pick) and /beginners-mind (fresh-eyes external audit);
  nudged by /wrapup when the backlog looks untended.

See SKILL.md for full reference.
```
