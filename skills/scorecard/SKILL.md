---
name: scorecard
description: Letter-grade audit of a codebase as it stands: code quality and agent-readiness. Use after a feature or before a big PR.
argument-hint: [directory | --quick]
---

# Codebase Scorecard

Perform a comprehensive, critical third-party audit of a codebase and produce a structured scorecard with letter grades. This is a deep analysis, not a surface-level check.

## When to Use

- After completing a feature or major refactoring
- Code review preparation — run before submitting a PR
- Technical debt assessment — quantify what needs attention
- Onboarding to a new codebase — understand health at a glance
- Before/after comparisons — run before a cleanup, then after, to measure improvement

## How to Invoke

```
/scorecard                    # Full codebase audit of current directory
/scorecard src/               # Audit specific directory
/scorecard --quick            # Abbreviated audit (summary table only)
/scorecard --agents           # Agent-readiness audit only (second table, skip the code grades)
```

A full run produces **two** grades: one for the code, one for agent-readiness. They answer different questions for different audiences, so they get separate tables and separate overall marks — `Code: B / Agent-readiness: C+`.

## Where the rest lives

This file is the process and the output format. Read `references/dimensions.md` — the 14 code rubrics, the 5 agent-readiness rubrics, and the grading scale — when you reach Phase 2 and are ready to grade, not before. `references/worked-example.md` is one finished report; read it once when learning the format, not every run.

## Analysis Process

You MUST perform thorough investigation before grading. Do not grade from vibes — read actual code and docs. Launch multiple exploration agents in parallel to maximize coverage.

### Phase 1: Reconnaissance (parallel)

Launch these investigations simultaneously using the Task tool with subagent_type=Explore:

**Agent 1 — Structure & Architecture:**
- Map the full directory structure, file counts, line counts
- Identify the build system, entry points, dependency graph
- Read README, design docs, architecture docs
- Identify the core modules and their responsibilities
- Assess module boundaries, coupling, cohesion
- Look for god objects (classes with too many responsibilities)
- Check for circular dependencies
- Evaluate the build/bundle pipeline

**Agent 2 — Code Quality & Bugs:**
- Read the largest/most critical source files thoroughly
- Look for actual bugs: off-by-one errors, uninitialized variables, race conditions, edge cases
- Check error handling: swallowed errors, inconsistent patterns, raw exceptions shown to users
- Look for dead code, unused imports, unreachable branches
- Check naming consistency, coding style consistency
- Look for magic numbers, hardcoded values that should be configurable
- Identify code duplication (copy-pasted blocks, near-identical functions)
- Check for proper resource cleanup (file handles, connections, temp files)

**Agent 3 — Security & Licensing:**
- Search for ALL shell execution patterns (system, exec, backticks, eval, spawn, child_process, subprocess, os.system, etc.)
- Search for ALL file operations and check for path traversal, symlink attacks, TOCTOU races
- Check for injection vulnerabilities (SQL, command, XSS, template, regex)
- Check for hardcoded secrets, credentials, API keys
- Look for unsafe deserialization, prototype pollution, or equivalent language-specific risks
- Check for predictable random values used for security purposes
- Read LICENSE files, check for attribution requirements
- Search for copied/vendored code without attribution
- Check dependency licenses for compatibility

**Agent 4 — Tests & Documentation:**
- Read ALL test files — assess coverage breadth and depth
- Identify tautological tests (tests that pass even when code is broken)
- Look for tests that verify messages/strings instead of actual behavior
- Check for flaky tests (timing-dependent, order-dependent, environment-dependent)
- Identify major untested code paths
- Read ALL documentation files
- Cross-reference docs against actual code — find stale claims, wrong references
- Check for contradictions between different docs
- Verify that documented features actually exist in code
- Check if claimed metrics (coverage %, performance numbers) are substantiated
- Read one user-facing page as a first-time reader: can you say what it's for and what to do next? Does it talk about how it was produced instead of the subject? (`/docs` has the standard)

**Agent 5 — Performance & Duplication:**
- Identify hot paths (rendering loops, request handlers, per-frame/per-request code)
- Look for O(n^2) or worse algorithms in hot paths
- Check for unnecessary work (recomputation, redundant I/O, missing caches)
- Look for string concatenation in loops (language-dependent: bad in Java/Perl/Python, fine in others)
- Check for N+1 query patterns, unbatched operations
- Look for missing debouncing, throttling, or pagination
- Catalog all duplicated code patterns with specific locations
- Identify abstractions that should exist but don't

**Agent 6 — Agent Readiness:**
- Read the agent-facing instructions (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`) and check **every factual claim** against the code — stale rules are the finding, not the absence of rules
- Find the work queue. Is it ranked? Are there duplicate or dangling entry numbers? Are the owner's own requests distinguishable from machine-generated ones?
- Find the verification recipe. Run it. Does it work *right now*? How many environments does it cover?
- Hunt vacuous gates: for every test threshold and CI check, ask what input would make it fail. Report each one that has no answer
- Look for thresholds set just above a measured failure rate, tests whose names promise more than their assertions deliver, and tests loosened to accommodate a bug
- Check isolation: worktrees, ports, shared machine-wide singletons (devices, session pools, databases, keychains), whether production is guard-blocked, and whether real credentials or personal data are reachable from an ordinary task
- Check whether lessons are recorded anywhere, and whether the same mistake recurs in the history

### Phase 1.5: External Security Cross-Check (best-effort)

Alongside Agent 3, attempt an independent second opinion from a different model via the `delegate-security-audit` skill. This exists because a single model — including Claude auditing its own analysis — misses classes of vulnerabilities another model catches, and Claude's own guardrails limit how adversarially it will probe certain code. Treat this as strictly additive: if it's unavailable, the scorecard proceeds on Agent 3 alone.

**Check availability first; skip silently if unavailable:**

```bash
command -v pi >/dev/null && pi auth check --provider openrouter --no-refresh >/dev/null 2>&1 && echo available
```

If `pi` isn't installed, or the OpenRouter credential check fails, don't attempt the delegation — proceed with Agent 3's findings alone and note in the report: "External security cross-check skipped (delegate-security-audit unavailable: `pi` not installed / OpenRouter not authenticated)." Never block or fail the scorecard over this being unavailable.

**If available**, invoke the `delegate-security-audit` skill (via the Skill tool) for guidance, but override its default behavior for this context: **scorecard is a read-only grading tool**, so brief GLM explicitly not to modify any files, and run its `pi` command with `--exclude-tools edit,write` appended (the same read-only pattern `delegate-review` uses) regardless of what that skill's own example shows — a grading pass must never leave code changes behind as a side effect. Give it the same scope Agent 3 covers (shell execution patterns, path traversal/symlink/TOCTOU, injection, hardcoded secrets, unsafe deserialization, predictable randomness in security contexts) and ask for a report — findings with file:line and severity, not fixes. Run it in the background (`run_in_background`) while the other Phase 1 agents work, since it can take several minutes; this costs real money, which is expected for a periodic scorecard run per CLAUDE.md, but don't loop it.

Fold its findings into Agent 3's before grading, tagging each with its source. Where the two disagree on severity, or one surfaces something the other missed, note the discrepancy in the report rather than silently picking one — the disagreement itself is signal.

### Phase 2: Grading

After all agents complete, synthesize findings into grades against the rubrics in `references/dimensions.md`. Be honest and critical. A "B" should mean genuinely good code, not "I didn't look hard enough to find problems."

## Output Format for Agent-Readiness

```
| #  | Dimension            | Grade | Key Finding |
|----|----------------------|-------|-------------|
| A1 | Tracking & Priorities| C     | 134 entries, 3 references point at a renumbered item |
| A2 | Verifiability        | B+    | Real device harness; only ever driven from one origin |
| A3 | Guard Integrity      | C-    | A documented gate does not exist in code; one suite cannot fail |
| A4 | Isolation & Safety   | B     | Worktrees used; shared device collisions misread as page bugs |
| A5 | Knowledge Capture    | B-    | Excellent lessons in code comments, not propagated to docs |

**Agent-Readiness: C+**
```

Then, in the detailed report, add one section: **"What would break first in an unattended run"** — the single change that would most increase how long agents can work here without a human. Be concrete and name the file.

## Output Format

### Summary Scorecard

```
# Codebase Scorecard: [Project Name]

**Audited**: [date] | **Size**: [X files, Y KLOC] | **Language(s)**: [primary languages]

| # | Category          | Grade | Key Finding |
|---|-------------------|-------|-------------|
| 1 | Architecture      | B+    | Clean renderer; Editor is a god object |
| 2 | Code Quality      | B-    | Good conventions documented, inconsistently followed |
| 3 | Consistency       | B     | Mostly uniform, some mixed patterns |
| 4 | Security          | C-    | Multiple shell injection vectors |
| 5 | Performance       | C     | Uncached hot-path computation |
| 6 | DRY               | C+    | 5+ duplicated patterns identified |
| 7 | Testability       | B+    | Pure renderer, DI in most modules |
| 8 | Test Coverage     | B-    | Good breadth, tautological in places |
| 9 | Type Safety       | N/A   | Perl — no type system |
| 10| Documentation     | C     | Multiple stale references |
| 11| Error Handling    | C+    | Inconsistent user-facing messages |
| 12| Extensibility     | B     | Good plugin points, tight core coupling |
| 13| Repo Hygiene      | B-    | Junk files, missing .gitignore entries |
| 14| Accretion         | C     | Add:delete 7:1 in production code; zero refactor moves in 110 commits |

**Overall: C+**
```

### Detailed Report

After the summary table, provide these sections:

#### Top Strengths (3-5 bullets)
What the project does well. Be specific — cite files and patterns.

#### Critical Issues (prioritized list)
Issues that should block a release or be fixed immediately. Include:
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Category tag (e.g., [Security], [Bug], [Performance])
- Specific file:line references
- Brief description of the issue and its impact
- Suggested fix

#### Architecture Assessment (2-3 paragraphs)
Honest assessment of the overall design. What's the biggest structural problem? What design decision will cause the most pain as the project grows?

#### Documentation vs Reality
List every place where documentation contradicts the actual code. Be specific with quotes from docs and what the code actually does.

#### Quick Wins (3-5 items)
Easy fixes that would meaningfully improve quality. Each should be achievable in a single commit.

#### Technical Debt (if applicable)
Larger structural issues that need sustained effort. For each item, describe the current state, the target state, and a rough sense of scope (single file vs cross-cutting).

## Guidelines for the Auditor

- **Be genuinely critical.** A useful audit finds real problems. Praising everything helps nobody.
- **Read actual code.** Don't grade based on file names or README claims. Verify.
- **Cite specific evidence.** Every grade must reference concrete findings with file:line.
- **Don't penalize for language limitations.** Perl doesn't have type safety — don't dock points for that. Grade within the language's idioms.
- **Don't penalize for scope.** A small project doesn't need a plugin architecture. Grade proportionally.
- **Do penalize for claims vs reality.** If docs claim "95% test coverage" but there are no metrics, that's a documentation problem.
- **Security issues are never "low priority."** If you find an exploitable vulnerability, the Security grade cannot be above C regardless of how good everything else is.
- **Consider the codebase's stage.** An MVP doesn't need the same polish as a mature production system. Grade proportionally to ambition and maturity — but still flag real risks regardless of stage.
- **Check the junk drawer.** Look at git status, untracked files, temp files, debug artifacts. These reveal working habits.
