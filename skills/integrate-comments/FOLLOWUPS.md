# integrate-comments — follow-ups

Skill split out of `/walkthrough iterate` on 2026-05-12. The iterate verb was generic — marker rewrite, review-log, no-fabrication, uncommitted-state hard stop — and walkthrough was carrying it incidentally. This skill is the new home; walkthrough keeps content-generation only.

## S1. Large-iterate UX (batch vs. interactive) — INHERITED FROM WALKTHROUGH

**Original surfacing.** The iDM walkthrough's first iterate pass picked up 22 reviewer comments and made batch decisions on all of them. Several were spec-shaped (substantial rewrites, deferred follow-ups) — the user had to trust the batch synthesis rather than walking through them one at a time.

**What's already addressed.** Preserve-don't-strip (`@<user>:` → `@<user>+seen:` in place) plus the review-log preserves the disposition trail. A user can re-read post-iterate and see which paragraph each comment hung off, alongside the disposition. That narrows the "trust batch synthesis" concern but doesn't eliminate it.

**What's still open.** The batch-vs-interactive choice isn't surfaced. For very large iterates (proposed default threshold N≥10 comments), the skill could offer:

- **Batch** (current default behavior): integrate all comments in one revision.
- **Interactive walk-through**: present each comment with proposed integration, accept/edit/skip per comment.
- **Spec-shaped only interactive**: batch prose-tweak comments; pause on comments that look like spec gaps (heuristic: comment mentions architecture, data model, naming, behavior changes, or starts with "huh — I thought...").

Not yet baked in. Could surface via `AskUserQuestion` when N≥10, defaulting to batch.

## S2. Multi-reviewer attribution — DESIGN OPEN

**Problem.** Username discovery assumes a single distinct `@<word>:` prefix in the doc. Multi-reviewer docs (Derek and Alice both leaving comments on the same draft) currently aren't first-class. The SKILL.md says "process all of them in one pass, attributing dispositions per-reviewer in the review-log" — but the review-log shape doesn't have a Reviewer column.

**Open question.** Add a `Reviewer` column to the per-comment table? Or split the table into per-reviewer sections? First-time multi-reviewer doc would settle this.

## S3. Sibling-skill discovery for follow-ups

**Problem.** The skill says "defer to the content-generator skill's follow-ups verb when one exists — `/walkthrough follow-ups` for walkthroughs." That's fine for walkthroughs but generic markdown (survey drafts, design notes) has no follow-ups verb yet. The integrate-comments review-log captures follow-up candidates, but they have no canonical filing destination.

**When this matters.** First time we iterate on a survey draft (or similar non-walkthrough doc) and need to file follow-ups, we'll feel the gap. May want a generic follow-ups skill, or per-content-type ones.

## Related

- `~/code/claude/skills/skills/walkthrough/SKILL.md` — sibling skill (content generator only after this split)
- `~/code/claude/skills/skills/walkthrough/FOLLOWUPS.md` — earlier follow-ups, some of which (S3 in particular) migrated here.
