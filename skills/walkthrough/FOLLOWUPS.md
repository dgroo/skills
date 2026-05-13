# walkthrough — follow-ups

Originally surfaced 2026-05-11 from dogfooding against a real personal project. Updated 2026-05-12 after a cross-session handoff captured decisions from a follow-up session about observed iterate behavior; decisions 1–7 from that handoff landed directly in `SKILL.md` (see git log for that revision). Later in 2026-05-12, iterate was split out into a separate `/integrate-comments` skill — see that skill's `FOLLOWUPS.md` for iterate-shaped open questions.

## S1. Username discovery fallback — RESOLVED (2026-05-12)

**Problem.** Skill spec'd `<!-- @<username>: -->` with username defaulting to `git config user.name`. In practice that can mismatch how the human signs comments: a developer might have `git config user.name` set to a system handle while they annotate with a different prefix (e.g. their first name). The grep missed.

**Resolution.** SKILL.md Iterate section now defines a cascade: scan the doc first for any `@<word>:` markers and use the most common one; fall back to `git config user.name` → `user.email` local-part → `$USER` → ask. The "scan the doc first" step handles the actual case because the doc is authoritative for whoever marked it up.

## S2. v0.x vs v-infinity scope question — RESOLVED (2026-05-12)

**Problem.** When the walkthrough describes an actively-developing project, there's a real ambiguity: is the narrative describing the system *as currently shipping* or *as fully designed*? The dogfood surfaced this exactly — the first reviewer comment was a meta-question about which framing to use, and the answer changed the document's tone.

**Resolution.** SKILL.md Draft section now defaults to **v-infinity-with-progression-notes** for actively-developing projects: describe the app as it would look when "done as currently conceived," with a progression note at the top. No scope-time question by default; override only on explicit user request for a different framing.

## S3. Large iterate UX (batch vs. interactive) — MIGRATED 2026-05-12

Moved to `../integrate-comments/FOLLOWUPS.md` (as S1) when iterate was split out of this skill. Iterate is no longer walkthrough-specific; the open UX question belongs with the new home.

## Related

- `SKILL.md` — the skill these improvements target
- 2026-05-12 cross-session handoff (in-conversation, not filed as an artifact) — source of decisions 1–7 that landed in SKILL.md
