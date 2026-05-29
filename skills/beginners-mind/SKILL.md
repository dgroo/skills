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

(Further sections to be added by subsequent plan tasks.)
