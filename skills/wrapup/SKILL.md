---
name: wrapup
description: Actively assess whether this session is safe to end. Inventories in-flight state, executes routine wrap-prep writes (DIARY entries, story files, design/NEXT.md session handoff, queue notes) directly, auto-commits and pushes complete work (surfacing only ambiguous or destructive cases), then gives a definitive READY / WAIT / STAY verdict. Judges whether THIS session is the right place to keep working — pushing back with a visible STAY when bouncing would discard real in-flight context — and sharpens that call against an intent hint when one is given.
argument-hint: "[?|!|?!] [<optional intent for next work>]"
---

# Wrapup — explicit session-end readiness gate

> "Are we actually in a good place to wrap up and start fresh? If so, get us to the /sup state. If not, say so."

Use when you're about to bounce the session and want a yes-or-no answer (not silence-as-signal). Trigger phrases: "are we good to wrap?", "safe to bounce?", "can I end here?", "I'm going to start a new session if you think we are good to do so", "/wrapup", "/wrapup I'm thinking about picking up X next."

**Companion to `/sup`.** `/sup` is descriptive (situation report, default-silent on end-of-session). `/wrapup` is action-imperative (always answers, always preps). Same neighborhood, different verb class. After a successful `/wrapup` READY verdict, opening a fresh session and running `/sup` will work cleanly — that's the contract.

**Not the same as `/context-save`.** `/context-save` persists this session's working context for `/context-restore` later. `/wrapup` doesn't preserve anything cross-session — it just ensures the _vault and repo state_ would let any fresh CC session pick up cleanly.

## Modifiers — the decisiveness dial

`/wrapup` takes an optional leading `?` / `!` / `?!` modifier (before any intent hint) that sets how eager the skill is to _act_ vs. to _check first_. This is a convention shared across `/wrapup`, `/sup`, and `/next`:

> **`?` = assess, minimize mutation · `!` = act decisively, minimize interruption · `?!` = assess first, then act only on a positive verdict.**

Each skill implements only the modifiers that differ from its default. `/wrapup`'s default _acts_ (it does prep + commits), so it uses the full spectrum — four forms on one axis, check-only → act-iff-green → act-then-report → act-maximally:

| Form         | Posture              | Behavior                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/wrapup ?`  | **Advise only.**     | Inventory + Phase 4 recap + verdict. **Makes no changes** — no auto-`/cpush`, no DIARY / story / `NEXT.md` / queue writes. "Where do we stand?" Overlaps `/sup`'s readiness read by design; it's the lightest touch.                                                                                                                                                                                                              |
| `/wrapup ?!` | **Gated wrap.**      | Assess readiness _first_. If the verdict is ✅ READY, do the full wrap (Phase 1.5 + Phase 3) and confirm. If ⏸ WAIT / ↺ STAY, surface the verdict + what's blocking and **hold off on prep** — let the user decide whether to proceed anyway. Won't pour effort into wrap-prep when the honest answer is "keep going." The "I came back after an hour — wrap if we're good, else tell me" form.                              |
| `/wrapup`    | **Default wrap.**    | Assume you're wrapping: do the routine prep + commits (Phase 1.5 + 3 — mechanical, low-judgment), _then_ verdict. Ask only on the carve-outs. Phase 2's high-bar STAY check still runs; on the rare STAY it preempts the Phase 3 handoff writes (you're not leaving), though Phase 1.5's commit+push of complete work has already landed.                                                                                       |
| `/wrapup !`  | **Autonomous wrap.** | Like default, but raise the interrupt threshold to the max: resolve everything you can yourself, minimize ⏸ WAIT, make the call on borderline-ambiguous dirt instead of surfacing it. **Only** pause for the genuinely irreversible carve-outs — destructive git ops (force-push, `git reset`, rebase, `rm` of tracked files) still require per-instance confirm per the global Safety rule; `!` does **not** override that. |

`?!` and `!?` are equivalent. A modifier composes with an intent hint: `/wrapup ! picking up slice 3` = autonomous wrap, judged against that intent. The distinction that matters: `?!` checks the verdict _before_ doing prep (optimizes for "should you even be leaving?"); the default does prep _then_ reports (optimizes for "you're leaving — let me get you there").

## Three verdicts

| Verdict      | When                                                                                                                  | What                                                                                                  |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| ✅ **READY** | Clean tree, decisions journaled, tasks resolved or written down. Or intent hint isn't a fit for this session's cache. | Confirm safe-to-bounce. End.                                                                          |
| ⏸ **WAIT**   | Something in-flight would be lost or hard to pick up cold, and resolving it needs a call only you can make.           | List items + proposed prep, surface the ambiguous/destructive call, execute once resolved, re-assess. |
| ↺ **STAY**   | Real context value here for the natural next step — a given intent hint, or (on a bare wrap) the in-flight thread itself. Bouncing discards it and forces a cold re-derive. **High-bar and rare** — not "you've been working here." | Push back: explain what's in cache that helps, suggest staying. User decides.                         |

## Sequence

### Phase 1: Inventory in-flight state

Gather in parallel — same shape as `/sup`'s sitrep mirror, with sharper edges on "what would be lost":

1. `git status` — uncommitted changes, untracked files. The blocker question: is any of this hand-typed work that would be hard to redo? (Lockfile churn = no; new feature half-done = yes.)
2. `git stash list` — stashes are usually forgotten. Any non-empty stash is a flag.
3. `git log --oneline <branch>..HEAD` (or `git log -5` on detached) — what shipped this session, for the journal-completeness check below.
4. **TaskList** — open tasks the conversation never closed.
5. **Conversation context** — scan for:
   - Non-trivial **decisions** made this session (architecture, tradeoffs, scope calls) that aren't in `DIARY.md` or `design/` notes yet. These are the highest-leverage "would be lost" items — code commits don't capture the why.
   - In-flight reasoning ("I was about to…", "next step is…") that isn't pinned anywhere durable.
   - Half-done refactors mentioned but not finished.
6. **Independent-review cadence** — run `last-codex-review --nudge` (a read-only dotfiles helper; `~/.codex` rollouts keyed by repo cwd, no state). It is silent unless it's been >21 days since an independent (non-Claude) Codex look at this repo _and_ non-doc code has changed since — in which case it prints a one-line `↳ Independent review: …` nudge toward a `/codex review` sweep. This is a periodic, codebase-wide reminder (Derek won't remember on his own), **not** a per-session gate. Capture its output for Phase 4; if the command is absent (older host / dotfiles not pulled) just skip — never block on it.

Don't read whole files — this is a scan, not an audit. Heuristic: would a fresh CC session running `/sup` on this repo have everything it needs?

### Phase 1.5: Auto commit-and-push sweep

If Phase 1's `git status` surfaced uncommitted changes that look **complete-and-committable** (not mid-experiment dirt the conversation already flagged as WIP), **just run `/cpush` directly** — no up-front offer. Invoking `/wrapup` is itself the instruction to "make sure everything is recorded and pushed so I can start fresh"; treat that as standing authorization to land the session's complete work. `/cpush` commits everything as atomic commits and pushes. After it completes, re-confirm `git status` is clean, then continue to Phase 2 / Phase 3 — the "uncommitted changes" bullets in Phase 3 are now mostly moot.

Skip Phase 1.5 entirely when:

- The tree is already clean.
- The conversation already established that the dirt is mid-experiment / intentional WIP (don't re-litigate). Surface it in the verdict instead of committing it.
- Only stashes are dirty (Phase 3 handles those separately).

**Surface-don't-auto carve-outs** (the "something really needs your attention" cases): if landing the work would require a **destructive git op** (force-push, `git reset`, rebase, history rewrite, `rm` of tracked files), stop and ask per-instance — the global Safety rule still governs those, and `/wrapup` does not override it. Likewise, if the dirty tree is genuinely ambiguous (can't tell complete work from mid-experiment dirt from the conversation), surface it rather than guessing.

Rationale: across observed sessions, `/cpush` then `/wrapup` ran as a two-step ceremony at session end, and `/wrapup` was reliably approving the commit + push anyway. Collapsing the offer into an automatic sweep removes the rubber-stamp step; the diary entries written in Phase 3 can then reference the just-landed SHAs cleanly. The only things still gated are the irreversible ones.

### Phase 2: Judge cache-relevance — should you even be leaving?

**Always run this check**, intent hint or not. Its whole job is to catch the case where wrapping is the wrong move and say so _visibly_ — before you bounce and lose hot context that finishing-now would spend cheaply.

- **Intent hint given** (`/wrapup picking up next-set-bugs`) — evaluate whether THIS session is well-positioned for _that named work_ before doing wrap-up prep.
- **No intent hint** (bare `/wrapup`) — the "next work" is implicit: the thread this session is already on. Ask whether there's genuinely-hot in-flight work where finishing _now_ is materially cheaper than bouncing and re-deriving it cold. This is the honest "don't leave yet — you should keep going here" call. It must clear a **high bar** (see the STAY rule): the standing expectation is that a bare `/wrapup` wraps, so STAY here is the rare exception, not a routine outcome. When it does fire, it's loud on purpose — a `## ↺ STAY HERE` headline, not a buried aside.

Three signals say STAY (read "the intent" as the named intent, or the in-flight thread on a bare wrap):

1. **Files just touched relate to the intent.** Recent edits to `idm/journals.py` and the intent says "fix next_set bugs" — the warm cache is exactly the right cache.
2. **Decisions just made inform the intent.** This session settled tradeoffs that the next chunk would otherwise have to re-derive cold.
3. **Implementation context is hot.** You just shipped slice N of a multi-slice story and the intent is slice N+1 of the same story — fresh-session restart would re-read the same files anyway.

Signals that say BOUNCE (proceed to Phase 3 — this is the common case, especially on a bare wrap):

- **Bare wrap and nothing's genuinely mid-thought** — the session's work is done/committable and there's no hot thread whose cold restart would cost real re-derivation. This is the default; when in doubt on a bare wrap, BOUNCE.
- Intent lives in a different repo, different working directory, or different code surface than this session touched.
- This session is at high context pressure (the `<context-pressure>` reminder fired, or you've been re-reading files).
- Subject is genuinely orthogonal — different story, different layer of the stack, different user goal.

If STAY: skip Phase 3, emit ↺ STAY verdict with the specific signals that fired ("recent commits in `idm/journals.py`," "this session decided <X>"). Let the user override.

### Phase 3: Execute prep (only if Phase 1 found in-flight state)

**Default: just do the writes, then commit and push them.** Routine wrap-prep is mechanical journaling and bookkeeping — DIARY entries, story files, `design/NEXT.md` handoff, queue notes. These are low-judgment, easily edited afterward, and asking-for-OK on each one adds friction without value. Write them directly, then land them — invoking `/wrapup` is the explicit authorization to commit and push the session's work (it overrides the global "never commit unless explicitly asked" default for exactly this skill, because the invocation _is_ the ask). Reserve per-instance confirmation for the genuinely irreversible operations: destructive git ops (force-push, `git reset`, rebase, `rm` of tracked files) and dirty trees you can't confidently classify as complete-vs-WIP.

Standard preps:

- **Decisions not journaled**: write a `DIARY.md` entry directly. Narrative form, why-and-context, latest-first per project convention. No propose-then-OK gate at wrapup time. (Compare with persona-voice journaling like `diary_propose_entry` — that's a different surface where propose-then-curate is the point.)
- **In-flight todos worth not losing** — route by shape:
  - **The next session's pick-up-here handoff** (the "next: X, then Y" you'd otherwise only say in the tl;dr) → **(over)write `design/NEXT.md`** — the canonical, _ephemeral_ session-handoff surface from the design-corpus model (`groot-claude-coord`). Give it a brief current-focus line plus an ordered do-next list (numbered `1.` / `2.` or `- [ ]`), highest-priority first. **Overwrite, don't append** — NEXT.md is "where to pick up _now_", not a growing log (its history lives in `DIARY.md`). This is the **producer half** of the handoff: `/sup` and `/next` read `design/NEXT.md` and lead with its do-next list _in order_ (via `backlog-scan`'s `NEXT.md handoff` surface + [`backlog-ranking.md`](../next/backlog-ranking.md) §3 rule 0), so what you write here is what the next session picks up — surviving the `/clear` that discards the tl;dr and scrollback. Writing it is the whole point of `/wrapup` deferring work. Use `design/NEXT.md` (canonical path) even if the project currently has a root `NEXT.md` — and flag the legacy location for cleanup if so.
  - **Larger or design-open work** → `design/stories/drafts/`; **loose backlog with no next-session ordering** → `## Open` in `TODO.md`; **dev-inbox projects** → a dev-inbox entry. Default to the lightest surface that won't get forgotten.
- **New stories surfaced this session**: file in `design/stories/ready/` (design baked) or `design/stories/drafts/` (design still open). Same just-write principle — story files are durable but easily edited.
- **Open TaskList items that are actually done**: mark them completed. Items genuinely incomplete: leave open + flag in the verdict.
- **Uncommitted changes that should land**: usually already handled by Phase 1.5's automatic `/cpush` sweep. If something was left uncommitted (e.g. `/cpush` skipped it), draft atomic commit(s) and run `/cpush` directly — no OK gate, per the auto-commit-and-push default above. If the project has pre-commit hooks, let `/cpush` run them; if a hook fails, surface the failure rather than forcing past it.
- **Uncommitted changes that are mid-experiment**: surface — propose either committing-as-WIP, stashing with a descriptive name, or leaving as-is with a note. Default suggestion is "leave as-is, but note it" — most mid-experiment dirt should not become a commit. This is the carve-out the auto-commit default explicitly excludes.

After the Phase 3 writes are done, land them too: batch the resulting changes into atomic commit(s) and push via `/cpush` directly — no separate OK. The only things that still pause for you are the carve-outs (destructive ops, ambiguous dirty trees).

### Phase 4: Session recap

Render a short bulleted summary of what this session accomplished, immediately above the verdict block. **Always emit** — even on trivial sessions. This is for the reader who walks back to this terminal cold ("wait, what the hell was I doing in this window two days ago?"); the verdict alone doesn't answer that, and scrollback above the verdict won't either if the session was long.

Format:

```
**Session recap:**
- 3–6 short bullets, one concrete action per bullet (for trivial sessions, 1–2 is fine — don't pad)
- Commits land first, with explicit repo names: e.g., `Committed `58c2d81` to dgroo/dotfiles and pushed`
- Then decisions / drafts / discussed-but-not-shipped items
- If session covered multiple distinct topics, focus on the most recent — that's what the cold reader is asking
```

**Source: conversation scrollback** (what the assistant actually did this session), augmented by commits if they happened. Not `git log` alone — commits miss decisions reached, drafts started, and discussions that didn't ship, which are exactly the things you don't remember. If working context has been compressed/auto-summarized and earlier work isn't visible, emit one bullet `_Earlier work in this session not in working context._` rather than fabricating.

If Phase 1's independent-review check (step 6) produced a nudge line, surface it on its own line **between the recap and the verdict block** — it's non-blocking context, never part of the ✅/⏸/↺ judgment. One line, verbatim from the helper; don't expand on it (it's a "maybe, sometime" reminder Derek may skip).

The recap sits **above** the verdict; the verdict still gets to be the final emission per Phase 5's load-bearing-UI rule.

### Phase 5: Verdict

Emit one of the three verdicts as a **visible markdown headline in your assistant text** (not a Bash `printf` — see the note below), so it lands as the unmissable last thing the user reads:

```markdown
## ✅ READY TO WRAP — safe to bounce. A fresh session with /sup will pick up cleanly.
```
```markdown
## ⏸ NOT YET — <N> item(s) need attention first.
```
(Then list the items.)
```markdown
## ↺ STAY HERE — this session has <specific signals> in cache for <intent, or "the current thread">; bouncing discards real context. Recommend continuing.
```

Render it as an actual `##` heading in your response (the emoji carries the colour-free signal — ✅ / ⏸ / ↺ — per the color-blind-safe rule), **not** inside a code fence. For READY and STAY, that's the whole emission — no extra prose after it, **except** the conditional Phase 6 handoff prompt (cross-machine / complex-bootstrap only), which is the one artifact permitted to follow the verdict. For WAIT, list the items below the heading with explicit next steps the user can act on.

> **Why markdown, not ANSI `printf`.** This verdict used to be a bright-yellow ANSI block emitted via `printf`. That broke: current Claude Code builds collapse successful Bash stdout behind a folded "Ran 1 shell command", so the load-bearing verdict became invisible — produced but hidden. Assistant-text markdown can't be collapsed like a tool result, so it's robustly visible across CC versions. Don't reintroduce the `printf` form. (Fixed 2026-06-25; same fix applied to `/sup`.)

**The verdict heading is a final-state signal, never a preview.** The user reads it and bounces. Treat it as load-bearing UI: it appears once, at the very end, only after all wrap-prep writes have landed, the Phase 4 recap has rendered, and any commit-OK has been granted and executed. Do NOT render a verdict (or anything shaped like one) before that point. If you find yourself wanting to surface "once X is done, the verdict will be ✅" — stop. Do X. Then emit the verdict. The heading's job is to be unambiguous; conditional/preview/hypothetical verdicts are the bug this rule prevents.

### Phase 6: Cross-session handoff prompt (conditional)

Fires **only** when the handoff crosses an explicit boundary that `design/NEXT.md` + a fresh `/sup` won't smoothly bridge on their own:

- **Different machine** — the intent hint or conversation names another host ("migrating to Roci", "I'll pick this up on Serenity").
- **Non-obvious session bootstrap** — resuming needs mechanical steps a fresh `/sup` won't surface: a dependency install (lockfile changed this session), a specific checkout / worktree, a cross-repo "stay out of X" constraint, or a service left running on a particular host.

When neither fires — the common same-machine, next-session case — **emit nothing**. `design/NEXT.md` + `/sup` already carry the handoff; a bootstrap prompt there is noise, and this skill's default is to stay quiet.

When it fires, emit a **fenced, paste-ready prompt** the user can hand straight to the new session. It's a thin _session-bootstrap_ wrapper, **not** a second copy of the state:

- Name the host + checkout to start in.
- List the mechanical bootstrap: `git pull`, `bun install` / equivalent **iff** deps changed this session, a health check (`make smoke` / project equivalent).
- **Point at `design/NEXT.md` (and `/sup`)** for the actual resume state — don't restate it. The durable half already lives there; duplicating it just invites drift.
- Carry only the cross-cutting constraints `/sup` won't surface on its own: stay in repo X, don't touch repo Y, a service is running on host Z.

Keep it **ephemeral — print it, don't write a file.** `design/NEXT.md` is the durable handoff; a filed prompt would drift against it. Offer to save only if the user asks.

**This is the one emission permitted after the verdict.** The prompt is the actionable artifact the cross-machine verdict points at, so it follows the verdict heading (Action-at-bottom) — the single exception to Phase 5's "verdict is the last thing" rule, and only for this conditional prompt. Have the verdict line reference it ("…pick up on <host> with the prompt below").

## Output expectations

- **One verdict per invocation.** Don't hedge across two verdicts ("READY-ish but maybe STAY"). Pick the one that fits and explain.
- **The verdict heading is the headline.** Anything above it is inventory + recap; the heading itself is the answer.
- **Brief above the heading.** If READY, no prose beyond the Session recap. If WAIT, items list below. If STAY, the rationale is _inside_ the heading line; expand only if the user asks. The Phase 4 Session recap always renders regardless of verdict.
- **Don't repeat /sup's content.** `/wrapup` is not a sitrep. Don't list the backlog, don't recommend a pick, don't reproduce git status. That's `/sup`'s job after the bounce. The Session recap is the one exception — it's the "what was I doing" signal both skills emit.

## Companion to /sup

The READY verdict's contract: after the user bounces and runs `/sup` in a fresh session, the new session has everything it needs. That's why journal-completeness, `NEXT.md` currency, and "uncommitted decisions" matter as inventory items — they're the things `/sup` can't recover if `/wrapup` didn't catch them first.

If you're tempted to skip the journal-decisions check because "the diff captures it" — don't. The commit message captures _what_; DIARY entries capture _why_. A fresh session reads `git log` and sees the _what_; only the DIARY tells it the _why_.

## Rules

- **Always emit a verdict.** Silence is the bug this skill exists to fix.
- **Always emit the Session recap** (Phase 4) above the verdict, even on trivial sessions. The "what was I doing in this terminal" failure mode is what the recap exists to fix; making it conditional defeats that.
- **Verdict is final state, not preview.** The ✅ / ⏸ / ↺ heading is the user's bounce signal — they read it, they leave. Never render a verdict heading (or anything that resembles one) as a hypothetical, conditional, or "once X is done" preview. Emit only after all prep is complete. See Phase 5 for the longer rationale.
- **Auto-commit and push complete work.** Invoking `/wrapup` is the explicit authorization to land the session's committable changes — commit and push them directly via `/cpush`, no per-write or per-commit OK. This overrides the global "never commit unless explicitly asked" default _for this skill only_, because the invocation is the ask. **Still ask per-instance for the carve-outs:** destructive git ops (force-push, `git reset`, rebase, `rm` of tracked files) per the global Safety rule, and dirty trees you can't confidently classify as complete (mid-experiment WIP is sometimes intentional — surface it, don't commit it).
- **DIARY entries / story files / `design/NEXT.md` / queue notes: just write them.** Routine wrap-prep writes are mechanical journaling, not judgment-heavy decisions. The user edits afterward if framing's off. Propose-then-OK adds friction without judgment value at this stage. (For persona-voice journaling like `diary_propose_entry` — propose-then-curate still applies; that's a different surface where the propose step is the point.)
- **STAY is high-confidence only — higher-bar still on a bare wrap.** If you're not sure the cache actually helps the next step (named intent _or_ the in-flight thread), lean READY and let the user push back. Never manufacture a STAY out of "well, you've been working here" — that's the exact failure mode. On a bare `/wrapup` (no intent), only raise STAY when finishing _now_ is materially cheaper than a cold restart _and_ the work is genuinely mid-thought; the standing default is that a bare wrap wraps. When STAY does fire, it's the loud `## ↺ STAY HERE` headline — the visible "you should stick around" call, never a silent slide into READY.
- **Cross-session handoff prompt is conditional and ephemeral.** Only on an explicit machine boundary or non-obvious bootstrap (Phase 6); print it, never file it; point it at `design/NEXT.md` rather than restating the state. Same-machine next-session handoffs emit nothing — the default is silence.
- **One sentence per inventory item.** This is a glance, not a report.

## Help

When invoked as `/wrapup help`, print the following block verbatim:

```
wrapup — Actively assess whether this session is safe to end; prep if needed; give a definitive verdict.

Usage: /wrapup [?|!|?!] [<optional intent for next work>]

Arguments:
  (none)            Default wrap: do routine prep + commits, then verdict.
                    Ask only on carve-outs (destructive ops, ambiguous dirt).
                    Still raises a loud STAY if there's a strong reason to
                    keep going in this session (high-bar, rare).
  <intent>          Same + judge whether THIS session is the right place
                    for that intent. Sharpens the STAY call against it.

Modifiers (decisiveness dial — leading, before any intent):
  ?                 Advise only — inventory + verdict, makes NO changes.
  ?!                Gated wrap — wrap iff READY; if WAIT/STAY, stop and tell you.
  !                 Autonomous wrap — resolve everything you can, minimize WAIT;
                    only pause for irreversible carve-outs (destructive git ops
                    still confirm per the Safety rule; ! does not override it).

Verdicts:
  ✅ READY          Clean handoff state. Bounce + /sup will work.
  ⏸ WAIT            N items need attention first. List + prep proposals follow.
  ↺ STAY            Real in-flight context here (named intent or current
                    thread). Recommend staying. High-bar, rare.

Handoff prompt (conditional):
  On a cross-machine or non-obvious-bootstrap handoff, also prints a
  paste-ready bootstrap prompt for the next session — ephemeral (never
  filed), points at design/NEXT.md rather than restating it. Same-machine
  next-session handoffs print nothing.

Verbs:
  help              Show this message.

Companion to /sup (descriptive sitrep). See SKILL.md for full reference.
```
