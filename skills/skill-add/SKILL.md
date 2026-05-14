---
name: skill-add
description: Use when proposing a new Claude Code skill — evaluates the idea against the installed catalog for collisions, overlaps, and wrap candidates; pushes back if the value is thin; interviews for clarifications only if proceeding; then creates the skill file, updates README, and runs make install. Triggers on "/skill-add <description>", "I want to add a skill that…", "let's make a skill for…", "should I write a skill that…".
argument-hint: <one-line description of the proposed skill>
---

# Add a Skill

Gate before creation. Most skill ideas should exist; some shouldn't; some should wrap or extend an existing skill. This skill makes that call deliberately instead of reflexively building.

Three phases — **evaluate**, **decide**, **create**. The evaluate phase is the point of the skill; the create phase delegates to a small interview and a file write.

## How to Invoke

```
/skill-add a skill that appends to a sparkfile
/skill-add /idea — quick capture of project ideas
/skill-add                   # no args — ask for the proposal
```

The argument is the user's rough pitch. You will turn it into a real proposal during evaluation.

If invoked with no argument, ask one question: *"What's the proposed skill — name and what it does, in one or two sentences?"*

---

## Phase 1: Capture the proposal

Pin down four things before evaluating. Infer what you can from the user's invocation text; only ask for what's genuinely missing.

1. **Working name** (e.g., `idea`, `skill-add`). If the user didn't name it, propose one.
2. **One-line purpose** — what it does, in their words. Don't paraphrase yet.
3. **Trigger phrases** — what the user would type or say to invoke it. ("`/idea <text>`" / "save this to my sparkfile" / etc.)
4. **Where it sits** — local-only skill in this repo, or upstream-bound? **Default: local-only.** Upstream-bound means it has to fit a name and style Joe would accept and goes through a PR — most ideas don't need that.

Echo the four bullets back so the user can correct them before you spend time on the catalog scan.

---

## Phase 2: Evaluate against the catalog

Three checks in parallel. Each can produce a finding that changes what gets built (or whether it gets built).

### 2a. Collision check — does this name or trigger already exist?

```bash
ls ~/.claude/skills/ 2>/dev/null
ls skills/ 2>/dev/null
```

Look for:
- **Exact name match** (`skills/<name>/` already exists) — must rename.
- **Near-name match** (`/idea` vs `/ideas` vs `/spark`) — flag as potential confusion.
- **Trigger collision** — the proposed trigger phrase already routes to another skill (read frontmatter `description:` on candidates that look adjacent).

If any candidate skill is plausibly close, **read its SKILL.md** before pronouncing. Frontmatter alone misleads — the body tells you what the skill actually does.

### 2b. Overlap / wrap check — should this extend an existing skill instead?

For each plausibly-adjacent skill, judge:

| Verdict | What it means | Output |
|---------|---------------|--------|
| **Independent** | Solves a different problem, no shared surface area. | Proceed as new skill. |
| **Subset** | The proposed skill is a subset of an existing one. | Don't create — recommend the existing one with a usage hint. |
| **Superset** | The proposed skill extends an existing one in a coherent way. | Recommend wrapping: the new skill calls the existing one, then adds its layer. (Pattern: `/sup` wraps `/sitrep`.) |
| **Adjacent** | Lives in the same neighborhood but is a different shape. | Proceed, and add a "Companion to" line in the new skill's body that names the neighbors. |

Be specific. "Looks similar to `/todo`" is not a verdict; "`/todo` files priority-tagged tracker entries; `/idea` files untriaged sparks — different lanes" is.

### 2c. Value / shape check — does this earn its keep?

Push back honestly. The questions to answer:

- **Does the skill encode something hard to remember or easy to skip?** If not, a CLAUDE.md line is cheaper.
- **Would a script + shell alias do the same job?** If yes, suggest that path; a skill that wraps a one-liner is overhead.
- **Is the LLM doing something the LLM is actually good at?** Tagging, classifying, summarizing — yes. Mechanical file append — debatable; pure regex/string work — no.
- **Is the trigger phrase one the user will actually reach for?** Skills with abstract triggers ("`/synthesize`") get forgotten; concrete verbs survive.
- **Honest reason to build anyway?** If the answer is "I want it" or "this is more fun as a skill", that's a valid reason — say it out loud, don't dress it up as utility.

When the value is thin, name the cheaper alternative (CLAUDE.md note, shell alias, existing skill) before recommending against. If the cheaper path actually loses something real, that's the justification for the skill.

---

## Phase 3: Decide

Present findings in one block, then let the user choose. Format:

```
**Proposal:** /<name> — <one-line purpose>

**Collisions:** <none / list specific clashes>
**Overlaps:** <none / verdict per neighbor, see table above>
**Value:** <earns its keep / borderline (reason) / thin (cheaper alternative is X)>

**Recommendation:** <proceed as new / wrap /<existing> / skip — use X instead / proceed but rename to Y>
**Open questions:** <bulleted, only if any>
```

Wait for the user to pick: **proceed / modify / abandon / different path.** Don't assume.

---

## Phase 4: Interview (only if proceeding)

A short, focused interview. Skip questions whose answers are already clear from Phase 1–3. Don't pad.

Ask only what you need:

1. **Final name and description.** The frontmatter `description:` is what makes the skill discoverable — needs to be specific enough that future-you matches it on the right trigger. Draft one, get approval.
2. **Argument shape.** `<arg>`, `[optional arg]`, subcommands (`/idea review`)? Used for `argument-hint:`.
3. **Tool restrictions.** Read-only? Then `allowed-tools` should restrict accordingly (see `/sitrep`, `/sup` for examples). Most skills don't need this.
4. **Voice.** Joe-style (tight, numbered phases, code-fence examples — see `/todo`, `/scorecard`) or Derek-style (more editorial, decision tables, longer rationale — see `/claude-md-add`, `/groot-project`). Default: Joe-style unless the skill is genuinely opinion-heavy.
5. **Companion skills.** Any existing skill the new one should explicitly cross-reference (from Phase 2b's "Adjacent" verdicts)?
6. **Anything skill-specific.** File locations, data shape, subcommand semantics, etc.

---

## Phase 5: Create

1. **Write `skills/<name>/SKILL.md`.** Use the structure of an adjacent skill in the chosen style as a template — don't invent a new shape.
2. **Update `README.md`.** Add a row to the Skills table, alphabetical order. (Project convention — see this repo's `CLAUDE.md`.)
3. **Run `make install`.** Symlinks the skill into `~/.claude/skills/`.
4. **Show the result.** Path to the new SKILL.md, the README row added, and the install output line.
5. **Don't commit.** Stage nothing automatically. Tell the user what to commit and let them.

If the skill needs companion files (a script, a template), create them alongside `SKILL.md` in the same directory.

---

## Guidelines

- **Lead with the evaluation, not the creation.** The point of this skill is the gate. If you skip straight to writing SKILL.md because the proposal "obviously" stands, you've replaced `/skill-add` with raw skill-writing — and that's fine, but say so.
- **One skill in, one skill out.** Don't propose adjacent skills the user didn't ask for. Note them in the recommendation if they're relevant, but don't bundle.
- **Local-only by default.** This repo is a fork; upstream-bound skills are rare and need to clear a different bar (Joe's style, generic enough, etc.). The pre-commit hook (`scripts/check-upstream-edits.sh`) blocks accidental edits to upstream files — let it do its job, don't fight it.
- **Match the surrounding style.** Joe's skills (`/todo`, `/project-setup`) are tight and pragmatic; Derek's local skills (`/claude-md-add`, `/groot-project`) are heavier on rationale. Pick one consciously per Phase 4 — don't mix.
- **The trigger phrase is the most important field.** A skill no one reaches for is dead weight. Make sure the trigger matches how the user actually talks about the work.

## Related

- **`/import-skill`** — for importing an *existing* skill (e.g., from another repo) into this one. Different problem; this skill is for *new* skills.
- **`/skills-review`** — audits the *installed* catalog (duplicates, conflicts, usefulness). Different lifecycle stage; this skill runs at proposal time.
- **`superpowers:writing-skills`** — the superpowers framework's authoring skill. Alternative to Phase 5; some users prefer it. Mention it in Phase 4 if the user asks.
