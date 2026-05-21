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
- **Would the user ever want Claude to invoke this proactively?** If no — they'll always explicitly type `/<name>` — a slash command is lighter. Skills cost context every session; commands cost nothing until used. Defer to `/cmd-add`.
- **Would a script + shell alias do the same job?** If yes, suggest that path; a skill that wraps a one-liner is overhead.
- **Is the LLM doing something the LLM is actually good at?** Tagging, classifying, summarizing — yes. Mechanical file append — debatable; pure regex/string work — no.
- **Is the trigger phrase one the user will actually reach for?** Skills with abstract triggers ("`/synthesize`") get forgotten; concrete verbs survive.
- **Honest reason to build anyway?** If the answer is "I want it" or "this is more fun as a skill", that's a valid reason — say it out loud, don't dress it up as utility.

When the value is thin, name the cheaper alternative (CLAUDE.md note, slash command via `/cmd-add`, shell alias, existing skill) before recommending against. If the cheaper path actually loses something real, that's the justification for the skill.

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
2. **Include the standard `help` verb.** Every new skill ships with a `help` routing entry plus a dedicated `## Help` section. See [Help verb convention](#help-verb-convention) below for the format. This is non-negotiable scaffolding — don't ask the user whether to include it.
3. **Update `README.md`.** Add a row to the Skills table, alphabetical order. (Project convention — see this repo's `CLAUDE.md`.)
4. **Run `make install`.** Symlinks the skill into `~/.claude/skills/`.
5. **Show the result.** Path to the new SKILL.md, the README row added, and the install output line.
6. **Don't commit.** Stage nothing automatically. Tell the user what to commit and let them.

If the skill needs companion files (a script, a template), create them alongside `SKILL.md` in the same directory.

---

## Help verb convention

Every skill in this repo includes a `help` verb that prints a unix-style usage block. The point: a user typing `/<skill> help` should get the same surface they'd get from a CLI's `--help` flag — one-line description, invocation shape, list of verbs/arguments with one-line descriptions, pointer to the SKILL.md for the full reference.

**Anchor in SKILL.md.** Two places:

1. A routing-table row (or equivalent — see "skills without a routing table" below): `| /<skill> help | Print usage (see Help section) |`
2. A dedicated `## Help` section that pins the exact output block. When invoked, the skill prints what's in that section verbatim.

**Standard help block format:**

```
<skill-name> — <one-line description from frontmatter>

Usage: /<skill-name> [verb] [args]

Verbs:
  (none)            <what bare invocation does>
  <verb-1>          <one-line description>
  <verb-2>          <one-line description>
  ...
  help              Show this message.

[Optional — Modes / Options sections for non-verb args.]

See SKILL.md for full reference.
```

**Adapt for shape:**

- *Skills with one main action, no subcommands* (e.g., `/bug`, `/idea`): use `Arguments:` instead of `Verbs:` — list the arg shapes.
- *Skills with modes that are doc-metadata, not verbs* (e.g., `/walkthrough`'s `current` / `planned` / `infinity`): list them under a `Modes:` section below `Verbs:`.
- *Skills with both verbs and options*: both sections; verbs first.

**Skills without a routing table.** Many existing skills document their interface via `## Quick reference`, `## Subcommand:` headers, or prose. For *new* skills, prefer a `## Routing` table — it's the cleanest anchor for help. For *retrofits* (handled by `/skills-review`), the help section can read from whatever verb-doc shape the skill already has; you don't have to rewrite the skill's structure to add help.

**Example** (for the `/journal` skill from this skill's invocation example):

```
journal — Append timestamped entries to a daily journal, with light triage on review.

Usage: /journal [verb] [args]

Verbs:
  (none) <text>     Append text as a timestamped entry to today's journal file.
  review            Surface recent entries; offer to tag or extract follow-ups.
  help              Show this message.

See SKILL.md for full reference.
```

The skill's `## Help` section contains this block verbatim, indented as a code fence. When the user invokes `/journal help`, the skill prints exactly that block.

---

## Guidelines

- **Lead with the evaluation, not the creation.** The point of this skill is the gate. If you skip straight to writing SKILL.md because the proposal "obviously" stands, you've replaced `/skill-add` with raw skill-writing — and that's fine, but say so.
- **One skill in, one skill out.** Don't propose adjacent skills the user didn't ask for. Note them in the recommendation if they're relevant, but don't bundle.
- **Local-only by default.** This repo is a fork; upstream-bound skills are rare and need to clear a different bar (Joe's style, generic enough, etc.). The pre-commit hook (`scripts/check-upstream-edits.sh`) blocks accidental edits to upstream files — let it do its job, don't fight it.
- **Match the surrounding style.** Joe's skills (`/todo`, `/project-setup`) are tight and pragmatic; Derek's local skills (`/claude-md-add`, `/groot-project`) are heavier on rationale. Pick one consciously per Phase 4 — don't mix.
- **The trigger phrase is the most important field.** A skill no one reaches for is dead weight. Make sure the trigger matches how the user actually talks about the work.
- **Help is universal.** Every skill gets a `help` verb (see [Help verb convention](#help-verb-convention)). Don't surface this as an interview question — scaffold it automatically. Skills without help are flagged by `/skills-review` and need retrofit.

## Help

When invoked as `/skill-add help`, print the following block verbatim:

```
skill-add — Gate before creating a new Claude Code skill. Evaluates, decides, then creates.

Usage: /skill-add [<one-line pitch>]

Arguments:
  <pitch>           Free-form description of the proposed skill. If omitted,
                    the skill asks for one. Routes the pitch through Phases
                    1-5 (capture, evaluate, decide, interview, create).

Phases:
  1. Capture        Pin down name, purpose, triggers, local-vs-upstream.
  2. Evaluate       Collision / overlap / value checks against installed catalog.
  3. Decide         Present findings; user picks proceed / modify / abandon.
  4. Interview      Short, focused — only what isn't already clear.
  5. Create         Write SKILL.md (with mandatory `help` verb), update README,
                    run make install. Don't commit.

Conventions:
  Help verb         Every new skill ships with a `/<name> help` routing entry +
                    `## Help` section. Scaffolded automatically, not asked.

See SKILL.md for full reference.
```

## Related

- **`/import-skill`** — for importing an *existing* skill (e.g., from another repo) into this one. Different problem; this skill is for *new* skills.
- **`/skills-review`** — audits the *installed* catalog (duplicates, conflicts, usefulness). Different lifecycle stage; this skill runs at proposal time.
- **`superpowers:writing-skills`** — the superpowers framework's authoring skill. Alternative to Phase 5; some users prefer it. Mention it in Phase 4 if the user asks.
