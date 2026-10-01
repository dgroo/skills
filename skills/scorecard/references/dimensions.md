# scorecard — dimensions and grading scale

Part of the `/scorecard` skill; read at Phase 2, when grading. The process is in `SKILL.md`.

## Evaluation Dimensions

### 1. Architecture (Weight: High)
How well-structured is the codebase? Are responsibilities clear?
- **A**: Clean separation of concerns, clear module boundaries, dependency injection, single responsibility
- **B**: Good structure with minor coupling issues or one area of unclear responsibility
- **C**: Some modules doing too much, moderate coupling, unclear boundaries in places
- **D**: God objects, circular dependencies, tangled responsibilities
- **F**: Monolithic, no discernible structure

### 2. Code Quality (Weight: High)
Is the code correct, readable, and maintainable?
- **A**: No bugs found, clear naming, good error handling, proper resource cleanup throughout
- **B**: Minor issues, readable, mostly correct
- **C**: Some bugs or error handling gaps, readability issues in places
- **D**: Multiple bugs, poor readability, missing error handling
- **F**: Pervasive bugs, unreadable code

### 3. Consistency (Weight: Medium)
Are patterns, naming, and conventions uniform across the codebase?
- **A**: Uniform patterns, naming, error handling, and style throughout
- **B**: Mostly consistent with minor variations
- **C**: Inconsistent in some areas — different patterns for the same problem
- **D**: Wildly different styles across files, no discernible conventions
- **F**: Every file looks like it was written by a different person

### 4. Security (Weight: High)
Are there vulnerabilities? Is the threat model appropriate? Grade from the combined findings of Agent 3 and the external cross-check (Phase 1.5), when the latter ran — tag each finding with its source (`[Agent 3]` / `[GLM]`) in the Critical Issues list.
- **A**: No vulnerabilities found, proper input validation, secure defaults, documented threat model
- **B**: Minor gaps but no exploitable issues, good practices overall
- **C**: Some risks that need attention (e.g., unsanitized input in non-critical paths)
- **D**: Exploitable vulnerabilities present
- **F**: Critical vulnerabilities (injection, auth bypass, data exposure)

### 5. Performance (Weight: Medium)
Is the code efficient where it matters?
- **A**: Hot paths are optimized, appropriate caching, no unnecessary work
- **B**: Generally efficient, minor optimization opportunities
- **C**: Some unnecessary work in hot paths, missing obvious caches
- **D**: O(n^2) in hot paths, redundant I/O, no caching where needed
- **F**: Fundamentally broken performance characteristics

### 6. DRY / Duplication (Weight: Medium)
Is logic expressed once, or copy-pasted?
- **A**: No meaningful duplication, good abstractions at the right level
- **B**: Minor duplication, mostly DRY
- **C**: Noticeable copy-paste that should be refactored (3+ instances)
- **D**: Significant duplication across files
- **F**: Rampant copy-paste throughout

### 7. Testability (Weight: Medium)
Is the code designed to be testable?
- **A**: Dependency injection, clear interfaces, pure functions, easy to mock boundaries
- **B**: Mostly testable, minor coupling issues
- **C**: Some components hard to test in isolation, tight coupling in places
- **D**: Tightly coupled, requires complex setup to test anything
- **F**: Untestable — global state, hidden dependencies, no seams

### 8. Test Coverage & Quality (Weight: Medium)
Do tests exist, and do they actually catch bugs?
- **A**: Comprehensive coverage, tests verify behavior (not just smoke tests), edge cases covered
- **B**: Good coverage with minor gaps, tests are meaningful
- **C**: Tests exist but have gaps, some tautological tests, missing edge cases
- **D**: Sparse tests, many tautological, major features untested
- **F**: No tests or tests that always pass

### 9. Type Safety (Weight: Medium)
Is the type system used effectively? (Grade within the language's capabilities — don't penalize Perl for not being TypeScript.)
- **A**: Strong typing throughout, generics used well, no escape hatches
- **B**: Good typing with minor gaps (a few `any`/`Object`/untyped areas)
- **C**: Mixed — some typed, some untyped, type assertions used as shortcuts
- **D**: Weak typing, frequent escape hatches, types are lies
- **F**: No typing, or types are so wrong they're misleading
- **N/A**: Language has no type system (Python without hints, Perl, shell scripts) — skip this dimension and redistribute weight

### 10. Documentation (Weight: Medium)
Is the project documented, accurately, *for a reader*? Grade against `/docs`: does each page serve one Diátaxis mode (tutorial / how-to / reference / explanation) or does it blur them? Is there a named reader? Does the first sentence answer? Does any page talk about how the documentation was produced or verified (the "development notes" defect)? Is generated reference single-sourced with a drift check that fails? Apply the reader test to one page: could someone who hasn't seen the code say what it's for and what to do next?
- **A**: One mode per page, a stated audience, front-loaded answers, generated reference with a proven drift check, passes the reader test
- **B**: Good docs with minor gaps or slightly stale references; a page or two blur modes
- **C**: Docs exist but read as development notes, mix modes, or have stale references and gaps
- **D**: Minimal or mostly wrong documentation
- **F**: No documentation, or docs that actively mislead

### 11. Error Handling (Weight: Medium)
Does the code handle failures gracefully?
- **A**: Comprehensive error handling, typed errors, graceful degradation, clear user messages
- **B**: Good coverage, minor gaps, consistent patterns
- **C**: Basic handling, some swallowed errors or inconsistent patterns
- **D**: Many unhandled cases, errors swallowed or leak implementation details
- **F**: No error handling, crashes on unexpected input

### 12. Extensibility (Weight: Low)
How easy is it to add features or modify behavior?
- **A**: Plugin architecture or clear extension points, open/closed principle
- **B**: Reasonably extensible, adding features is straightforward
- **C**: Can be extended but requires modifications to existing code
- **D**: Hard to extend without significant refactoring
- **F**: Requires rewrite to add features

### 13. Repo Hygiene (Weight: Low)
Is the repository clean, well-organized, and professional?
- **A**: Clean git history, proper .gitignore, no junk files, CI configured, clear branching strategy
- **B**: Mostly clean with minor issues
- **C**: Some junk files, messy history, incomplete .gitignore
- **D**: Significant clutter, broken CI, no .gitignore
- **F**: Repository is a mess

### 14. Accretion (Weight: Medium)
Is the codebase being folded back as it grows, or only added to? This is a *trend* — the other thirteen grade the tree as it stands; this grades its direction. Run `/slop --quick` and report its grade; that skill owns the method (articulability and surface area decide; history is evidence; smells only annotate). DRY (#6) measures duplication *present*; this measures whether duplication and size are being *removed*. Fix commits that delete nothing, fix-of-a-fix chains in one file, a refactor share near zero, and a tracker that only grows are the signals.
- **A**: Surface area flat or shrinking over the window; refactoring visibly happening; fixes name causes and delete something
- **B**: Mostly chosen; occasional additive fix or unexplained growth
- **C**: Accreting — production add:delete climbing, refactor share near zero, god files growing
- **D**: Sediment — fix-of-a-fix chains, nobody can say why half of it is there
- **F**: Dead in Naur's sense: modifiable, but not well

---

## Agent-Readiness Dimensions

A second, separate table. The 14 dimensions above grade the code. These grade whether **an agent could work here unattended for eight hours without a human** — a different question, and increasingly the one that determines throughput.

Grade these even on a project that has never been worked on by agents; the answer tells the owner what it would cost to start. Skip the whole table only if the user asks for `--quick`.

### A1. Tracking & Priorities (Weight: High)
Is there a work queue an agent can read, rank, and update without guessing?
- **A**: Tracker exists and is prioritised; the human's own direct requests are tracked *separately* and ranked above machine-found work; no duplicate or dangling entry numbers; stale entries pruned
- **B**: Good tracker, minor staleness, human requests not separated but not being buried either
- **C**: Tracker exists but is unranked or has grown past the point of being readable; human requests compete on equal footing with machine-generated items
- **D**: Inline `TODO:` comments only, or a tracker nobody updates
- **F**: No queue — an agent has nothing to pull from

*Check for:* duplicate heading numbers, references pointing at renumbered or deleted entries, entries marked done that aren't, and whether anything distinguishes "the owner asked for this" from "an agent found this."

### A2. Verifiability (Weight: High)
Can an agent confirm a change works, by driving the real thing?
- **A**: A documented recipe for exercising the product end to end (drive the UI, run the binary, curl the endpoint), it works right now, and it covers more than one environment
- **B**: Recipe exists and works, single environment
- **C**: Tests only — nothing that exercises the assembled product; an agent must infer that a feature works from unit coverage
- **D**: Tests are slow, manual, or partly broken; no path from "code changed" to "product works"
- **F**: No way to verify anything without a human

*This is the highest-leverage dimension.* Without it, everything merges on the strength of reports.

*Check for:* a harness that only ever runs in one configuration (one origin, one screen size, one locale) — that makes an entire class of bug structurally invisible. And **can the fixtures exhibit the properties their tests assert?** A corpus that alternates authors so a multi-revision session is unreachable by construction, two rounds with byte-identical images so "image changed" can never fire, a field the real API never returns — construct the failing case by hand and confirm the fixture could produce it.

### A3. Guard Integrity (Weight: High)
Do the project's own checks actually fail when something is wrong?
- **A**: Gates are meaningful and proven; thresholds derived from requirements; CI enforces architectural invariants, not just lint
- **B**: Solid gates, one or two soft thresholds
- **C**: Some gates cannot fail as written, or thresholds are set just above a measured failure rate — enshrining the failure rather than fixing it
- **D**: Tests pass when the code is broken; assertions check log messages rather than behaviour
- **F**: Green means nothing

*Actively hunt vacuous gates.* For each one ask: **what input would make this fail?** Report every gate with no answer. Also flag tests whose names promise more than their assertions deliver, and any test loosened to accommodate a known bug.

*Check for:* **a verdict-file mechanism** — does the check tool write instrument exit codes and the HEAD it ran at somewhere a merge path can read *instead of the worker's report*? Workers have reported "clean build" over a machine-readable refusal; a project whose only record of a check is the agent's say-so cannot grade above C here. And **every predicate ships with the case that must not trigger it** — a rule tested only on the input its author wrote is unproven.

### A4. Isolation & Safety (Weight: High)
Can several agents work at once without corrupting each other or the owner's real data?
- **A**: Worktree-per-agent is the norm; machine-wide shared singletons (devices, session pools, ports, databases, keychains) are documented with collision-avoidance; production is explicitly guard-blocked; credentials and personal data never enter agent context
- **B**: Good isolation, shared resources undocumented but not currently colliding
- **C**: Agents share a checkout or a device; collisions happen and get misdiagnosed as product bugs
- **D**: No isolation; real credentials or personal data reachable from a normal task
- **F**: An agent can destroy the owner's production data by following instructions

*Security-style rule: if agents can reach production data or credentials, this cannot be graded above C.*

*Check for:* **tripwires on global-blast-radius files** — are the few places where any change has global effect (default configs, prompts, ranking loops, abstention gates, the production asset) guarded by a test that fails on content change without an explicit marker? An escalation instruction without one is a wish. And **reversible destructive tooling** — do the project's own reapers, purgers and cleanup scripts quarantine rather than delete, take a required root with no default, and read a liveness signal themselves? A reaper once deleted two live agents' worktrees; a purge script came one guard line from `rm -rf /*`.

### A5. Knowledge Capture (Weight: Medium)
Does the project remember what it learned, and does the learning escape the project?
- **A**: Lessons recorded with cost and cause; generalisable ones promoted into shared tooling; existing lessons sharpened rather than duplicated; instructions to agents match what the code actually does
- **B**: Good diary or lessons file, slightly behind
- **C**: Lessons live only in commit messages and issue threads; the same mistake is re-learned
- **D**: Agent instructions (`CLAUDE.md` and similar) contradict the code — **stale rules are worse than none**, because they are trusted
- **F**: Nothing recorded

*Check every factual claim in the agent-facing instructions against the code.* A rule stated as absolute with an undocumented exception is a finding: readers trust it and audit against it.

---

## Grading Scale

| Grade | Meaning | Implication |
|-------|---------|-------------|
| A+/A  | Excellent | Ship with confidence |
| A-/B+ | Very good | Minor polish needed |
| B/B-  | Solid | Some issues to address |
| C+/C  | Fair | Needs attention before scaling |
| C-/D+ | Below average | Significant work needed |
| D/D-  | Poor | Major problems |
| F     | Failing | Fundamental issues |

**Overall grade** = weighted average, but drag it down if any HIGH-weight category is D or below. A project with A architecture but F security is not a B — it's a C at best.

