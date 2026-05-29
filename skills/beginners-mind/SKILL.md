---
name: beginners-mind
description: Periodic fresh-eyes audit of any project. Reads the project's profile, introspects current state, observes behavioral patterns, runs an under-briefed fresh-observer subagent (code-only, question-first), pulls from a curated external corpus, and produces a four-section report — Recommendations, Behavioral observations, Cool things, "Why is it like this?". Stateful (corpus + findings + ledger persist across runs). Use when asked to "review the setup", "fresh eyes on this project", "beginner's mind", "/beginners-mind", or to apply prior recommendations via "/beginners-mind apply <ID>".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebFetch, WebSearch, AskUserQuestion
---

# /beginners-mind — fresh-eyes audit for any project

(Implementation in progress — sections added task-by-task per the implementation plan at `~/code/claude/skills/design/plans/2026-05-28-beginners-mind.md`.)

## How to invoke

- `/beginners-mind` — full run.
- `/beginners-mind --init` — interactive profile setup (also auto-fires if no profile found).
- `/beginners-mind --force` — bypass cadence guardrail.
- `/beginners-mind --dry-run` — show planned phases and estimated token spend; no fetches, no writes.
- `/beginners-mind --skip-research` / `--skip-transcripts` / `--introspect-only` — phase-level cost control.
- `/beginners-mind --bootstrap-corpus` — re-seed the project corpus.
- `/beginners-mind apply <ID>` or `do recommended` — act on prior report's action items.

## Profile schema

A profile is a markdown file with **two H2 sections that have different access rules**:

- `## Visible to fresh observer` — structural information the Phase 3 fresh-observer subagent IS allowed to see (scope, corpus location, behavioral signal sources, etc.).
- `## Orchestrator only — do not include in fresh-observer subagent context` — rationale, design history, "known-weird-but-intentional" answers. The orchestrator uses this ONLY when answering questions the fresh subagent asks; it MUST NOT include this section in the subagent's input.

### How to parse a profile

1. Read the profile file with the `Read` tool.
2. Split on the H2 headers. Identify both sections by exact header match (case-sensitive on the first phrase: "Visible to fresh observer" and "Orchestrator only").
3. If either section is missing, surface an error: "Profile at <path> is missing required section: <name>."
4. Return both sections as separate strings. The Phase 3 dispatcher uses ONLY the "Visible to fresh observer" section.

### Locating the profile

Priority order, first match wins:

1. Explicit path from `--profile <path>` argument.
2. `design/beginners-mind.md` relative to the current working directory.
3. `.beginners-mind.md` at the current working directory.
4. If none found, fall through to `--init` mode (Task 3).

(Further sections to be added by subsequent plan tasks.)
