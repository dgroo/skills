---
author: claude
priority: medium
---

# /beginners-mind — periodic "fresh eyes" review of the coding setup

## Problem

Derek's coding / Claude Code setup has accumulated meaningful complexity: federated repos (`dgroo/dotfiles`, `dgroo/dot-claude`, `dgroo/skills`, `groot-claude-coord`, `remote-coding-setup`), custom skills, hooks, MCP servers, shell config, terminal stack, gbrain, host pair (Roci + Serenity), per-project conventions. Most of it was decided in-context and is fine, but:

- Some decisions are stale — made when the toolset or workflow was different — and would benefit from a fresh look.
- The CC ecosystem moves fast; new techniques, tools, skills, and patterns appear constantly that Derek isn't tracking systematically.
- Derek has unconscious behavior patterns (re-typing the same prompt, manually doing things a skill would do, re-explaining the same context) that he can't easily see himself.
- Some things in the setup are genuinely novel — worth surfacing both for self-awareness and (eventually, in v2) for sharing with an AI discussion group.

No existing mechanism takes an outsider's perspective on the whole setup. `/skills-review` is scoped to installed skills. `/roci-sitrep` is host-state. gstack's `/retro` is a weekly engineering-output review. Nothing crosses (introspection × behavior × external research) and produces "what would a fresh observer notice and ask?"

## Proposed solution

A new skill `/beginners-mind` that runs roughly monthly and produces a structured report adopting the perspective of an engineer joining Derek's organization. Three input streams converge: introspection (current setup state), behavior (what Derek actually does, observed via CC transcripts, diary, git), and external research (curated corpus of CC / coding-workflow sources, kept current). The skill is stateful — it maintains a corpus, a findings archive, and a recommendation ledger — so each run builds on prior runs.

## Design notes

### Naming

`/beginners-mind` — from "shoshin," the Zen idea of approaching things with the openness of a beginner. Captures the framing: a fresh observer with no investment in why-it's-like-this. Distinct from `/retro` (engineering retro on shipped work) and `/skills-review` (skills only).

### Homes

- **Skill code:** `~/code/claude/skills/skills/beginners-mind/SKILL.md` (per `dgroo/skills` local-skills convention; symlinked into `~/.claude/skills/` via `make install`).
- **Design doc (this file):** `~/code/claude/skills/design/stories/ready/beginners-mind.md`.
- **State:** `~/.claude/beginners-mind/` (versioned via `dgroo/dot-claude`).

### State directory layout

```
~/.claude/beginners-mind/
├── corpus.md              # tiered source list, self-maintained
├── findings/              # per-run findings (JSON; input to next run's diff)
│   └── YYYY-MM-DD.json
├── reports/               # human-readable reports
│   └── YYYY-MM-DD.md
├── ledger.md              # recommendation history: pending/accepted/rejected/deferred
└── last-run.json          # timestamp, token estimate, duration (for guardrail)
```

### Invocation

- `/beginners-mind` — full run.
- `/beginners-mind --force` — bypass interval guardrail.
- `/beginners-mind --dry-run` — plan only; no fetches, no writes.
- `/beginners-mind --bootstrap` — re-seed corpus (also auto-fires if `corpus.md` missing).
- `/beginners-mind apply <ID>` or `do recommended` — act on prior report's action items. Mirrors `/skills-review`'s "do recommended" pattern. IDs are `R1`, `R2`, … from the recommendations section.

### Run flow

**Phase 0 — Cost guardrail.** Read `last-run.json`. If `days-since-last < 21`, AskUserQuestion: "Last run was N days ago, ~X tokens. Run anyway?" with options [proceed / defer / abort]. Bypassable with `--force`.

**Phase 1 — Introspect (parallel subagents).**

- Skills catalog: delegate to `/skills-review research` logic; do not duplicate it.
- `~/.claude/` config diff since last run (settings, hooks, `rules/`, `CLAUDE.md`).
- Dotfiles diff (bare repo at `$HOME/.dotfiles.git`).
- Federation repo activity (`git log` + summary of changed surfaces) across all five federated repos.
- Tooling snapshot: `brew list`, `pipx list`, MCP servers, gbrain config.

**Phase 2 — Behavioral observation (parallel subagents).**

- Read CC transcripts under `~/.claude/projects/*/` since last run. Subagent summarizes: repeated prompts, common frustrations, things Derek re-explains, prompts he edits/retries, things he does manually that a skill or alias would simplify. Returns a short summary (not raw transcripts) to keep main context clean.
- Read diary shards (`diary/*.md`) across federated repos since last run. Surface themes and recurring frictions.
- Walk git commit activity for behavioral trends ("seven sessions touched shell config this month", "no commits to skills repo despite many CC sessions").

**Phase 3 — External research (parallel subagents per source).** Walk `corpus.md`; for each source, fetch new content since last run. Use ETag / last-modified / since-param where possible to minimize fetch volume. Provenance recorded per finding (URL + date + excerpt). Synthesis biased toward "new since last run."

**Phase 4 — Synthesize.** Cross-reference introspection × behavior × research. Four report sections:

1. **Recommendations** — concrete proposals. Each cites motivation (which observation triggered it), source (which corpus item supports it, if any), effort estimate (per global "1/1000 calibration"), action ID for later `apply`.
2. **Behavioral observations** — "you keep doing X" patterns. Gentle, with proposed remediation. This is the unconscious-pattern surface.
3. **Cool things callout** — patterns visible in Derek's setup that don't appear in the external corpus. Candidates for sharing.
4. **"Why is it like this?"** — places where the setup has accumulated complexity a newcomer would question. Each item gets a short answer the synthesis can attempt from diary / git blame / commit messages, or a flagged unknown.

**Phase 5 — Output + state update.**

- Write report to `~/.claude/beginners-mind/reports/YYYY-MM-DD.md`.
- Append findings to `findings/YYYY-MM-DD.json`.
- Update `ledger.md`: new recommendations as `pending`. Existing unresolved recs that resurface get a `still-relevant` mark.
- Propose `corpus.md` adds (new sources cited this run that aren't in corpus yet) and prunes (sources that produced zero usable signal across last 3 runs).
- Surface report path + one-line summary to terminal.

### Bootstrap (first-run only)

No `corpus.md` exists. Flow:

1. **Ask Derek first.** "Before I do meta-research, what sources do you already trust for CC / coding-workflow signal? Anything that comes to mind — blogs, GitHub users, Substacks, Discord channels, podcasts, conference series, individual people." Capture the seed list.
2. **Meta-research pass** via WebSearch / WebFetch: identify additional trusted CC writers, Substacks, GitHub users, conference talks, podcasts.
3. **Present combined candidate list** (Derek-seeded + LLM-discovered), each with a one-line "why this," for Derek's approval / rejection / edit.
4. **Write approved sources** to `corpus.md`, tagged by tier.

The Derek-first step is intentional: leverages existing trust before LLM discovery, and gives Derek visibility into what assumptions get baked in.

### Corpus tiers

- **Tier 0 (always pull, high signal):** Anthropic changelog, Claude Code release notes, `anthropics/claude-cookbook` recent commits, Anthropic engineering blog.
- **Tier 1 (curated individuals):** Substacks, RSS feeds, specific GitHub users' activity. Seeded at bootstrap; grown over time via run-by-run proposals.
- **Tier 2 (community surfaces, lower-trust):** HN posts tagged Claude/Anthropic, `/r/ClaudeAI` top-monthly. Filtered hard.
- **Tier 3 (peer reports):** AI discussion group's report archive. v2 only.

### Scope (introspection surface)

- **In:** `~/.claude/` config, installed skills (all sources), dotfiles, shell config, federation repos, `~/bin/`, gbrain config, terminal stack, top-level inventory of `~/code/`.
- **Out:** deep per-project analysis (covered by individual project skills), Roci / Serenity hardware specifics (covered by `/roci-sitrep`).

### Cost guardrail details

- `last-run.json` tracks timestamp, estimated token usage, duration.
- Default minimum interval: 21 days. Aligned with the "roughly monthly" target with some slop.
- Phase 0 guardrail asks before proceeding if interval hasn't elapsed.
- `--force` bypasses.
- Out of scope for v1: SessionStart hook that nudges on "you haven't run in a while" — revisit if needed.

### Federation cross-repo commits

Skill state lives in `dgroo/dot-claude` (via `~/.claude/beginners-mind/`). Skill code lives in `dgroo/skills`. Report-driven action items, if accepted, edit their respective repos. Per the `remote-coding-setup` CLAUDE.md hub-use-case rule, the skill surfaces which repo each commit lands in before committing.

### Out of scope (v1)

- Discussion-group exchange (produce shareable / consume others' reports) → v2 once a couple runs reveal what's actually worth sharing.
- Background watcher (continuous polling between runs) → only if monthly corpus refresh becomes the bottleneck.
- Auto-applying recommendations → always user-driven via `apply <ID>`; never silent.

## Acceptance criteria

- [ ] Skill code at `~/code/claude/skills/skills/beginners-mind/SKILL.md`, symlinked via `make install`.
- [ ] State directory `~/.claude/beginners-mind/` created with `corpus.md`, `findings/`, `reports/`, `ledger.md`, `last-run.json`.
- [ ] Phase 0 guardrail blocks runs <21 days apart unless `--force`.
- [ ] Bootstrap flow asks Derek for trusted sources first, then does meta-research, then presents combined list for approval.
- [ ] Full run produces a report with all four sections (Recommendations, Behavioral observations, Cool things, "Why is it like this?").
- [ ] Each recommendation includes motivation, source citation (if any), effort estimate, action ID.
- [ ] `apply <ID>` mode acts on a recommendation from the latest report.
- [ ] Ledger updates persist across runs (recs marked `pending` / `accepted` / `rejected` / `deferred` / `still-relevant`).
- [ ] Subagents used for transcript reading, external research, and federation introspection (for parallelism + main-context isolation).
- [ ] Each cross-repo commit surfaces its target repo before being made.

## Open questions

- Should the bootstrap meta-research pass also propose a CC discussion-group archive location (shared GitHub repo, Notion, Substack), even though v1 doesn't act on it? Could surface for Derek to think about ahead of v2.
- Threshold for "zero usable signal across N runs" before auto-proposing corpus prune. N=3 feels right; could be a config knob in `corpus.md` header.
- Transcript subsampling strategy if token budget is exceeded — by recency, by project, by session length? Defer until actual run cost is observed.

## Related

- `~/code/claude/skills/skills/skills-review/SKILL.md` — adjacent skill; Phase 1 delegates to its `research` mode.
- `~/code/0.llm/remote-coding-setup/CLAUDE.md` — federation context, hub-use-case rule, design placement rule.
- `~/.claude/CLAUDE.md` — global conventions; effort estimates inherit the "1/1000 calibration" rule.
- gstack `/retro` — engineering retro on shipped work; different surface, name nearby.
- gstack `/skills-review` — installed-skills audit; subset of this skill's introspection surface.
