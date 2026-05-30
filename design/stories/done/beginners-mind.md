---
author: claude
priority: medium
---

# /beginners-mind — fresh-eyes audit for any project

## Problem

Long-lived projects accumulate complexity that's invisible from the inside. Decisions get made in context, work fine, and stay. Conventions calcify. Tools that used to be cutting-edge become assumed background. Unconscious habits — re-typing the same prompt, manually doing things a script would do, re-explaining the same context every session — slip beneath self-awareness. The wider ecosystem moves on, and the project doesn't track that drift systematically.

The problem applies at any scale: a single application repo, a library, a tooling environment, or a federation of interrelated repos (e.g., one engineer's whole coding setup). What's missing is a periodic mechanism that takes an outsider's perspective on the project, surfaces what a fresh observer would notice, and produces actionable findings.

LLMs are structurally bad at this on their own. Their nature is to build context from what they see; by the time they understand the project, they've absorbed its framing and lost the beginner's-mind vantage. The skill has to be designed around that limitation, not in spite of it.

## Proposed solution

A general skill `/beginners-mind` that runs roughly monthly on any project. The skill is _general_ (works on any project) but operates against a _project profile_ artifact — generated on first run via `--init` — that tells the orchestrator what to introspect, where the corpus lives, what behavioral signals to read, and what state location to use. Subsequent runs read the profile and proceed.

The beginner's-mind perspective itself comes from a deliberate architectural choice: the perspective-bearing work is done by a fresh subagent that is _under-briefed on purpose_ — given the code and file tree but not the project's own framing (README, design docs, rationale). It produces _questions_ a beginner would ask, not conclusions. The orchestrator, which does have the full context, then answers those questions. The mismatch between "what a beginner would expect" and "what the docs say" is the report content.

The skill is stateful: it maintains a corpus of external sources, a findings archive, and a recommendation ledger so each run builds on prior runs.

## Design notes

### Naming

`/beginners-mind` — from "shoshin," the Zen idea of approaching things with the openness of a beginner. Captures the framing: a fresh observer with no investment in why-it's-like-this. Distinct from `/retro` (engineering retro on shipped work) and `/skills-review` (skills only).

### Homes

- **Skill code:** `~/code/claude/skills/skills/beginners-mind/SKILL.md` (per `dgroo/skills` local-skills convention; symlinked into `~/.claude/skills/` via `make install`).
- **Design doc (this file):** `~/code/claude/skills/design/stories/ready/beginners-mind.md`.
- **Per-project profile:** location specified inside the profile itself; default `design/beginners-mind.md` if the project uses a `design/` subtree, else `.beginners-mind.md` at root.
- **Per-project state:** location specified by the profile. Default for repos with a `design/` subtree: `design/beginners-mind/state/`. Default for the federation/global use case: `~/.claude/beginners-mind/`.

### The beginner's-mind mechanism (architectural core)

The skill _cannot_ think with beginner's mind directly; it has to delegate that to a subagent whose context is deliberately constrained.

**Three reinforcing constraints on the fresh-observer subagent:**

1. **Subagent isolation.** Its own context window. No conversation history. No accumulated assumptions from the orchestrator session.
2. **Code-first, docs-withheld.** Given the file tree and code at the paths the profile specifies. _Not_ given the project README, CLAUDE.md, design docs, diary, or rationale. A real new hire has the repo and confusion, not the design doc.
3. **Question-first, not conclusion-first.** The subagent's deliverable is a list of questions a beginner would ask, not a list of findings. Examples: "Why two slightly different config files for the same concept?" "What's this `archived/` directory and is it still relevant?" "This function is called from twelve places — why isn't it a class?"

The orchestrator (which has the full context) then answers each question, using the project profile's _background_ section, the README, CLAUDE.md, design docs, diary, and `git blame`. Three outcome buckets fall out naturally:

- **Answered cleanly from docs/history** → project is well-documented; no action.
- **Answered only with awkward backstory** → "Why is it like this?" report material. Candidate for cleanup, or for a comment explaining the constraint.
- **Unanswerable even with full context** → genuine cruft. Top-priority finding.

This pattern also handles the "cool things" callout: questions a beginner would ask that turn out to have surprisingly _good_ answers ("oh, that's actually clever") are the things worth sharing.

### Project profile artifact

The profile is the project's pact with the skill. Generated by `--init`, hand-edited as needed, committed to the repo. It has **two sections with different access rules**:

```markdown
# <Project name> — /beginners-mind profile

## Visible to fresh observer

(structural info — orchestrator AND subagent both see this)

- **Scope:** which dirs/repos/files are in for introspection.
- **Out of scope:** what to ignore (archived dirs, vendored deps, generated code).
- **Behavioral signal sources:** which streams to read (git, CC transcripts at <path>, diary at <path>, issue tracker, PR history).
- **Corpus location:** path to this project's corpus.md.
- **State location:** where findings/reports/ledger live.
- **Cadence:** target interval in days (default 30).
- **Token budget:** per-run hard ceiling (default 500K).
- **What to watch for:** project owner's standing concerns ("I think our test coverage is fragmenting", "we keep re-inventing config patterns").
- **What to skip:** explicit anti-recommendations ("don't suggest more tests; we know", "we are deliberately not using TypeScript").

## Orchestrator only — do not include in fresh-observer subagent context

(rationale, decisions log, "why is it like this" answers)

- Design history pointers (links to design/ docs, key diary entries, ADRs).
- Known-weird-but-intentional choices, with their reason.
- Decisions log: things considered and rejected, with why.
```

The split is enforced by the orchestrator: when it dispatches the fresh-observer subagent, it includes only the _Visible to fresh observer_ section. The _Orchestrator only_ section is consulted later when answering the subagent's questions.

**Why the split matters:** without it, the moment you give the subagent enough to know "what to look at," you've also given it enough to know "what to expect," and the beginner's-mind quality collapses. Structural-where vs. interpretive-why has to stay separated.

### State directory layout

Per-project; location from the profile. Example for a repo with `design/`:

```
<project>/design/beginners-mind/
└── state/
    ├── corpus.md              # tiered source list, self-maintained
    ├── findings/              # per-run findings (compressed; input to next run's diff)
    │   └── YYYY-MM-DD.json
    ├── reports/               # human-readable reports
    │   └── YYYY-MM-DD.md
    ├── ledger.md              # recommendation history
    └── last-run.json          # timestamp, token estimate, duration
```

`findings/` is stored compressed (patterns + file pointers, _not_ transcript excerpts or raw content) so subsequent runs reload cheaply.

### Invocation

- `/beginners-mind` — full run.
- `/beginners-mind --init` — interactive profile setup (also auto-fires if no profile found).
- `/beginners-mind --force` — bypass cadence guardrail.
- `/beginners-mind --dry-run` — show planned phases + estimated token spend; no fetches, no writes.
- `/beginners-mind --skip-research` / `--skip-transcripts` / `--introspect-only` — phase-level cost control for cheap iterative runs.
- `/beginners-mind --bootstrap-corpus` — re-seed the project corpus (also auto-fires if `corpus.md` missing).
- `/beginners-mind apply <ID>` or `do recommended` — act on prior report's action items. IDs are `R1`, `R2`, … from the recommendations section. Mirrors `/skills-review`'s pattern.

### Run flow

**Phase 0 — Cadence guardrail.** Read `last-run.json`. If `days-since-last < profile.cadence_days`, AskUserQuestion: "Last run was N days ago, ~X tokens. Run anyway?" with [proceed / defer / abort]. Bypassable with `--force`.

**Phase 1 — Introspect (parallel subagents).** What lives in the project right now.

- Walk the in-scope paths from the profile.
- Skills/tooling catalog where applicable (delegate to `/skills-review research` if available).
- Diff config-shaped files against previous run.
- Snapshot installed tools relevant to project (e.g., `brew list`, `pipx list`, MCP servers, package manifests).

**Phase 2 — Behavioral observation (parallel subagents).** What the project owner actually does.

- Read transcripts (if profile points to a transcript source) since last run. Subagent summarizes: repeated prompts, common frustrations, re-explanations, manual-then-automated patterns. Returns a short summary, not raw content.
- Read diary entries / notes / journal (if profile points to them) since last run.
- Walk git commit activity in the window for behavioral trends ("seven sessions touched X this month").

**Phase 3 — Fresh-observer questions (isolated subagent).** The architectural core.

- Dispatch a _fresh_ subagent with: (a) the in-scope file tree, (b) the _Visible to fresh observer_ section of the profile, (c) the persona prompt ("you are a senior engineer joining this team on day one; the code is your only briefing"). Deliberately omit README, CLAUDE.md, design docs, the _Orchestrator only_ section.
- Subagent returns a list of questions, each tagged by file/path it relates to.
- Orchestrator answers each question using full context (the withheld docs, _Orchestrator only_ profile section, `git blame`, diary). Bucketing into clean / awkward-history / unanswerable happens here.

**Phase 4 — External research (parallel subagents per source).** What the rest of the world is doing.

- Walk `corpus.md`. For each source, fetch new content since last run, using ETag / last-modified / since-param where possible. Provenance recorded per finding (URL + date + excerpt).
- Synthesis biased toward "new since last run."

**Phase 5 — Synthesize.** Cross-reference introspection × behavior × fresh-observer questions × research. Report has four sections:

1. **Recommendations** — concrete proposals. Each cites motivation (which observation triggered it), source (corpus item if any), effort estimate (per global "1/1000 calibration"), action ID for later `apply`.
2. **Behavioral observations** — "you keep doing X" patterns from Phase 2. Gentle, with proposed remediation. The unconscious-pattern surface.
3. **Cool things callout** — patterns visible in the project that don't appear in the external corpus, plus fresh-observer questions that turned out to have surprisingly good answers. Candidates for sharing.
4. **"Why is it like this?"** — fresh-observer questions whose answers required awkward backstory or were unanswerable.

**Phase 6 — Output + state update.**

- Write report to `reports/YYYY-MM-DD.md`.
- Append findings (compressed) to `findings/YYYY-MM-DD.json`.
- Update `ledger.md`: new recommendations as `pending`. Existing unresolved recs that resurface get a `still-relevant` mark.
- Propose `corpus.md` adds (new sources cited this run) and prunes (sources that produced zero usable signal across last 3 runs).
- Surface report path + one-line summary to terminal.

### Profile initialization (`--init`)

No profile exists. Interactive flow:

1. **Identify the project.** Ask owner: "What is this project, in one paragraph?" Capture identity.
2. **Define scope.** Default = current repo. Ask: "Anything to add (sibling repos, additional dirs) or exclude (`archived/`, generated code, vendored deps)?"
3. **Behavioral signal sources.** Ask: "Which signal streams should the skill watch — git, CC transcripts (specify path glob), diary, issue tracker, PR history? Pick all that apply."
4. **Owner-seeded corpus.** "What sources do you already trust for this project's domain? Anything — blogs, GitHub users, Substacks, podcasts, people, conference series." Capture seed list.
5. **Meta-research pass.** WebSearch / WebFetch to identify additional candidates for the project's domain. Present combined Derek-seeded + LLM-discovered list, each with a one-line "why this," for owner approval.
6. **Standing concerns + anti-recs.** "What do you want me to be especially watchful for? Anything I should explicitly _not_ recommend?"
7. **Token budget + cadence.** Sensible defaults (500K, 30 days); ask if the owner wants different.
8. **Write the profile.** Two sections clearly marked. Write corpus.md and an empty state scaffold. Commit (announcing which repo).

The owner-first step at (4) is intentional: leverages existing trust before LLM discovery, and gives the owner visibility into what assumptions get baked in.

### Corpus tiers

Same tiering applies to all projects; what fills each tier is project-specific.

- **Tier 0 (always pull, authoritative):** primary-source docs / changelogs / official channels for the project's domain.
- **Tier 1 (curated individuals):** trusted bloggers / GitHub users / Substacks / podcasts. Seeded at init; grown via run proposals.
- **Tier 2 (community surfaces, lower-trust):** aggregators (HN, subreddits, mailing lists). Filtered hard.
- **Tier 3 (peer reports):** other practitioners' reports. v2 only.

### Token cost constraints

Token spend is the highest-risk axis of this skill. Constraints, in priority order:

1. **Subagents do all heavy reading; main context only sees summaries.** Architectural — every phase that touches large content (transcripts, code, fetched articles) is subagent-mediated.
2. **Hard per-run token budget**, declared in the profile (default 500K). Each phase estimates cost before running; phases that would exceed get scoped down or skipped with a surfaced warning.
3. **Incremental, not full.** Transcripts / diary / git / external sources all scoped to "since last run" by default. Cumulative state is what makes this cheap — first run is expensive, subsequent runs amortize hard.
4. **ETag / last-modified caching for external fetches.** Don't re-pay for unchanged sources. Cached responses live in `state/cache/`.
5. **Subsampling with disclosure.** If transcripts in window exceed N tokens, sample by recency + project coverage + skip-extremes. Report explicitly notes "subsampled X of Y transcripts."
6. **Phase skip flags** (`--skip-research`, `--skip-transcripts`, `--introspect-only`) for cheap iterative development of the skill itself.
7. **Cost transparency.** Log "estimated: ~X / actual: ~Y" per phase. Builds owner intuition over time about where spend goes.
8. **Findings written compressed.** Patterns + file pointers, not transcript excerpts. Next run reloads pointers, not raw content.
9. **Hard fail-safe.** If actual run cost exceeds budget by 1.5x, skill aborts current phase, writes partial report, surfaces overrun. Better partial than runaway.

### Worked example: federation-wide use case

The skill applies to Derek's federated coding environment by configuring `remote-coding-setup` as the "project," with:

- **Scope:** all five federated repos (`dgroo/dotfiles`, `dgroo/dot-claude`, `dgroo/skills`, `groot-claude-coord`, `remote-coding-setup`), plus `~/.claude/`, plus `~/bin/`.
- **Behavioral signal sources:** CC transcripts under `~/.claude/projects/*/`, diary shards across federated repos with diaries, git activity across all five repos.
- **Corpus:** CC ecosystem (Anthropic changelog, CC release notes, cookbook, trusted CC writers).
- **State location:** `~/.claude/beginners-mind/` (outside any one repo, since no single repo owns the meta-review).
- **Profile location:** `~/code/0.llm/remote-coding-setup/design/beginners-mind.md`.
- **Cross-repo commits:** the skill surfaces which repo each commit lands in, per the `remote-coding-setup` CLAUDE.md hub-use-case rule.

The federation case is the most demanding configuration; if the general skill handles it, simpler projects fall out for free.

### Out of scope (v1)

- **Discussion-group exchange** (produce shareable / consume others' reports) → v2 once a couple runs reveal what's actually worth sharing.
- **Background watcher** (continuous polling between runs) → only if monthly corpus refresh becomes the bottleneck.
- **Auto-applying recommendations** → always user-driven via `apply <ID>`; never silent.
- **SessionStart hook nudging** on "you haven't run in a while" → revisit if cadence slips materially.

## Acceptance criteria

- [ ] Skill code at `~/code/claude/skills/skills/beginners-mind/SKILL.md`, symlinked via `make install`.
- [ ] `--init` flow produces a valid profile with both sections (_Visible to fresh observer_ and _Orchestrator only_).
- [ ] Orchestrator dispatching the fresh-observer subagent includes only the _Visible to fresh observer_ section; _Orchestrator only_ content is never passed to it.
- [ ] State directory scaffolded per profile-specified location, with `corpus.md`, `findings/`, `reports/`, `ledger.md`, `last-run.json`.
- [ ] Cadence guardrail blocks runs inside `profile.cadence_days` unless `--force`.
- [ ] Owner-first bootstrap: skill asks owner for trusted sources before doing meta-research; presents combined list for approval.
- [ ] Full run produces a report with all four sections (Recommendations, Behavioral observations, Cool things, "Why is it like this?").
- [ ] Each recommendation includes motivation, source citation (if any), effort estimate, action ID.
- [ ] `apply <ID>` mode acts on a recommendation from the latest report.
- [ ] Ledger updates persist across runs (recs marked `pending` / `accepted` / `rejected` / `deferred` / `still-relevant`).
- [ ] Subagents used for transcript reading, fresh-observer question generation, external research, and federation introspection (parallelism + main-context isolation).
- [ ] Per-phase token cost estimate logged before phase runs; actual logged after.
- [ ] Hard fail-safe aborts phase if actual exceeds budget × 1.5; partial report written.
- [ ] Phase skip flags (`--skip-research`, `--skip-transcripts`, `--introspect-only`) work and reduce spend correspondingly.
- [ ] Each cross-repo commit surfaces its target repo before being made.
- [ ] Federation use case is documented as a worked example in this design doc (above).

## Open questions

- **Profile location precedence.** Default is `design/beginners-mind.md` if `design/` exists, else `.beginners-mind.md` at root. Should the skill _prefer_ the `design/` location and offer to create one? Probably yes for projects using `/groot-project`, no otherwise — but how to detect cleanly?
- **Subagent reading the code wholesale.** For large projects, the fresh-observer subagent reading the file tree could itself blow the token budget. Sampling strategy needed: top-level dirs + entry points + N most-changed files in the last quarter? Defer to first real-project run.
- **Corpus prune threshold.** "Zero usable signal across last 3 runs" before auto-proposing removal. N=3 is intuition; could be a knob in `corpus.md` header.
- **Bootstrap meta-research scope.** For Derek's federation case the corpus is CC-ecosystem; for a Rails app it's Rails-ecosystem; for a data-pipeline project it's data-eng-ecosystem. The meta-research pass needs the project identity (from step 1) to guide search. Implementation detail, but flag it.
- **Discussion-group archive location pre-thinking.** Should `--init` also ask "where will you eventually share these reports?" so v2's design space is informed by v1 use? Probably yes as an open question in the profile, no as a commitment.

## Related

- `~/code/claude/skills/skills/skills-review/SKILL.md` — adjacent skill; Phase 1 delegates to its `research` mode for skills-catalog introspection.
- `~/code/claude/skills/skills/walkthrough/SKILL.md` — closest structural precedent: general skill, project-specific output, fresh-perspective via subagent dispatch.
- `~/code/claude/skills/skills/groot-project/SKILL.md` — precedent for skill that bootstraps project-level artifacts.
- `~/code/0.llm/remote-coding-setup/CLAUDE.md` — federation context, hub-use-case rule, design placement rule.
- `~/.claude/CLAUDE.md` — global conventions; effort estimates inherit the "1/1000 calibration" rule.
- gstack `/retro` — engineering retro on shipped work; different surface, name nearby.
- gstack `/skills-review` — installed-skills audit; subset of this skill's introspection surface.
