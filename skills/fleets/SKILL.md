---
name: fleets
description: Which go-team fleets are alive, across every project — leases, last landing, session state. Use when you suspect a fleet has stalled.
allowed-tools: Bash, ListAgents, CronList
---

# Fleets: is anything actually running?

"Silence means the fleet is working" is what a fleet says. Whether it's true is a measurement: are seats leased, when did something last land, and is the session that owns the fleet busy, idle, or waiting on you? This answers that for every project at once, from wherever you are.

1. `python3 ~/.claude/skills/fleets/scripts/fleets.py` — one row per repo with go-team artefacts: leases held (and their seats), the oldest lease's age, time since the last landing, time since the last commit, the top open ask. `‼` marks leases with no landing for three hours or more.
2. `ListAgents` — for each `‼` row, find that project's session and its status. **`‼` next to `idle` or `waiting` is a stalled fleet**: work is leased, nothing has landed, and nobody is ticking. `waiting` says what it's waiting on — usually you. If this is the session that owns a fleet, `CronList` shows whether its heartbeat exists.
3. Report one line per fleet: alive (busy, landing recently), stalled (leases, idle, hours since a landing), or dead (leases but no session at all). For stalled ones, say what would restart them — usually `/go-team start` in that project, which now installs the heartbeat.

Don't message the fleets to ask how they are; that's what the artefacts are for.
