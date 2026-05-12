# walkthrough — follow-ups

Originally surfaced 2026-05-11 from dogfooding against iDM. Updated 2026-05-12 after a cross-session handoff captured decisions from Derek's iDM session about observed iterate behavior; decisions 1–7 from that handoff landed directly in `SKILL.md` (see git log for that revision).

## S1. Username discovery fallback — RESOLVED (2026-05-12)

**Problem.** Skill spec'd `<!-- @<username>: -->` with username defaulting to `git config user.name`. On Derek's machine that returns `iamgroot`; he annotates with `@derek` (his first name). The grep missed.

**Resolution.** SKILL.md Iterate section now defines a cascade: scan the doc first for any `@<word>:` markers and use the most common one; fall back to `git config user.name` → `user.email` local-part → `$USER` → ask. The "scan the doc first" step handles the actual case because the doc is authoritative for whoever marked it up.

## S2. v0.x vs v-infinity scope question — RESOLVED (2026-05-12)

**Problem.** When the walkthrough describes an actively-developing project, there's a real ambiguity: is the narrative describing the system *as currently shipping* or *as fully designed*? The iDM dogfood surfaced this exactly — Derek's first comment was a meta-question about which framing to use, and the answer changed the document's tone.

**Resolution.** SKILL.md Draft section now defaults to **v-infinity-with-progression-notes** for actively-developing projects: describe the app as it would look when "done as currently conceived," with a progression note at the top. No scope-time question by default; override only on explicit user request for a different framing.

## S3. Large iterate UX (batch vs. interactive) — PARTIALLY ADDRESSED (2026-05-12)

**Original problem.** The iDM iterate pass picked up 22 reviewer comments and made batch decisions on all of them. Several were spec-shaped (substantial rewrites, deferred follow-ups) — the user had to trust the batch synthesis rather than walking through them one at a time.

**What's addressed.** The 2026-05-12 handoff added preserve-don't-strip iterate (`@<user>:` → `@<user>+seen:` in place) and a separate `clean-comments` verb. That means iterate is no longer destructive of the original comment context — a user can re-read the doc post-iterate and see exactly which paragraphs each comment hung off, alongside the disposition in the review-log. That narrows the "trust batch synthesis" concern.

**What's still open.** The batch-vs-interactive walk-through choice itself isn't surfaced. For very large iterates (proposed default threshold N≥10 comments), the skill could still offer:

- **Batch** (current default behavior): integrate all comments in one revision.
- **Interactive walk-through**: present each comment with proposed integration, accept/edit/skip per comment.
- **Spec-shaped only interactive**: batch prose-tweak comments; pause on comments that look like spec gaps (LLM heuristic: comment mentions architecture, data model, naming, behavior changes, or starts with "huh — I thought...").

Not yet baked in. Could surface via `AskUserQuestion` when N≥10, defaulting to batch.

## Related

- `~/code/iDM/design/notes/2026-05-11-narrative-assistGM-human-review-log.md` — original surfacing
- `SKILL.md` — the skill these improvements target
- 2026-05-12 cross-session handoff (in-conversation, not filed as an artifact) — source of decisions 1–7 that landed in SKILL.md
