#!/usr/bin/env python3
"""Which fleets are alive? One row per repo under the given roots that has go-team artefacts.

  fleets.py [root ...]        (default: ~/src)

Reads each repo's .git/leases (seat, dispatched age), landings.log (last landing age), last commit
age, ASKS.md top open item. Session state (busy/idle/waiting) comes from ListAgents — the skill
joins it by project name; this script reports what git can see. A fleet with leases, no landing for
hours, and an idle session is stalled whatever its last message said.
"""
import os, re, subprocess, sys, time
from datetime import datetime, timezone

def git(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True); return r.stdout.strip() if r.returncode == 0 else ""

def age(ts):
    if ts is None: return "—"
    s = max(0, time.time() - ts); h = s / 3600
    return f"{int(s // 60)}m" if h < 1 else (f"{h:.1f}h" if h < 48 else f"{h / 24:.0f}d")

def parse_when(v):
    v = v.strip().strip('"')
    try: return float(v) if re.fullmatch(r"\d{9,}(\.\d+)?", v) else datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
    except ValueError: return None

def main():
    roots = [os.path.expanduser(r) for r in (sys.argv[1:] or ["~/src"])]
    rows = []
    for root in roots:
        for name in sorted(os.listdir(root)):
            repo = os.path.join(root, name)
            common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
            if not common: continue
            ldir = os.path.join(common, "leases")
            leases = [os.path.join(dp, f) for dp, _, fs in os.walk(ldir) for f in fs] if os.path.isdir(ldir) else []
            lp = os.path.join(common, "landings.log")
            if not leases and not os.path.exists(lp): continue
            seats, oldest = [], None
            for lf in leases:
                txt = open(lf, errors="replace").read()
                seat = (re.search(r"^slot=(\S+)", txt, re.M) or re.search(r"^seat=(\S+)", txt, re.M))
                seats.append(seat.group(1) if seat else os.path.relpath(lf, ldir))
                d = re.search(r"^dispatched=(.+)$", txt, re.M)
                if d and (w := parse_when(d.group(1))) is not None: oldest = w if oldest is None else min(oldest, w)
            last_landing = None
            if os.path.exists(lp):
                for line in reversed(open(lp).read().splitlines()):
                    parts = line.split()
                    if parts and (w := parse_when(parts[0])) is not None: last_landing = w; break
                if last_landing is None: last_landing = os.path.getmtime(lp)
            last_commit = git(repo, "log", "-1", "--format=%ct"); last_commit = float(last_commit) if last_commit else None
            top = "—"
            asks = os.path.join(repo, "ASKS.md")
            if os.path.exists(asks):
                for l in open(asks):
                    if re.match(r"^\s*- \[ \]", l): top = re.sub(r"\s+", " ", l.strip()[6:])[:48]; break
            stalled = bool(leases) and (last_landing is None or time.time() - last_landing > 3 * 3600)
            rows.append((name, len(leases), ",".join(seats)[:28], age(oldest), age(last_landing), age(last_commit), top, stalled))
    if not rows: print("no repos with go-team artefacts under", roots); return
    print(f"{'project':<12} {'leases':>6}  {'seats':<28} {'oldest lease':>12} {'last landing':>12} {'last commit':>11}  top open ask")
    for name, n, seats, ol, ll, lc, top, stalled in rows:
        flag = "‼ " if stalled else "  "
        print(f"{flag}{name:<10} {n:>6}  {seats:<28} {ol:>12} {ll:>12} {lc:>11}  {top}")
    print("\n‼ = leases held but no landing for 3h+. Join with ListAgents: an idle or waiting session next to ‼ is a stalled fleet.")

if __name__ == "__main__":
    main()
