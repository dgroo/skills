---
name: ponder
description: Use when Derek declares a thinking/research task — "do a design pass on X", "I was thinking about X on my hike", "thinking task", "let's think through X", "we may or may not build this", "/ponder <topic>". Declares design-thinking mode - the deliverable is a design artifact (drafts story with named open decisions), NOT code. Explore the repo, recover in-repo prior art, think in options, write the story, stop. Building anything is gated behind Derek's explicit go. NOT for one-line spark capture (/idea), web-research reports (/deep-research), or specs headed straight to implementation (gstack /spec).
argument-hint: "[<topic> | handoff | help]"
---

# Ponder — a thinking task, not (yet) a building task

Derek starts a lot of threads whose honest status is "we may or may not turn this into real work." This skill makes that a declared mode with a contract, instead of an ad-hoc vibe that implementation slowly leaks into.

**The mode contract.** While a ponder is active:

- The deliverable is a **design artifact with named open decisions** — not code, not config, not scaffolding.
- Writes are confined to the project's design corpus (`design/stories/drafts/` when the project has it; `design/notes/` otherwise; ask if neither exists).
- Turning any part of the thinking into real work requires Derek's **explicit go** — a recommendation in the artifact is not a go.
- If an implementation itch appears mid-ponder ("this would only take a minute"), it goes in the story as a first-increment candidate. It does not get built.

## Routing

| Invocation | Behavior |
|---|---|
| `/ponder <topic>` | Run the full flow on the topic (Derek's message often *is* the topic — quote it back in the frame) |
| `/ponder` | Ask one question: "What's the topic, and is there a leading example or constraint I should anchor on?" |
| `/ponder handoff` | Skip to Phase 5: package the current thread's thinking as a handoff prompt for another session/repo |
| `/ponder help` | Print usage (see Help section) |

## The flow

**1. Frame.** Restate the question in one paragraph, in your own words, and get the boundaries down: what's in scope, what Derek explicitly flagged as orthogonal (bound it in one line and stop), and which decisions look like one-way doors vs. two-way. If the framing is wrong, this is the cheap place to find out — but don't interview; Derek is often away. Lead with the frame and keep moving.

**2. Explore.** In-repo prior art first — this is Chesterton's-fence recovery, not a formality: grep `design/`, `DIARY.md`, stories in all three trust tiers, and the code itself for places the question already has a partial answer (a flag, a tenet, a deferred decision). Check sibling repos/global setup when the topic smells cross-project. Delegate read-heavy sweeps to Explore subagents; keep conclusions, not file dumps. External research only if the question genuinely turns on outside facts — and if it needs more than a quick check, say so and recommend `/deep-research` rather than doing a shallow imitation of it.

**3. Think.** Options with tradeoffs, a recommendation with reasons, and — the part that makes a ponder useful later — the *rejected* options with why, so the decision doesn't get re-litigated from scratch in three months. Name the principles doing the work (fail-closed, mechanical-copy-of-the-rule, lens-not-vault, whatever the project's load-bearing ideas are).

**4. Write the artifact.** A drafts story (or note), with: provenance stamp, the frame, prior art found, the design itself, **an `## Open decisions` section listing every call that is Derek's**, first-increment candidates (what we'd build first *if* he says go), and non-goals. Commit it as its own atomic `docs(design)` commit and push. This is the one thing a ponder always produces — a thread that evaporates on session end was a chat, not a ponder.

**5. Route and stop.** End the turn with: the open decisions as a compact list (recommendation marked), a link to the artifact (`grootos-link` where available), and — when part of the work belongs in another repo or a fresh session — a **paste-ready handoff prompt** that names the artifact path and scopes what the receiving session should and shouldn't do. Then stop. No "shall I start on increment 1?" — the go is Derek's to give unprompted.

## Guardrails

- **No writes outside the design corpus.** A ponder that edited `lib/` wasn't a ponder.
- **Bound the orthogonal.** When Derek flags an adjacent axis as out of scope, give it one bounding sentence in the artifact (how the two compose) and go no further — the bounding line prevents scope-creep arguments later.
- **Promotion is a separate act.** After Derek answers the open decisions, the story moves `drafts/ → ready/` with decisions recorded inline — that edit is in-bounds; the building it unlocks still is not, until he says go.
- **Escalate honestly.** If mid-ponder the topic turns out to need real external evidence, a spike, or another repo's context, say which and route — don't fake it with plausible prose.

## Help

When invoked as `/ponder help`, print the following block verbatim:

```
ponder — Declare a thinking/research task: explore, design, write a drafts story, stop before building.

Usage: /ponder [<topic> | handoff | help]

Arguments:
  <topic>           Run the full flow: frame → explore (in-repo prior art
                    first) → think in options → write a drafts story with
                    named open decisions → route and stop.
  (none)            Ask for the topic and any anchoring example/constraint.
  handoff           Package the current thread's thinking as a paste-ready
                    prompt for another session or repo.
  help              Show this message.

Contract:
  Deliverable is a design artifact, never code. Writes confined to the
  design corpus. Building anything waits for Derek's explicit go.

See SKILL.md for full reference.
```

## Related

- **`/idea`** — one-line spark capture; a ponder is what a spark becomes when it earns an hour.
- **`/deep-research`** — web-sourced, cited research reports; a ponder recommends it when the question turns on outside facts.
- **`superpowers:brainstorming`** — interactive requirements interview headed toward building in-session; a ponder is autonomous, artifact-producing, and explicitly may-never-build.
- **`/cleanup-design`** — maintains the corpus ponders write into.
