# helping-hands — follow-ups

Surfaced 2026-05-12 from RED/dogfood against `~/code/iDM/design/helping-hands/` (5 open items, 3 closed). Items below are skill-level improvements that didn't land in the initial SKILL.md; each came up in the first real run.

Items applied directly to SKILL.md from the same dogfood (not listed here): cheap-filter for `all`, NEXT.md trust-direction inversion, tool-availability gate for "already-LLM-resolvable," extend-vs-closure approval reconciliation, AskUserQuestion-as-default tightening, slug-ambiguity clarification.

## S1. Sibling-synergy heuristic is currently decorative

**Problem.** The Validate phase tells the model to detect "are 2+ open items obviously co-batchable" but gives no signal for "obvious." In the iDM dogfood, `meta-metagm-survey` + `survey-bank-research` were genuinely co-batchable (same external sources: Colville, Shea, Monte Cook; same user trip; both feed `surveys-and-feedback-loop.md`) but the dogfood-run model surfaced them as independent rows because it had no rule to follow.

**Proposed heuristic** (needs another dogfood to validate):

Two open items are co-batchable when *any* of:
- They cite a shared *external* source (same blog, same book, same site to visit).
- They share a downstream story / spec file in their `## Why`.
- They share a single user-side dependency (same wifi trip, same paid signup, same person to ping).
- One item's "When you're done" output would naturally include the other's deliverable.

If 2+ items match: surface as a co-batch suggestion in the `all` table — a sub-row or annotation, not a separate bucket. Skill should still let the user pick them one-at-a-time; the synergy is a routing hint, not a forced grouping.

## S2. Readiness table needs a "what does this unblock now" signal

**Problem.** In iDM, `foundry-mcp-setup` and `rpg-folder-examination` are both technically `blocked-on-user`, but they're not equivalent: `foundry-mcp-setup` is parked relative to current focus (Slice 4/Assistant v0.1 per NEXT.md), while `rpg-folder-examination` would sharpen work the user is *actively* doing (M12 data model in `assistant-mode-first.md`). Surfacing them in the same row weight is wrong prioritization.

**Proposed addition.** Either a "current-focus signal" column in the `all` table (✓ / — / unknown), or a sub-bucket split: `blocked-on-user (current-focus)` vs `blocked-on-user (parked)`. The signal comes from cross-referencing each item's cited stories/files against NEXT.md's "Current focus" section.

Not yet baked in because the cross-reference logic adds real complexity; worth seeing whether the user actually wants this on a re-run, or whether they'd rather just sort by `priority:` frontmatter.

## S3. Closure should suggest a diary entry when the project has one

**Problem.** iDM's project CLAUDE.md says: *"Maintain `DIARY.md` — add an entry when making significant changes, architectural decisions, or non-obvious tradeoffs."* Closing a helping-hand with a non-trivial `## Decision` is exactly that — and the skill's Closure section currently lists frontmatter + Decision section + follow-ups but doesn't mention the diary.

**Proposed fix.** Closure section should add a project-aware check: if a root-level `DIARY.md` (or convention pointer in CLAUDE.md to a diary file) exists, propose a diary entry alongside the closure edit. Wording: "Diary-worthy? If yes, here's a draft entry…" — surfaced, not silent.

The same logic likely applies for `CHANGELOG.md` in projects that use one. Project-aware closure is its own design pass; this is the seed for it.

## S4. Stale-references finding type is incomplete when refs point into `deprecated/`

**Problem.** The skill says: if a helping-hand cites a file now in `deprecated/`, surface that the path is stale but don't load the deprecated file's contents (per Derek's global rule). That's right for the read-with-permission discipline, but it means the `stale-references` bucket's disposition is incomplete: the skill can say "path moved" but can't say "the move makes the item moot." The user has to either re-grant read permission for the deprecated file or evaluate the staleness themselves.

**Proposed fix.** Add a sub-disposition: `stale-references (deprecated-target)` with the action "ask the user to confirm whether the deprecation makes the item moot — load deprecated file's contents only if they say yes." Distinct from `stale-references (path-moved)` where the ref can just be updated.

## S5. NEXT.md drift as a co-output

**Problem (caught in dogfood).** iDM's `design/NEXT.md` had a "## Open helping-hands items" section listing only 1 of 5 open items. The skill detected the disagreement (per the SKILL.md update) but the natural follow-up — propose updating NEXT.md as a side cleanup — wasn't called out as a first-class output.

**Proposed fix.** When the orient-phase NEXT.md hint disagrees with the directory: stage a NEXT.md cleanup proposal as a separate, optional output of the run. Phrasing: "NEXT.md lists N items; directory has M. Propose this edit to NEXT.md after we're done with the queue work — ok to queue?" Don't fold the edit into the helping-hands flow itself; surface it as a sibling proposal.

This is the same pattern `cleanup-design` uses for dead-link findings — surface, don't act.

## S6. Frontmatter-only filter implementation tip

**Problem.** SKILL.md now says "read frontmatter only" for `all`, but doesn't show *how* cheaply. The dogfood run loaded all 8 files including 3 closed ones to discover status.

**Proposed addition** (small):

```bash
# Open items only — body bytes not loaded
grep -l '^status: open' design/helping-hands/*.md
# Or: include in-progress
grep -lE '^status: (open|in-progress)' design/helping-hands/*.md
```

Worth pasting a one-line example in the `all` flow body so the model has the cheap-filter command ready. Not a SKILL.md correctness issue — just an ergonomics nudge.

## S7. Voice-trigger / alias consideration

**Observation.** The user originally floated `/hhands` as an alias. The skill's description includes "/hhands" as a trigger string, which means the matcher should pick it up via description-search, but no actual alias mechanism exists in the skills system. If `/hhands` becomes the daily shortcut, worth a `voice triggers` line analogous to the gstack skills (e.g., "helping hands", "h-hands"). Not blocking; just an ergonomics question once usage settles.

## Related

- `walkthrough` / `cleanup-design` — sister skills with their own FOLLOWUPS.md; same dogfood-then-refactor cadence.
- `~/code/iDM/design/helping-hands/README.md` — convention source-of-truth (3 rules: pre-exhaust LLM work, artifact as source-of-truth, JIT citation-by-path).
- 2026-05-12 baseline + dogfood subagent reports (in-conversation; not filed as artifacts) — source of the gaps enumerated above.
