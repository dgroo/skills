---
name: roci-sitrep
description: Whole-host status snapshot for the always-on remote-coding host (Rocinante24 today). Composes git-fleet across ~/code, host vitals (uptime, load, disk, tailscale), container daemon state, brew services, relay state across projects, and open helping-hands. Use when asked "how's Roci?", "status report", "roci sitrep", "/roci-sitrep", or invoked from `/loop` for periodic monitoring. Distinct from /sup (current session/repo) — this is fleet-state across the host.
allowed-tools: Read, Glob, Grep, Bash
---

# /roci-sitrep — Fleet-state report for the remote-coding host

Produces a glanceable, one-page report covering the always-on host (Rocinante24 today; Studio later) end-to-end. Two intended invocations:

1. **Interactive:** Derek (or any CC session) asks "how's Roci?" — get the report inline.
2. **Continuous:** `/loop 30m /roci-sitrep --save` running in a long-lived tmux session on the host, writing dated findings to `~/.claude/monitor/findings/<ISO-timestamp>.md` for later review or anomaly-detection.

This skill is the **cheap path** from `design/notes/2026-05-21-meta-monitoring-research.md` — start here, evaluate after real use, upgrade to Desktop scheduled tasks / cloud routines / *claw if the cheap path leaves bases uncovered.

## How to invoke

```
/roci-sitrep              # print report inline
/roci-sitrep --save       # also write to ~/.claude/monitor/findings/<ts>.md
/roci-sitrep --quiet      # no inline output, just write to disk (useful inside /loop)
```

## What it checks

Run each in parallel where possible. **Tolerate per-check failures**: a single broken command shouldn't kill the whole report. If a check fails, surface that in the report ("⚠ container daemon: unreachable") rather than crashing.

### 1. Host vitals

```bash
uptime                            # load + uptime
df -h / ~                         # free disk on root + home
sw_vers -productVersion           # macOS version (one-time-ish sanity)
```

### 2. Network reachability

```bash
tailscale status 2>/dev/null | grep -E "^(\S+)\s+$(scutil --get LocalHostName 2>/dev/null || hostname)" || echo "tailscale: not on tailnet"
```

If running on a host other than Roci, also check that Roci itself is reachable:

```bash
tailscale status 2>/dev/null | grep rocinante24
```

### 3. Container layer (Phase 6 health)

```bash
container system status 2>&1 | head -3     # daemon up?
container ls -a 2>&1 | head -10            # any zombie containers?
brew services list | grep -E "^container\s" 2>&1
```

If the container CLI isn't installed (Phase 6 not yet on this host), skip silently.

### 4. Repo fleet under ~/code

```bash
git-fleet --json 2>/dev/null
```

Summarize in the report: count of repos, list of any with `dirty > 0` or `ahead > 0` or `behind > 0`. If `git-fleet` is missing, fall back to a one-liner find + git status loop.

### 5. Relay state across projects

For each project under `~/code` that has `design/relay/STATE.md`:

```bash
relay-status 2>/dev/null
```

(Run from the project root — `relay-status` uses `git rev-parse --show-toplevel`.) Surface: parked / active=here / active=other / human-required. Flag anything stuck in `active=other` for > 6h as a soft anomaly.

### 6. Open helping-hands

Across known project roots: count files in `design/helping-hands/` whose YAML frontmatter has `status: open` (or absent — assume open). Report total + list the top 3 with their priorities. Flag any that are `status: done` but still in the directory (drift).

### 7. Unpushed work flag

Surface a one-liner if `git-fleet --ahead` would have any rows. This is the most likely "you forgot to push" signal.

## Output format — text (default, terminal-friendly)

```
## Roci sitrep — 2026-05-21 16:30 CDT

Host: uptime 2d 11h, load 2.4 / 2.2 / 2.5. Disk free: / 312G, ~ 412G. macOS 26.5.
Network: Tailscale ✓ rocinante24 active.
Container: daemon ✓ running (0.12.3). 0 containers up, 0 stopped.

Repos (4 under ~/code):
  • 0.llm/remote-coding-setup  clean  master  ↑1 ↓0
  • claude/skills              clean  main    ↑2 ↓0
  • games/warball              clean  main    ↑0 ↓0
  • vffins                     clean  master  ↑0 ↓0

Relays (1 project):
  • remote-coding-setup: ⚪ parked since 2026-05-21T14:35Z.

Helping-hands open (1):
  • design/helping-hands/2026-05-21-install-rosetta-on-rocinante24.md (medium)

Flags: 3 unpushed commits across 2 repos.
```

Keep it tight. Two rules:

- **One line per repo / relay / helping-hand** in normal cases. Multi-line only when something needs detail (an anomaly explanation).
- **Lead with "Flags:" if anything looks off.** A clean run gets a one-liner ("Flags: none"). The "something needs attention" cases want to be visible without scrolling.

## Output format — `--save` and `--quiet`

When `--save` is passed, after printing the report, also write it (verbatim, sans ANSI escapes) to:

```
~/.claude/monitor/findings/<YYYY-MM-DDTHHMMSSZ>.md
```

With a YAML frontmatter:

```yaml
---
generated_at: 2026-05-21T21:30:00Z
host: rocinante24
trigger: loop      # "interactive" | "loop" | "manual"
anomalies: 1       # 0 = clean run; >0 if anything was flagged
---
```

When `--quiet` is passed (typically from `/loop`), skip the inline print and only do the disk write. The `/loop` machinery surfaces the run anyway; double-printing is noise.

Findings older than 7 days can be pruned (`find ~/.claude/monitor/findings -mtime +7 -delete`); not part of this skill's job.

## Anomaly detection (light)

Don't try to be a full alerting system in V1. But while assembling the report, flag the following as anomalies (incrementing the `anomalies:` counter and printing prominently):

- **Relay stuck.** `active != none && active != $THIS_HOST` for > 6h. Probably means the other side dropped the ball.
- **Container daemon down.** Was up before, is down now (compare against last finding if present).
- **High load sustained.** load1 > 4 AND load5 > 4 (sustained, not a momentary spike).
- **Disk low.** Free disk on `/` < 10 GB.
- **Tailscale dropped.** No active match for our hostname in `tailscale status`.
- **Helping-hand stale.** `status: done` file still in `helping-hands/` for > 24h (the cleanup-design skill should be catching these, but this is a backstop).

For "compare against last finding," read the most recent file in `~/.claude/monitor/findings/` (if any) and parse its frontmatter `anomalies` field. This is best-effort; the skill should never block on it.

## /loop integration (for monitor mode)

Recommended setup, once you decide to leave a monitor running:

```bash
# On Roci, in a dedicated tmux session
tmux new-session -As monitor
claude
# inside Claude:
/loop 30m /roci-sitrep --save --quiet
```

Findings accumulate in `~/.claude/monitor/findings/`. To check on the monitor from any other CC session:

```
@~/.claude/monitor/findings/    # latest finding(s) glanceable
```

Or invoke `/roci-sitrep` directly (without `--save`) for a fresh report any time.

**7-day expiry caveat.** Per Claude Code's [scheduled-tasks docs](https://code.claude.com/docs/en/scheduled-tasks), recurring tasks auto-expire after 7 days. To keep the monitor running indefinitely, the bare `/loop` needs to be re-fired weekly, or migrated to a Desktop scheduled task. Captured in the research note; not solved here.

## Non-goals

- Not a remediation system. This skill surfaces; it doesn't fix. A `/roci-doctor` or `/approve-pending` skill would be the natural remediation layer.
- Not multi-host. Future Studio + multi-host setup will want a meta-aggregator; this skill is single-host.
- Not a replacement for `/sup`. `/sup` is per-session/repo; this is per-host. They coexist.
- Not yet integrated with openclaw's heartbeat / recurring-task machinery. Captured as an open question — when/if that integration matters, this skill stays the same shape, the trigger just changes (openclaw's scheduler invokes it instead of /loop).

## Related

- `git-fleet` (in dotfiles `~/bin/`) — the building block this composes over.
- `~/.claude/monitor/findings/` — where `--save` writes to.
- `design/notes/2026-05-21-meta-monitoring-research.md` (in `remote-coding-setup`) — the design rationale for picking the cheap path.
- `/sup` — sibling per-session/repo sitrep skill.
- `relay-status` (in dotfiles `~/bin/`) — relay state per project; this skill aggregates across projects.
