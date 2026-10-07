---
name: meta-feedback
description: End-of-session lookback on the collaboration itself, not the code. Finds the moments in this session where Derek's ask and the outcome diverged (a correction, a reversal, a redo, a false "verified", a procedure done by hand that wants to be a skill) and turns each into a concrete proposed change — sharper prompting, a CLAUDE.md / rules / memory edit, or a skill add/edit/remove — scoped global or project-specific. Signal over volume: "clean, nothing to fold back" is a normal result, but useful changes aren't dropped for tidiness. Modes: bare `/meta-feedback` (propose now, interactive), `file` (write a central review report without asking — what /wrapup calls; surfaces major findings), `review` (collate pending reports into one Obsidian review page, a recommendation and tick-boxes per item), `apply` (act on what Derek ticked or commented, log it, delete resolved reports). Triggers on "/meta-feedback", "meta feedback", "what should we fold back from this session", "how could I have steered that better". Not for reviewing code.
argument-hint: "[file | review | apply | help]"
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
| `/meta-feedback file` | Run the lookback; write a central report; ask nothing. **What `/wrapup` calls** — a hurried wrap never has to evaluate anything, but major findings get a one-line flag. Zero findings → writes nothing. |
| `/meta-feedback review` | Collate every open report into `design/meta-feedback/REVIEW.md`: one heading per proposal, a stated recommendation on each, tick-boxes per item and per section. Asks nothing in the terminal; Derek reviews in Obsidian. `/sup` suggests this whenever reports are pending and newer than the page. |
| `/meta-feedback apply` | Read `REVIEW.md`: act on every ticked box and `derek:` comment, log each to the ledger, drop the item from the page, delete each report once nothing in it is open. |
| `/meta-feedback help` | Print usage (see Help section). |

## Signal rules

The goal is signal in both directions. Padding the report with proposals made for the sake of proposing bloats always-loaded files and trains Derek to skim; dropping a materially useful change because a rule was applied too rigidly is just as much a failure. These are judgment rules with a default, not filters — when a rule's default would throw away something plainly useful, keep the item and say which rule it bent.

1. **Clean is a normal result.** Many sessions have nothing worth folding back. Say `Clean — nothing to fold back.` and stop. Never pad to fill the three questions.
2. **Grounded in the session, not the topic.** A finding needs a _moment_: Derek restated, corrected, or reversed; Claude asked something the context already answered, did unasked work, stopped short, or claimed "verified" when it wasn't; or a multi-step procedure got done by hand in a way that plainly wants to be a skill or script. A session _about_ CLAUDE.md or skills does not by that fact produce CLAUDE.md or skill findings.
3. **Name the cost** — a redo, a wrong claim, a wasted round trip, lost work, or a near-miss that would have cost one of those. Can't name any cost → not a finding.
4. **Three headline proposals**, ranked by cost. Anything else that clears rules 2–3 goes in the report as a one-line `Also` entry — kept, not dropped — so it's there if Derek wants it.
5. **Check what already exists.** Before proposing a rule, grep global `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`, the project `CLAUDE.md`, the project memory index (`~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`), `~/.claude/skills/*/SKILL.md`, and the ledger. If the guidance exists and didn't fire, that's a finding against Claude, and the fix usually targets the _trigger_ (buried, vague, wrong section, outweighed) rather than a duplicate.
6. **Pick the lightest home that will actually fire.** A correction specific to one situation defaults to memory. A plainly general how-we-work rule can go straight to CLAUDE.md or a rules file on first sighting when it's material; recurrence (ledger or memory) or a real cost strengthens the case. The always-loaded global file still has to pass `/md-add`'s noise test.
7. **Try to fold before you add.** Note whether an existing entry could absorb the change (sharpened, not duplicated). If one can, propose that edit. If none can, add — a useful new rule beats a tidy file. A rule that demonstrably misfired is a rewrite or removal candidate.
8. **Declined items need new evidence.** If the ledger shows the same finding declined, re-propose only with a new moment, citing the prior decline.
9. **Prompting feedback: same bar.** Only when an ambiguous ask cost something, phrased as the sentence Derek could have typed. Report Derek's ambiguities and Claude's misses alike; no praise padding.
10. **Flag what's major.** A finding is _major_ when it cost a wrong answer, lost or nearly lost work, a destructive action, or a broken trust boundary — or when it's likely to bite again in the very next session. `file` mode returns it for `/wrapup` to surface (see Procedure).

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
4. **Scope each** (table above) and **pick its home** (rule 6).
5. **Rank** (rule 4) and **flag major** (rule 10). If nothing survives: `Clean — nothing to fold back.` Done.
6. **By mode:**
   - **bare** — present the report (format below) inline, ending with the numbered list. Dispose of what Derek picks (see Disposition); anything he leaves open gets filed as a report, as in `file` mode, so it isn't lost with the scrollback. Memory is the one thing you may write unasked, and only when the fact is verified and uncontroversial — say so.
   - **file** — write the report (below). Ask nothing, apply nothing. Emit one line: `Filed N meta-feedback proposal(s) → <grootos-link URL>`. For each **major** finding, also emit `⚠ Meta-feedback: <one line> — worth a look before you go (filed either way).` `/wrapup` carries these into its output; it still doesn't block the wrap.
   - **review** — list open reports in the reports dir, oldest first, and run the existence and ledger checks on every proposal (headline and `Also`) before writing a word. Cluster proposals that target the same entry or mechanism into one section. Then write (or extend) the review page (see "Review page" below). **Completeness check before the ready line:** every headline proposal and every `Also` line in every open report appears on the page or in the ledger — grep each report's `## Proposals` and `## Also` entries against the page and account for each one, including the ones the report itself marked "none proposed" (those get a ledger line, not a page item). The 2026-10-07 collation dropped three `Also` lines and they surfaced only at apply time. Then stop: emit one line, `Review page ready: N items in M sections → <grootos-link URL>`. Never walk the proposals in the terminal; the page is the review. (Derek, 2026-10-07: eleven reports' worth of dispositions in one terminal reply was too much to review.)
   - **apply** — read the review page. A ticked section box approves every recommendation in that section; a ticked item box is that item's disposition; a `derek:` comment overrides either and may change the shape or the home. Dispose of each decided item (see Disposition), resolve each `derek:` mark to `derek✓(cc): <what/where>`, remove the item from the page (a section with no items left goes too), and delete any report whose proposals are all in the ledger. Untouched items stay on the page for the next pass; the prompting notes leave when their `seen` box is ticked. Resolved `derek✓(cc)` marks stay on the page under one `## Applied <date>` section (his review window; the next `review` or `apply` pass sweeps it). **When any CLAUDE.md or `~/.claude/rules/` file was edited, finish by running the CLAUDE.md audit** (`claude-md-management:claude-md-improver`) on the edited file and report its verdict in the apply summary — Derek, 2026-10-07: with this many edits, check the file is still good and not bloated; routine on every apply that touches standing guidance, not only big ones. Be aggressive about finishing: the goal of an apply pass is an empty directory.

## Disposition

Every proposal leaves `apply` (or bare mode) in one of four ways:

- **Do it** — CLAUDE.md and rules via `/md-add`; a new skill via `/skill-add`; an edit to an existing skill by editing its source in `dgroo/skills`; memory by writing the file directly; anything else by just doing it in the owning repo.
- **Hand it off** — too big to do in the moment → file it as a story (`design/stories/drafts/`) or `TODO.md` entry in the _owning_ repo (`dgroo/skills`, `dot-claude`, the remote-coding repo, the project itself), citing the report's evidence. The story now owns it.
- **Decline** — with a short reason.
- **Skip** — leave it open for another pass.

Every non-skip outcome appends one line to the ledger: `<date> · <project> · <one-line finding> · accepted <sha> | handed off → <path> | declined: <reason>`. When a report has no open items left, **delete the report file** — the ledger and git history keep the record, and a resolved report left in place is noise that hides the open ones. (This deletion is the explicit purpose of `apply`; it doesn't need a separate confirmation.)

## Where reports live

All reports go to **one central place** so a project Derek stops working on can't strand them: `design/meta-feedback/` in the remote-coding capture repo (the repo named in global CLAUDE.md's "Cross-project capture" rule). It's live-synced across hosts, and `/sup` checks it from any project.

- **Report:** `design/meta-feedback/<YYYY-MM-DD>-<project>-<slug>.md` (slug = the session topic, kebab-case, 2–4 words). The design-sync watcher owns commits under `design/` there — don't hand-craft a `docs(design)` commit.
- **Review page:** `design/meta-feedback/REVIEW.md`, the one page Derek answers (format below); same watcher-owned commits.
- **Ledger:** `design/meta-feedback/LEDGER.md` — one line per disposed proposal, newest first. The recurrence and declined checks (rules 5, 6, 8) grep it; cross-project recurrence is the promote-to-global signal.
- Keep report content to _process_. Don't copy project data, credentials, or customer content into a report — it lands in a different repo than the session's.

## Review page

`design/meta-feedback/REVIEW.md`, beside the reports. Modelled on the dashboard project's `design/NEEDS-DEREK.md` page: Derek reads and answers it in Obsidian, so everything he can act on is a heading (it lands in the Outline) with tick-boxes under it, and his comments are `derek:` HTML comments per the global inline-review-marks convention.

- **Header:** H1, provenance stamp, a "How to answer" paragraph (tick an item, tick a section, or comment; what `apply` does with each), then the collation date and report count.
- **Sections** (`## A. <one-line theme>`): proposals clustered by the entry or mechanism they touch, so a rule three reports want changed is one rewrite, not three items. Each opens with the source-report links (relative) and the target file, then `- [ ] approve every recommendation in this section`.
- **Items** (`### A1 · <one-line change>`): `**Cost:**` one line, the moment and what it cost. `**Recommendation:**` one line, always present, starting with the verb (`do`, `hand off`, `decline`, `close`); when the home or the shape is uncertain it says so plainly and the alternative gets its own box; a genuinely open call says "no firm recommendation" in those words, never a soft hedge. Then the exact edit as a `diff` block when it is text, or one sentence when it is a file or a TODO entry. Then the boxes: `- [ ] do as recommended` (or `hand off` / `close` / `decline as recommended`), `- [ ] decline`, plus one box per named alternative.
- **Prompting notes:** one section at the end, reading only, with a single `- [ ] seen` box.
- **Re-running `review`** with items still open: keep every existing item with its ticks and comments, append the new reports' proposals into the matching section or a new one, bump the stamp. Never regenerate over Derek's marks.

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

## Also

- <one-line finding> · <global|project> · <target> · open

## Prompting

- <moment, compressed>: next time, try "<the sentence Derek could have typed>".

## Evidence

- Proposal 1: <the moment — what was asked, what happened, where it diverged>. <Existed-and-didn't-fire note, or prior-decline citation, when applicable.>

_Source session: <project> · <host> · <session id if known>._
```

Mark a major finding with a leading `⚠`. Each proposal carries `· open` until disposed (then it moves to the ledger). Omit `## Also` and `## Prompting` when empty. In bare mode, render the same shape inline (no provenance stamp) and close with the numbered list so Derek can reply with numbers.

## Help

When invoked as `/meta-feedback help`, print the following block verbatim:

```
meta-feedback — Session lookback on the collaboration: turns divergences
between ask and outcome into proposed changes to prompting, CLAUDE.md /
rules / memory, and skills. "Clean — nothing to fold back" is the expected
common result.

Usage: /meta-feedback [verb]

Verbs:
  (none)            Run the lookback now; present up to 3 headline proposals
                    (+ one-line extras); do the ones you pick (via /md-add,
                    /skill-add, direct edit).
  file              Run the lookback; write a report to the capture repo's
                    design/meta-feedback/. Asks nothing; flags major findings
                    in one line. What /wrapup calls. Zero findings -> nothing.
  review            Collate open reports into design/meta-feedback/REVIEW.md:
                    a heading per proposal with a stated recommendation and
                    tick-boxes per item and per section, for review in
                    Obsidian. Asks nothing in the terminal.
  apply             Act on what the review page has ticked or commented:
                    do / hand off (story or TODO in the owning repo) /
                    decline. Logs each to LEDGER.md, clears the item from
                    the page, deletes a report once fully resolved.
  help              Show this message.

Signal rules: grounded in session moments (not the topic), each with a named
cost; 3 headline proposals, extras kept as one-liners; existing-but-unfired
guidance usually fixes the trigger; fold into an existing entry when one can
absorb it, otherwise add. Bend a rule rather than drop something useful.

Scope: each finding is global or project-specific ("would this have mattered
in a different repo?"); recurrence across projects (via the ledger) promotes
to global. Reports are central so an abandoned project can't strand them.

See SKILL.md for full reference.
```
