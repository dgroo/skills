---
name: lanes
description: Work out what a project's domain lanes should be — the 2-4 durable areas of work several sessions could own in parallel — from the directory structure, the design corpus, and which files actually change together in the commit history. Re-run it periodically to reconsider as the project develops; it flags dead lanes and missing ones. Use when asked "what lanes should this project have", "propose lanes", "are our lanes still right", "/lanes". Companion to /lane, which puts a session into one.
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
---

# Lanes — what are this project's domains?

A **lane** is a long-lived worktree one session owns, named for a domain that outlives any feature in it. This skill answers the question that has to come first: **what are this project's domains?**

That is a judgment call over a codebase, which is why it is a skill and not a flag. But it is a judgment that should rest on evidence, and the evidence is the point.

## Two modes, same sequence

- **First run** — no lanes yet, or only feature-named ones. Propose a set.
- **Re-run** — lanes exist. Check them against where the work actually went, and report drift. This is the mode that earns repetition; run it when a project has changed shape, or from `/pm`.

## Sequence

### 1. Gather evidence — the history first

```bash
lane --json                          # what lanes exist now
lane --cluster --commits 400         # where the work actually is
```

Sandbox-off. `--cluster` is the load-bearing input and deserves reading carefully:

- **`where the work is`** — commit count per directory group. A group with sustained activity and enough files to be more than one concern is a lane candidate. A group with three commits is not.
- **`changes together`** — pairs landing in the same commit. **High co-change means one domain, not two.** `src/spatial + tests/spatial` co-changing 21 times is one lane, not two. `src/domain + src/persistence` at 15 is either one domain or a boundary that leaks, and which one it is is worth saying out loud.
- Machine-authored commits (`docs(design): sync`) are excluded by default. They are the majority of history on a doc-heavy repo and say nothing about where work is — on warball2 they were 79% and buried every real group. `--include-sync` puts them back if you need the raw picture.

Then, and only then, the structural inputs — they say how the code was *filed*, which is weaker evidence than how it is *worked*:

- The directory tree (one or two levels, not a full walk).
- `CLAUDE.md`, `design/DESIGN.md`, and any project-goals block — a project that has named its major features has half-named its lanes.
- `/standup` or `cc-session-board` if several sessions are already running: what they are each doing is the most current evidence there is.

### 2. Propose

**Two to four lanes, plus `main`.** Fewer than two and the machinery is inert by design; more than four and it stops being something a person can hold in their head, which was the whole reason to want lanes.

Each proposal carries:

- **A domain name** that will still be true in a month. `gameplay` will; `kickoff` won't. This is the single most common failure — feature names look natural and expire.
- **A one-line brief** — what the lane is for, in the project's own vocabulary.
- **Paths** it owns, as globs.
- **The evidence**: which groups it covers and what share of commits they carry. A proposal with no commit evidence behind it should say so rather than borrowing the others' authority.
- **Any singleton it owns** (`dev-server`, a fixed port, a device) — one lane must own each, or every session claims it.

Then name what you deliberately did *not* propose and why: a group too small to be a lane, a seam that looked like one but co-changes with its neighbour, work that belongs to `main`.

### 3. On a re-run, report drift before proposing anything

- **Dead lane** — declared, but its paths carry little recent work. Say how little. Candidate for removal, not automatic.
- **Missing lane** — a busy group belonging to no lane. The most valuable output of a re-run.
- **Feature-named lane** — a lane whose name has expired. `blocks`, `kickoff`, `nav-polish`. Propose the domain it should fold into.
- **Leaking boundary** — two lanes whose paths co-change heavily. Either merge them or move the shared thing.

### 4. Confirm, then write

Present the set and get a decision — `AskUserQuestion` when there is a genuine either/or between two carvings, plain prose otherwise. **Never write lanes unasked.** Then, per accepted lane:

```bash
lane <name> "<brief>" --no-session
lane --paths <name> '<glob>' '<glob>'
lane --owns <name> <thing>
```

`--no-session` throughout: proposing lanes is not the moment to start four sessions. Say afterwards that `/lane <name>` enters one and `lane <name>` from a terminal starts a session in it.

## Judgment

- **The tree is the weakest evidence, so do not lead with it.** Any repo has `src/`, `tests/`, `docs/`; that tells you nothing about who could work in parallel. Co-change does.
- **Tests usually are not a lane.** `tests/` co-changes with whatever it tests — that is the signal saying it belongs *to* those lanes, not beside them.
- **The design corpus usually is not a lane either.** `design/**` is gate-exempt and live-synced, and belongs to `main` where `/ponder` runs.
- **Do not propose a lane per person or per session.** Lanes are areas of the code. How many sessions are running is a separate, changeable fact.
- **A single-session project needs no lanes, and saying so is a valid outcome.** Everything downstream is inert below two live lanes. If the project is one person on one thing, say that and stop.

## Related

- `/lane` — put this session into one of them.
- `~/bin/lane` — the primitive: `lane`, `lane --cluster`, `lane <name> "<brief>"`.
- `/pm` — the periodic backlog-stewardship pass this belongs beside; a re-run fits naturally there.
- `groot-claude-coord/design/session-teams/DESIGN.md` §1 — the naming rule and why lanes are domains.
