---
name: retro
description: Evidence-first retrospective of a session or fleet from its transcripts and repo. Use when a process isn't working and you want to know why before changing anything.
argument-hint: [project-dir] [--hours N]
---

# Retro: find out what actually happened before deciding what to change

When a session or a fleet "keeps stalling" or "never finishes," the temptation is to add a rule. Don't — not yet. The fleets that stalled had the rule ("run it on a loop") written down; what they lacked was the evidence that it wasn't happening (zero scheduled wakeups in 480 hours) and the mechanism that would have made it happen. A retro produces both: the number, and the thing that refuses.

This complements `/go-team retro`, which reads `LESSONS.md` — the fleet's *self-report*. This reads what actually happened, which is a different source in the same way `/slop`'s history is different from `/scorecard`'s snapshot.

## Run the script first

```bash
python3 ~/.claude/skills/retro/scripts/retro.py <project-dir> [--hours 48]
```

It reads the project's session transcripts (`~/.claude/projects/…/*.jsonl`) and its repo, and reports numbers: session span and idle share; every idle gap with what preceded it and what resumed it; human turns and the human's own redirects ("why do we keep stalling", "this has been going on a while"); which channels were used — `AskUserQuestion` versus `DECISION NEEDED`, `Cron`/`ScheduleWakeup`, `Agent`, `SendMessage`; every question asked; and the repo's fleet artefacts — commits, merges, `Thesis:` trailers, leases, landing sources, the compass line, the top open ask and whether anyone holds a lane lease for it, the last lesson written.

## How to read it

1. **Gaps before counts.** An idle share of 90% is not "stalling" — it's *not running*. For each long gap, what preceded it is the cause: a question the human wasn't there to answer, a permission prompt, a turn that ended with a completion report and nothing to resume it. What resumed it tells you who was doing the work of keeping things alive (if it's always `[HUMAN]`, there is no heartbeat).
2. **Channels defined versus channels used.** A skill can define `DECISION NEEDED` and the model will still reach for `AskUserQuestion`, because that's the tool that exists. Zero uses of a designed channel means the design isn't binding.
3. **The human's own words are evidence.** "Why do we keep stalling waiting on me for tool approval?" is a root-cause statement. Quote it.
4. **Artefacts versus claims.** Landings all labelled `asks` while the top ask is untouched; a compass line reading `not-taken`; leases with no cron — each is a record that exists and a measurement that doesn't. That shape recurs everywhere; name it when you see it.
5. **The one diagnostic question**, from go-team's failure catalogue: *what else would produce exactly this reading?* Two states, one observation — find the signal they don't share before concluding.

## Write the findings as rule + mechanism

Each finding, ranked by evidence weight:

```
**N. <what happened, with the number>.** <the cost, and the evidence — quote the transcript or cite the artefact>
*Mechanism:* <the hook, script, agent definition, setting, or file the gate reads — the thing that refuses. A rule with no mechanism is a record of intent.>
```

Before proposing a new rule, read the target skill's existing ones and sharpen one instead of adding a sibling. Prefer one capstone with instances over fifteen parallel rules. Then deliver the proposals to the skills repo with `/request skills "<title>" --body-file <proposals.md>` — don't edit that repo from here.

## What this skill does not do

It doesn't grade code (`/slop`, `/scorecard`), and it doesn't fix anything. It tells you what happened, in numbers, so that the fix is the right one.
