# go-team — Lessons and self-improvement

Part of the `/go-team` skill; read when something bites, and every 20 cycles. The loop itself is in `SKILL.md`.

## Lessons and self-improvement

### The ledger

Maintain `LESSONS.md` in the project. **Append only when something actually bites** — not per cycle. Each entry:

```markdown
## <short title>
**What happened:** ...
**What it cost:** (time, a bad merge, data loss, a false report to the human)
**The rule that would have prevented it:** ...
**The mechanism that enforces the rule:** ...
**Scope:** project | general
```

**Before adding a lesson, read the existing ones and look for one to improve instead.** A sharper version of an existing lesson is worth more than a new near-duplicate. This is the single most important discipline here: without it the ledger becomes a pile nobody reads.

The test case for whether you are doing this right: *"don't run `stopall` on a shared session tool, it kills other agents' sessions"* and *"pin the simulator UDID, two automation sessions in one browser process crash it"* are **the same lesson** in different words — a shared machine-wide singleton that parallel agents collide on. They should be one entry, generalised, not two.

### Retro

Every N cycles (default 20), run a retro **silently**: read `LESSONS.md`, and write proposals to a scratch file rather than interrupting. Mention in the next report that proposals are waiting.

A lesson is promoted into a skill when it is `scope: general` **and** it has either bitten twice, or bitten once and cost something irreversible — data loss, a bad merge, or a false report to the human. First occurrences that cost nothing stay in the project.

Retro targets **the whole skills repo, not just this skill.** Lessons land where they belong: device and browser traps in the web-tool skill, isolation rules in the worker skill, scaffolding gaps in the setup skill, new audit dimensions in the scorecard. Deliver them with `/request` to the skills project rather than editing it directly.

Retro also proposes **deletions** — rules that have never fired since being added. A skill nobody reads is worse than no skill, and the only defence against that is removing things.

**Never edit a skill without the human's approval.** Present the proposed diff and wait. (The 48-hour retro that produced most of the mechanisms in this skill is the worked example: a proposal, reviewed, then applied — as a consolidating edit, not eighteen appended sections.)

---

