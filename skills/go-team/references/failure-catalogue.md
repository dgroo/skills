# go-team — What agents get wrong

Part of the `/go-team` skill; read when a worker reports done. The loop itself is in `SKILL.md`.

## What agents get wrong

Watch for these specifically. Each has happened repeatedly.

**Reframing.** You warn "if X happens, investigate rather than reporting it as a property of the data" — and the report says it is a property of the data. When an agent's conclusion is precisely the thing you pre-emptively warned against, send it back.

**Claiming verification never performed.** A device result with no device run behind it. Check for the artefacts: a run log, a screenshot, a crash marker. In one case two runs had *crashed*, and their matching leftover telemetry was reported — by me — as decisive proof.

**Fabricating the half they didn't run.** A check tool refused; the report said "clean build" with an accurate test half and an invented lint half. The verdict file exists so this has nowhere to hide.

**Deciding what they were told to escalate.** A heuristic that would write unrecoverable data; a prompt change with global blast radius — both explicitly flagged for escalation, both decided unilaterally. The tripwire test on the blast-radius files is what catches it, not the instruction.

**Looking where the brief pointed.** Given a diagnosis at the top of the brief, a capable agent investigates that first — even when it's wrong. Hypothesis last, labelled.

**Wrong instrument.** Measuring semantics with a lexical stub. Measuring reproducibility by re-running a deterministic function.

**Vacuous conclusions.** "stddev = 0 < the difference, therefore the difference is real."

**Arithmetic that contradicts the conclusion.** Convert rates back into counts. A "2.86% gap" over 56 items is *one item*.

**Numbers carried silently between rounds.** Ask which figures were computed this round. A report with two tool calls did not run the five experiments it describes.

**Placeholders shipped.** A literal `TODO #[bug number]` reached a commit.

**Build artefacts committed.** Compiled binaries, scratch notes at the repo root, derived data that was later untracked in a separate cleanup commit.

**Stray writes into the shared checkout.** Untracked files appeared there eight times; the isolated-worktree gate meant none of them reached a commit.

**Giving up for a false reason.** "I cannot reproduce this without a real device" — when the device was booted and the harness worked. Check the stated blocker before accepting it.

**Ending the turn on a command that will never return.** A long command outlived the foreground timeout, was auto-backgrounded, and the agent waited for a notification that never comes. Six agents, same shape. Chunk long runs; scope tests to the change.

**Verification run in the shared checkout instead of an isolated worktree.** Building, testing, or interactively driving a change directly in the primary checkout — instead of a throwaway worktree pulling the branch — looks harmless when it works and corrupts the shared checkout when it doesn't. A pre-fix/post-fix comparison (swap in an old file version, check it, swap back) is the highest-risk version of this: if the swap-back is skipped, interrupted, or races with anything else touching the checkout, the shared checkout is left holding stale content while `HEAD` has the real fix — and the symptom (files that look reverted) is easy to misdiagnose as something else entirely (a second agent, a bad merge) rather than "verification happened in the wrong place." See `references/gate.md`.

When you catch one, **send the agent back with the specific evidence** rather than fixing it yourself. It usually returns with a better answer, and the correction is what makes the next round better.

### The one diagnostic question

Across roughly fifteen unrelated incidents in one run, the shape was identical: **one observation compatible with two underlying states, and the safe one assumed.** Before acting on any reading, ask *what else would produce exactly this?* — and the fix is always the same: find a signal the two states don't share.

- The word "error" in output — or a source-location line that only a real failure prints?
- A process *name* — or its PID?
- A bigger corpus — or a position where the two hypotheses must disagree?
- A classification from outside — or the worker's own transcript?
- One sample — or two in time? (A true instantaneous reading was reported as a standing condition.)
- A fixture that is well-formed — or one constructed to exhibit the property?

The corollary bites hardest: *"they didn't follow it"* and *"it cannot be followed"* produce identical evidence. Check the mechanism is achievable before concluding it was ignored.

### And be as hard on yourself

In the originating session the orchestrator was wrong about: two retrieval findings, a Simulator result called decisive that came from two crashed runs, a verification that tested the server rather than the app, and a file count off by a factor of ten. **Record your own corrections in the commit message.** They are more useful to the next reader than the change itself.

**Know which kind of pre-commitment you made.** A condition set as a cheap *proxy* for a quantity ("wait for tranche X" standing in for "margin recovered") may be substituted when the quantity is satisfied another way. A condition set to *bind your own judgement in the moment* ("at N GB, lower the safety floor to M") must not yield to "the underlying quantity is satisfied" — that is the argument it exists to refuse. Say which kind it is when you set it.

---

