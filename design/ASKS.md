# Asks

<!--
What Derek has asked for, in order. Maintained by /pm; safe to reorder by hand.

Queue: one line per ask, top = next.
  Format: "- [ ] <title> → [<path>](<path>) · asked <YYYY-MM-DD>[, <date>…] [· Done: <one line>]"
  The pointer is the story or TODO entry that holds the substance. "[x]" = landed, "[-]" = dropped.
  Only Derek's word puts a line here.

Inbox: raw asks, verbatim, oldest first, not yet triaged. New asks are appended at the end of the file.
  Format: "- <YYYY-MM-DD HH:MM> — <text>", continuation lines indented two spaces.
  /pm triage moves each one to the Queue (or TODO / IDEAS) and removes it from here.
-->

## Queue

## Inbox
- 2026-10-19 05:04 — Some of this stuff may be accidental carry-over from Joe's original skill repo which we built on top of...probably worth a question of whether we have reached a point where we should break that connection, and maybe just keep an eye on his skills for useful ideas? (Derek, 2026-10-19, in grootPM's work-model-contract D2, on the (bug)/(feature)/(chore) TODO tags that came from /project-setup's template. Context: 21 of 55 skills are Joe's, upstream last merged 2026-10-01, fork 270 commits ahead.)
- 2026-11-03 10:36 — Run the Executive-summary pass (~/.claude/skills/pm/exec-summary.md § The pass) on every story in drafts/ and ready/ that backlog-scan reports missing or stale, and add · open status words to undecided decision headings first. Medium priority; a /cleanup-design run covers it.
- 2026-11-07 12:11 — high, from grootPM (2026-11-07): the ask-and-answer loop is decided; see grootPM design/stories/ready/ask-and-answer-loop.md, increments 2 and 4, and D4's amendment. /sup and /next rank answered threads above the ASKS queue; the scribe rule from /ponder step 4 (record Derek's answer inline, whatever channel it came on) generalises to /sup, /next, /helping-hands and /pm; /ponder stops writing the count mark at the Decisions heading and writes `· taken <date>` for two-way doors; /helping-hands extends its walk from helping-hands files to every open thread in the project, with --all; /wrapup lists the session's taken decisions and the turn recap names them in plain words. Thread state comes from the backlog-scan change asked of remote-coding-setup.
- 2026-11-07 12:11 — high, from grootPM (2026-11-07): the design-directory lifecycle is decided; see grootPM design/stories/ready/design-directory-lifecycle.md, D3, D4, D7. /cleanup-design: the archive bucket becomes the sweep (move files marked status: done into <dir>/z.archived/ in bulk, repoint links in live files, per-item mark proposals only on computed signals such as a plan whose story is in done/; when sweeping a project with an existing archived/ rename it to z.archived/; recognise both; drop the Orient note that plans fold into stories). /wrapup Phase 3 asks 'notes absorbed, plans whose story shipped this session?' and writes the marker (status: done, done: <date>, superseded_by: <path>, one-line Done banner under the H1). /pm's accuracy review covers notes as well as stories. /groot-project's notes, plans and helping-hands README templates gain the retire paragraph.
