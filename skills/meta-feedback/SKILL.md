---
name: meta-feedback
description: End-of-session lookback on the collaboration itself, not the code. Finds the moments in this session where Derek's ask and the outcome diverged (a correction, a reversal, a redo, a false "verified") and turns each into a concrete proposed change — sharper prompting, a CLAUDE.md / rules / memory edit, or a skill add/edit/remove — scoped global or project-specific. Anti-churn by design: "clean, nothing to fold back" is the expected common result. Modes: bare `/meta-feedback` (propose now, interactive), `file` (write a review report without asking — what /wrapup calls), `review` (walk pending reports later). Triggers on "/meta-feedback", "meta feedback", "what should we fold back from this session", "how could I have steered that better". Not for reviewing code.
argument-hint: "[file | review | help]"
---

# Meta feedback

After the work is done, ask what the _session_ taught about working together, and fold it back into the files the next session preloads. Three questions:

1. **Prompting** — what Derek could have typed to steer better.
2. **Standing guidance** — CLAUDE.md, `~/.claude/rules/`, auto-memory: add, sharpen the trigger, or remove.
3. **Skills** — add, edit, or remove.

Adapted from a friend's `/meta-feedback` skill (itself a colleague's end-of-session ritual). Pays off most after a session with back-and-forth on a design or a disagreement about how something was built. Companion to `/md-add` and `/skill-add` (which apply accepted changes), `/revise-claude-md` (narrower: adds missing project context, no divergence analysis), the global "Mistake retrospectives" rule (fires in the moment on one mistake; this sweeps the session), and `/beginners-mind` (periodic project-wide audit).

## Routing

| Invocation | Does |
| --- | --- |
| `/meta-feedback` | Run the lookback now; present proposals; apply the ones Derek picks. |
| `/meta-feedback file` | Run the lookback; write the report + one pointer line; ask nothing. **What `/wrapup` calls** — a hurried wrap never has to evaluate anything. Zero findings → writes nothing. |
| `/meta-feedback review` | Walk pending reports (`open` proposals) one at a time: accept / decline / skip. |
| `/meta-feedback help` | Print usage (see Help section). |

## Anti-churn rules (hard, not advisory)

A proposal made for the sake of proposing is as bad as a missed one: it bloats always-loaded files and trains Derek to skim the report. These rules bind every mode.

1. **Clean is the expected result.** Most sessions have nothing worth folding back. Say `Clean — nothing to fold back.` and stop. An empty report is the skill working, not failing. Never pad to fill the three questions.
2. **Divergences only, never the topic.** A finding needs a _moment_: Derek restated, corrected, or reversed; Claude asked something the context already answered, did unasked work, stopped short, or claimed "verified" when it wasn't. A session _about_ CLAUDE.md or skills does not thereby produce CLAUDE.md or skill findings.
3. **Every finding names its cost** — a redo, a wrong claim, a wasted round trip, lost work. No cost → not a finding.
4. **Cap: three proposals per session**, ranked by cost. Overflow is dropped, not listed as "also considered."
5. **Existing guidance that didn't fire is a finding against Claude, not a new rule.** Before proposing any rule, grep global `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`, the project `CLAUDE.md`, the project memory index (`~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`), and `~/.claude/skills/*/SKILL.md`. If it exists, the fix targets the _trigger_ (why it didn't fire — buried, vague, wrong section, outweighed), never a duplicate.
6. **Promotion ladder.** First sighting of a correction → a memory entry, or nothing if it was a one-off. CLAUDE.md or a rules file only when (a) it already exists as memory and still failed to fire, (b) prior reports show it recurred, or (c) the miss cost a wrong answer or real money. The always-loaded global file also has to pass `/md-add`'s noise test.
7. **Prefer edit and remove over add.** Every _add_ proposal states what it replaces or why nothing existing covers it. A rule that demonstrably misfired this session is a removal or rewrite candidate.
8. **Declined stays declined.** Grep prior reports (`find ~/code -path '*/design/meta-feedback/*.md' -not -path '*/worktrees/*'`) for the same finding. Re-proposing a `declined` item requires a _new_ moment and must cite the prior decline.
9. **Prompting feedback clears the same bar.** Only when an ambiguous ask cost a turn, phrased as the sentence Derek could have typed. Symmetric honesty: report Derek's ambiguities and Claude's misses alike; no praise padding.

## Scope: global or project-specific

Classify each finding with one test: **would this have mattered in a session on a different repo?**

| Finding is about | Scope | Goes in |
| --- | --- | --- |
| How we work, in any repo | global | `~/.claude/CLAUDE.md` (always-loaded — high bar) |
| A language / tool / file type / domain | global | `~/.claude/rules/<topic>.md` (path-scoped) |
| A correction on how to work, with the why | either | auto-memory `feedback_*.md` + index line, in that project's memory dir |
| A fact about the system or people, not derivable from the repo | project | auto-memory `project_*.md` / `user_*.md` |
| A convention, command, or gotcha specific to this repo | project | the project's `CLAUDE.md` |
| A repeatable multi-step procedure Claude ran or fumbled | usually global | new or edited skill in `dgroo/skills` (`~/code/claude/skills/skills/`) |

**Recurrence across projects is the promote-to-global signal.** A project-scoped finding that shows up again in a second project's reports gets proposed as a global rule, citing both.

## Procedure

1. **Walk the session from the top.** List each divergence (rule 2). If the context opens from a compaction summary, say so — earlier moments may be lost; don't reconstruct them from inference.
2. **Classify each:** ambiguous ask (Q1), missing or misfiring standing guidance (Q2), or a procedure that should be a skill (Q3). One divergence can land in two.
3. **Existence + ledger check** (rules 5 and 8).
4. **Scope each** (table above) and **apply the ladder** (rule 6).
5. **Cut to the cap** (rule 4). If nothing survives: `Clean — nothing to fold back.` Done.
6. **By mode:**
   - **bare** — present the report (format below) inline, ending with the numbered list. Apply only what Derek picks: CLAUDE.md and rules via `/md-add`, a new skill via `/skill-add`, an edit to an existing skill by editing its source in `dgroo/skills`, memory by writing the file directly. Memory is the one thing you may write unasked, and only when the fact is verified and uncontroversial — say so.
   - **file** — write the report file and one pointer line (below). Ask nothing, apply nothing, emit one line: `Filed N meta-feedback proposal(s) → <grootos-link URL>`.
   - **review** — find reports with `open` proposals (the `find` above, then grep `· open`), oldest first. Per proposal: show it, take accept / decline (with a short reason) / skip. Accept → apply as in bare mode. Update the status token in place.

## Where `file` mode writes

- **Report:** `design/meta-feedback/<YYYY-MM-DD>-<slug>.md` in the project the session ran in (slug = the session's topic, kebab-case, 2–4 words). `design/` is live-synced across hosts in Derek's repos, so it's reachable anywhere; where the design-sync watcher owns `design/` commits, let it — don't hand-craft a `docs(design)` commit. A project with no `design/` → write it under the remote-coding capture repo's `design/meta-feedback/` instead (the repo named in global CLAUDE.md's "Cross-project capture" rule), with the source project in the filename.
- **Pointer (exactly one line per report, not per finding):**
  - The project has `design/HUMAN-REVIEW.md` → add under `## Open`: `- <date> · <N> meta-feedback proposal(s): <short gist> · <path> · dogfood: /meta-feedback review`.
  - Otherwise → the cross-project capture queue shard (path and format from global CLAUDE.md's "Cross-project capture" rule): `<date> [<project>] <N> meta-feedback proposal(s): <short gist> → <report path>`, committed per that rule.
- Keep report content to _process_. Don't copy project data, credentials, or customer content into a report — especially when it lands in a different repo than the session's.

## Report format

The report follows the global document-ordering rule: what Derek has to decide comes first; evidence and provenance come last.

```markdown
# Meta-feedback — <topic> · <YYYY-MM-DD>

*Authored by <model> with Derek · Last updated <YYYY-MM-DD>.*

## Proposals

1. **<one-line change>** · <global|project> · <target file> · open
   ```diff
   <proposed change>
   ```
   Cost: <what the divergence cost, one line>.

## Prompting

- <moment, compressed>: next time, try "<the sentence Derek could have typed>".

## Evidence

- Proposal 1: <the moment — what was asked, what happened, where it diverged>. <Existed-and-didn't-fire note, or prior-decline citation, when applicable.>

_Source session: <project> · <host> · <session id if known>._
```

Status tokens are fixed so prior reports form a greppable ledger: `· open`, `· accepted <sha>`, `· declined: <reason>`. Omit `## Prompting` when empty. In bare mode, render the same shape inline (no provenance stamp) and close with the numbered list so Derek can reply with numbers.

## Help

When invoked as `/meta-feedback help`, print the following block verbatim:

```
meta-feedback — Session lookback on the collaboration: turns divergences
between ask and outcome into proposed changes to prompting, CLAUDE.md /
rules / memory, and skills. "Clean — nothing to fold back" is the expected
common result.

Usage: /meta-feedback [verb]

Verbs:
  (none)            Run the lookback now; present up to 3 proposals; apply
                    the ones you pick (via /md-add, /skill-add, direct edit).
  file              Run the lookback; write design/meta-feedback/<date>-<slug>.md
                    + one pointer line (HUMAN-REVIEW.md, else the capture
                    queue). Asks nothing. What /wrapup calls. Zero findings
                    -> writes nothing.
  review            Walk pending reports' open proposals: accept / decline /
                    skip. Declines are remembered and not re-proposed.
  help              Show this message.

Anti-churn: divergences only (never the session's topic), each with a named
cost; cap 3; existing-but-unfired guidance fixes the trigger, never adds a
duplicate; memory first, CLAUDE.md only on recurrence or real cost.

Scope: each finding is global or project-specific ("would this have mattered
in a different repo?"); recurrence across projects promotes to global.

See SKILL.md for full reference.
```
