---
name: pm
description: The project's PM. `/pm <text>` — or a plain `pm: <text>` message, which a hook files the moment it is typed, even mid-turn — takes work Derek wants done — anything from a spark to an epic — records it, checks it against existing work (an existing story gets the addition and a bump instead of a twin), and puts it on the ask queue in `design/ASKS.md`, which /next and /sup rank directly under the session handoff. `/pm triage` works through asks waiting in the inbox. Bare `/pm` is the periodic backlog-stewardship pass — hygiene via /cleanup-design, an accuracy review of stories, durable reprioritization (TODO order and story priority, asking on genuine tradeoffs), and grounded gap proposals. Use for "add this to the queue", "I want to work on this soon", "file this with the PM", "bump the X story", "run a PM pass", "is the backlog stale / in the right order / missing anything".
argument-hint: "<work to file> | triage | ? | ! | help"
---

# /pm — the project's PM

Derek hands work to the PM the way he would to a team lead: he says what he wants and trusts it to land in the right place, in the right order. Three verbs: take an ask, sort the inbox, review the backlog.

## Routing

| Invocation              | Behavior                                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `pm: <text>` (a plain message) | **Intake, and the one form that works the same idle or busy.** The `pm-receipt` hook files it the moment Enter is pressed and says so in a `[pm-receipt hook]` note; you [triage](#triage) if idle, or keep working and triage when the block wraps. |
| `/pm <text>`            | **Intake.** [Receipt](#receipt--always-first-always-one-append), then [triage](#triage) unless the session is mid-task. Typed mid-turn, it waits for the turn to end. |
| `/pm triage`            | [Triage](#triage) everything waiting in the Inbox.                                                                   |
| `/pm`, `/pm ?`, `/pm !` | The periodic pass. **Read [`review.md`](review.md)** (installed at `~/.claude/skills/pm/review.md`) and follow it.   |
| `/pm help`              | Print the [Help](#help) block verbatim.                                                                              |

Anything after `/pm` that is not `triage`, `?`, `!` or `help` is an ask. That includes instructions about work already on file ("bump the auth story", "move the importer to the top", "drop the tagging one"): they are asks about the queue, and triage applies them to the existing line.

## The ask file

`design/ASKS.md` holds what Derek has asked for, in order. Use root `ASKS.md` only when the project keeps its meta-files at the root and has no `design/`. If neither exists, create `design/ASKS.md` from [`asks-template.md`](asks-template.md) (installed at `~/.claude/skills/pm/asks-template.md`). In a linked worktree the ask file is the **main checkout's** copy, not the worktree's: asks belong on trunk, where design sync and the lead read them.

- **`## Queue`** is the priority list: one line per ask, top is next. Each line points at the story or TODO entry that holds the substance. `/next` and `/sup` rank the top open line directly under the session handoff (`backlog-ranking.md` §3).
- **`## Inbox`** is the last section of the file: raw asks, verbatim, oldest first, not yet triaged.

**Only Derek's word puts a line on the Queue.** That is what makes an ask outrank machine-found work: origin is which file an item is in, not a field anyone has to maintain. The PM may propose a line; it never adds one on its own.

## Receipt — always first, always one append

**If the message carries a `[pm-receipt hook]` note, the receipt is already done.** The hook appended the ask when Derek pressed Enter. Do not append it again; go straight to the triage decision below.

Otherwise:

1. Append one entry to the Inbox: `- <YYYY-MM-DD HH:MM> — <the text, verbatim>`. Indent continuation lines two spaces. A leading `@<project>` stays in the entry. Use the `ask` command when it is installed (`ask "<text>"`, in `~/bin`): it finds or creates the right file, including from a worktree, and places the entry. Append by hand only when it is not.
2. That is the whole receipt. Read nothing else, derive nothing, ask nothing. The ask is now on disk whatever happens to the session.

Then decide whether to triage now:

- **The session is idle, or the ask is what Derek is doing:** triage in the same turn.
- **The session is in the middle of other work:** do not triage in this context. Acknowledge as `triage pending` and go back to the work. Hand the Inbox to a **background agent** if the session can start one (Sonnet-tier, not Haiku, which did not hold the stub format when tried; brief: "read `~/.claude/skills/pm/SKILL.md`, run its Triage section in `<project path>`, and report the `Filed:` lines"), and relay its `Filed:` lines when it reports. If it cannot, add an in-session task ("triage the ASKS inbox when the current block wraps"). Either way the Inbox is the persistent record.

How the two typed forms behave mid-turn: `pm: <text>` is a plain message, so the hook files it at Enter and it reaches you while the turn is still running; keep working, and end the turn with its `Filed:` line. `/pm <text>` is a slash command, which Claude Code holds until the turn ends. A turn that received a `pm:` ask and ends without a `Filed:` line is refused once by the `pm-filed-check` hook.

## Triage

Start by reconciling the Queue, then take each Inbox entry, oldest first.

**0. Reconcile pointers.** A line whose story is now in `stories/done/`, or whose TODO entry is checked, becomes `[x]`. A pointer that broke because a story moved between `drafts/` and `ready/` is fixed in place.

**1. Another project's ask.** An entry tagged `@<project>` for a different project stays in the Inbox; say it is waiting to be carried over. Do not triage another project's work from here.

**2. Size it** from the text, without asking: a spark (a thought, no "soon" in it), a task (concrete, no design needed), a story (needs design), an epic (too large for one story). **"I'm debating building X" is a story, and it is queued.** When Derek says he is debating, considering, or not sure about something, he means "I think I want this and need help thinking it through, weighing the tradeoffs, or deciding whether it is a good idea." That is an ask for a `/ponder`, not a spark: file the stub, put it on the Queue, and say in the `Filed:` line that its next step is a ponder.

**3. Look for existing work, by content.** Run `backlog-scan`, list story titles across `drafts/`, `ready/` and `done/` (`grep -m1 '^# '`), and scan `TODO.md`, `IDEAS.md` and `REVISIT.md`. Read the opening section of at most the three most plausible matches. If none of them is the same work, it is new.

**4. Route it.**

- **Matches an open story:** append the text verbatim to that story under `## Captured addition (/pm, unreviewed)`, dated. Bump its Queue line (step 5).
- **Matches something in `done/`:** it already shipped. Say where. If the ask clearly wants more than what shipped, file a new story that links the done one; otherwise there is nothing to queue.
- **New, story-sized:** write a stub in `design/stories/drafts/` in `/story`'s stub format (verbatim body, the not-yet-pondered marker, `author: user`; honor the project's `STORY_TEMPLATE.md`). Never file to `ready/`. If step 3 turned up work that is related but not the same — including a story in another project — record it in one `Related (found at triage):` line under the marker, so `/ponder` starts from it. That line is the PM's; the body stays Derek's.
- **Task-sized:** add an entry to `TODO.md` in that file's own format, per `/todo`.
- **A spark:** one line in `design/IDEAS.md` in `/idea`'s format. No Queue line.
- **Epic-sized:** one stub named `<slug>-epic.md` in `drafts/`, and suggest `/ponder <slug>-epic`. Never decompose an epic at intake.
- **An instruction about the queue:** apply it to the existing line: stamp, move, or mark `[-]` for a drop.

**5. Place the Queue line.**

```
- [ ] <title> → [<path>](<path>) · asked 2026-10-01, 2026-10-14 · Done: <one line, only if the ask said>
```

- A position cue in the ask wins: "next", "top", "urgent", "after the importer".
- A new ask with no cue goes at the bottom of the Queue.
- A re-ask adds today's date to the line. Move it only on strong signal (it unblocks a line above it) and say why; otherwise it keeps its position, and the date count is what the review weighs.
- A story placed on the Queue gets `priority: high` if it was lower. Never lower a priority here.
- **The cap is the review's to enforce, intake only mentions it.** If this line takes the Queue past about eight open lines, still place it, and add to the `Filed:` line: `queue is at <N> — worth a /pm pass`.

**6. Do not guess.** Two plausible matches, or an ask that contradicts a `ready/` story, stays in the Inbox with a `<!-- derek(cc): <the question> — default: <what the PM would do> -->` mark on the line below it. Say so in the `Filed:` line.

**7. Remove the Inbox entry** once it is routed. Git keeps the history.

**8. Commit.** Where the design-sync watcher is running (`launchctl list 2>/dev/null | grep -q design-sync-watch`), saves under `design/` commit themselves. Otherwise, and for a root `TODO.md` or `ASKS.md`, stage the exact files and commit with a pathspec, then push.

## The `Filed:` line

A turn that received or triaged an ask ends with one line per ask, placed directly above the recap footer so it survives a view that shows only the final message:

```
Filed: <short title> → design/stories/drafts/<slug>.md (new, 4th in queue)
Filed: <short title> → design/stories/drafts/<slug>.md (new, 4th in queue — a "debating" ask: next step is /ponder <slug>)
Filed: <short title> → design/stories/ready/<slug>.md (bumped, asked 3×, still 2nd)
Filed: <short title> → TODO.md (new task, 5th in queue)
Filed: <short title> → design/IDEAS.md (spark, not queued)
Filed: <short title> → already shipped: design/stories/done/<slug>.md
Filed: <short title> → design/ASKS.md inbox (triage pending)
Filed: <short title> → design/ASKS.md inbox (needs your call: <the question>)
```

After a new story stub, offer once, in one line, to work it up now or leave it for `/ponder`. Do not start.

## Rules

- **Receipt before anything.** The append happens before any reading or thinking. An ask that exists only in the conversation can be lost.
- **Verbatim.** Derek's words go into the Inbox, the stub, and the captured addition unchanged. The PM authors titles, slugs and Queue lines, nothing else.
- **Intake never builds.** No implementing, no promoting to `ready/`, no design thinking. A stub's next step is `/ponder`.
- **The Queue is Derek's.** His order stands unless he gives a cue or the signal is strong. Hand edits to the file are authoritative.
- **File an ask where it belongs.** Text about a private project is not appended to a public repository's ask file; file it in the current project's Inbox with the `@<project>` tag and say so.
- **The PM does not dispatch.** With lanes, the lead reads the Queue when choosing what to brief. Without them, `/next` does.

## Help

When invoked as `/pm help`, print the following block verbatim:

```
pm — the project's PM. Takes asks, keeps the ask queue, runs the periodic
backlog pass.

Usage: pm: <work to file>          (plain message — works idle or mid-turn)
       /pm [<work to file> | triage | ? | ! | help]

Verbs:
  pm: <text>        The one form to remember. A hook appends the ask to the
                    Inbox the moment you press Enter, even while Claude is
                    busy; idle, it is triaged straight away; mid-task, the
                    work continues and the turn ends with its "Filed:" line.
                    (From a shell with no session: ask "<text>".)
  <text>            Intake. Append the ask verbatim to the Inbox in
                    design/ASKS.md, then triage it: check it against existing
                    work, bump the existing story or file a new stub / TODO
                    entry / spark, and place it on the Queue. Mid-task, only
                    the append happens and triage waits for the block to wrap.
                    Ends with a "Filed: <title> → <path> (new | bumped | …)" line.
  triage            Reconcile the Queue, then triage everything in the Inbox.
  (none)            The periodic pass: hygiene (via /cleanup-design) + accuracy
                    review + strong-signal reprioritization written back to
                    TODO and story frontmatter + the ask queue reconciled
                    (landed asks checked off and pruned). Presents gaps,
                    genuine priority tradeoffs, and proposed Queue admissions,
                    reorders and drops (cap: about eight open asks) for a decision.
  help              Show this message.

Modifiers for the pass (decisiveness dial):
  ?                 Advise only — run the full pass read-only, write nothing.
  !                 Autonomous — also file grounded gap-drafts and act on more
                    reorders without asking. Still surfaces genuine priority
                    TRADEOFFS (those stay Derek's call even under !).

The ask file (design/ASKS.md):
  ## Queue          Ordered asks, top = next. /next and /sup rank the top open
                    line right under the session handoff. Only Derek's word
                    adds a line (the pass proposes, never adds, even under !);
                    reorder by hand freely.
  ## Inbox          Raw asks awaiting triage.

Companions:
  Uses /story's stub format, /todo's and /idea's entry formats; reads
  ~/bin/backlog-scan; the pass wraps /cleanup-design and is nudged by /wrapup.

See SKILL.md for intake and review.md for the pass.
```

## Related

- **`/story`**, **`/todo`**, **`/idea`** — the direct doors when Derek already knows the size. `/pm <text>` is the door when he does not want to choose; it files in their formats.
- **`/ponder`** — develops a stub into a real story. Intake stops short of it on purpose.
- **`/next`**, **`/sup`** — read the Queue through `backlog-scan` and rank it under the handoff.
- **`/go-team`** — reads `ASKS.md` first and works its top open item; the Queue format keeps its `- [ ]` and `Done:` conventions.
- **Design record:** `design/stories/ready/pm-intake-and-ask-queue.md` in this repo. Built so far: receipt, in-session and background triage, the Queue, ranking, the pass's queue review (reconcile, admissions, cap), and the `pm:` path — the `ask` command (dotfiles `~/bin/ask`) plus the `pm-receipt` and `pm-filed-check` hooks (`~/.claude/hooks/`). Not yet: carrying `@<project>` asks to their project.
