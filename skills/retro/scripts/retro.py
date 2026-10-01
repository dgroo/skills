#!/usr/bin/env python3
"""Evidence for a process retro: what a session or fleet actually did, from its transcripts and repo.

  retro.py [project-dir] [--hours 48] [--gap 45]

Reads ~/.claude/projects/<sanitized dir>/*.jsonl modified in the window and the repo at project-dir.
Reports: session span and idle share; every idle gap over --gap minutes with what preceded it and
what resumed it; human turns and their redirect/frustration interjections; which channels were used
(AskUserQuestion vs DECISION NEEDED, Cron/ScheduleWakeup, Agent, SendMessage); every question asked;
and the fleet artefacts in the repo (commits, merges, Thesis: trailers, leases, landing sources,
compass, ASKS top item vs lane lease, last lesson). Numbers, not adjectives. Portable Python: no
backslashes in f-string expressions, no awk, no zsh modifiers.
"""
import argparse, collections, glob, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta

WS = re.compile(r"\s+")
def clean(s, n=150): return WS.sub(" ", s or "")[:n]
def parse_ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

REDIRECT = re.compile(r"why (do|are|is|does)|stall|stuck|waiting|research|alternativ|step back|mess|junk|start over|rethink|too (much|long)|slow|revert that|do not|don't|stop\b|going on a while|any progress", re.I)
TEMPLATE_DECISION = re.compile(r"only if a product principle", re.I)

def git(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""

def load_events(path):
    ev = []
    with open(path, errors="replace") as fh:
        for line in fh:
            try: d = json.loads(line)
            except Exception: continue
            t = d.get("type"); ts = d.get("timestamp")
            if t not in ("user", "assistant") or not ts: continue
            ts = parse_ts(ts); c = d.get("message", {}).get("content")
            if t == "user":
                txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
                if not txt.strip() or txt.lstrip().startswith("<"): continue
                kind = "SKILL" if "Base directory for this skill" in txt else "HUMAN"
                ev.append((ts, kind, txt, None))
            else:
                for x in c or []:
                    if not isinstance(x, dict): continue
                    if x.get("type") == "tool_use": ev.append((ts, "tool:" + x.get("name", "?"), json.dumps(x.get("input", {})), x))
                    elif x.get("type") == "text" and x.get("text", "").strip(): ev.append((ts, "SAY", x["text"], None))
    ev.sort(key=lambda e: e[0]); return ev

def analyse_session(path, gap_min):
    ev = load_events(path)
    if len(ev) < 2: return None
    span_h = (ev[-1][0] - ev[0][0]).total_seconds() / 3600
    gaps = [((b[0] - a[0]).total_seconds() / 60, a, b) for a, b in zip(ev, ev[1:]) if (b[0] - a[0]).total_seconds() > gap_min * 60]
    idle_h = sum(g for g, _, _ in gaps) / 60
    tools = collections.Counter(e[1][5:] for e in ev if e[1].startswith("tool:"))
    humans = [e for e in ev if e[1] == "HUMAN"]
    typed = [e for e in humans if len(e[2]) < 800 and "This session is being continued" not in e[2]]  # not pastes, summaries, skill bodies
    redirects = [(e[0], clean(e[2], 170)) for e in typed if REDIRECT.search(e[2])]
    questions = []
    for e in ev:
        if e[1] == "tool:AskUserQuestion" and e[3]:
            for q in e[3].get("input", {}).get("questions", []): questions.append((e[0], clean(q.get("question", ""), 160)))
    decisions = []
    for e in ev:
        if e[1] == "SAY":
            for m in re.finditer(r"DECISION NEEDED[:*\s]*([^\n]{3,200})", e[2]):
                s = m.group(1).strip()
                if not TEMPLATE_DECISION.search(s) and not s.lower().startswith("none"): decisions.append(clean(s, 140))
    goteam = sum(1 for e in ev if e[1] == "tool:Skill" and "go-team" in e[2]) + sum(1 for e in ev if e[1] == "SKILL" and "go-team" in e[2][:300])
    return dict(path=path, start=ev[0][0], end=ev[-1][0], span_h=span_h, idle_h=idle_h, gaps=gaps, tools=tools,
                humans=len(humans), redirects=redirects, questions=questions, decisions=list(dict.fromkeys(decisions)), goteam=goteam)

def repo_facts(repo, hours):
    if not git(repo, "rev-parse", "--git-dir").strip(): return None
    since = f"--since={hours} hours ago"
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    f = {}
    f["commits"] = len(git(repo, "log", since, "--no-merges", "--format=%h").split())
    f["merges"] = len(git(repo, "log", since, "--merges", "--format=%h").split())
    f["thesis"] = sum(1 for l in git(repo, "log", since, "--format=%b").splitlines() if l.startswith("Thesis:"))
    f["fixes"] = sum(1 for s in git(repo, "log", since, "--no-merges", "--format=%s").splitlines() if re.search(r"\b(fix|fixes|fixed)\b", s, re.I))
    ldir = os.path.join(common, "leases")
    lease_files = [os.path.join(dp, fn) for dp, _, fns in os.walk(ldir) for fn in fns] if os.path.isdir(ldir) else []
    f["leases"] = sorted(os.path.relpath(x, ldir) for x in lease_files)
    lp = os.path.join(common, "landings.log")
    f["landings"] = collections.Counter(l.split()[-1] for l in open(lp) if l.strip()) if os.path.exists(lp) else None
    cp = os.path.join(common, "compass.log")
    f["compass"] = open(cp).read().strip().splitlines()[-1] if os.path.exists(cp) else None
    asks = os.path.join(repo, "ASKS.md")
    f["top_ask"] = None
    if os.path.exists(asks):
        for l in open(asks):
            if re.match(r"^\s*- \[ \]", l): f["top_ask"] = clean(l, 120); break
        f["lane_lease"] = any("lane" in open(x, errors="replace").read() for x in lease_files)
    lessons = os.path.join(repo, "LESSONS.md")
    f["last_lesson"] = None
    if os.path.exists(lessons):
        heads = [l.strip("# \n") for l in open(lessons) if l.startswith("## ") and "<short title>" not in l]
        f["last_lesson"] = heads[-1] if heads else None
    return f

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--hours", type=int, default=48); ap.add_argument("--gap", type=int, default=45)
    a = ap.parse_args()
    repo = os.path.abspath(a.project)
    sanitized = repo.replace("/", "-")
    pdir = os.path.expanduser(f"~/.claude/projects/{sanitized}")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=a.hours)
    files = [p for p in glob.glob(os.path.join(pdir, "*.jsonl")) if datetime.fromtimestamp(os.path.getmtime(p), tz=timezone.utc) > cutoff]
    files.sort(key=os.path.getsize, reverse=True)
    print(f"# retro: {os.path.basename(repo)} — last {a.hours}h\n")
    if not files:
        print(f"no session transcripts modified in the window under {pdir}")
    for path in files[:3]:
        s = analyse_session(path, a.gap)
        if not s: continue
        start = s["start"].strftime("%m-%d %H:%M"); end = s["end"].strftime("%m-%d %H:%M")
        pct = 100 * s["idle_h"] / s["span_h"] if s["span_h"] else 0
        print(f"## session {os.path.basename(path)[:8]}  {start} -> {end} UTC  ({s['span_h']:.0f}h)")
        print(f"- idle in gaps > {a.gap} min: {s['idle_h']:.1f}h ({pct:.0f}%) across {len(s['gaps'])} gaps;  human turns: {s['humans']};  go-team invocations: {s['goteam']}")
        t = s["tools"]
        print(f"- channels: AskUserQuestion={t['AskUserQuestion']}  DECISION NEEDED (real)={len(s['decisions'])}  Cron*={sum(v for k, v in t.items() if k.startswith('Cron'))}  ScheduleWakeup={t['ScheduleWakeup']}  Agent={t['Agent']}  SendMessage={t['SendMessage']}  Bash={t['Bash']}")
        if s["questions"]:
            print("- questions asked of the human:")
            for ts, q in s["questions"][:10]: print(f"    {ts.strftime('%m-%d %H:%M')}  {q}")
        if s["redirects"]:
            print("- the human's redirects / frustration:")
            for ts, q in s["redirects"][:8]: print(f"    {ts.strftime('%m-%d %H:%M')}  {q}")
        if s["gaps"]:
            print(f"- longest idle gaps and what preceded them:")
            for g, x, y in sorted(s["gaps"], key=lambda z: -z[0])[:5]:
                print(f"    {g/60:4.1f}h after {x[0].strftime('%m-%d %H:%M')} [{x[1]}] {clean(x[2], 120)}")
                print(f"          resumed by [{y[1]}] {clean(y[2], 80)}")
        print()
    f = repo_facts(repo, a.hours)
    if f:
        print(f"## repo facts (last {a.hours}h)")
        print(f"- commits {f['commits']}, merges {f['merges']}, Thesis: trailers {f['thesis']}, fix-subjects {f['fixes']}")
        print(f"- leases: {len(f['leases'])} {f['leases'][:4]}   landings by source: {dict(f['landings']) if f['landings'] else 'none'}")
        print(f"- compass last line: {f['compass'] or 'none'}")
        if f.get("top_ask") is not None:
            print(f"- top open ask: {f['top_ask']}   lane lease present: {f.get('lane_lease')}")
        print(f"- last lesson recorded: {f['last_lesson'] or 'none'}")
    print("\nRead the gaps before the counts: what preceded each idle stretch is the cause. Then ask of every rule the evidence suggests — what mechanism would enforce it?")

if __name__ == "__main__":
    main()
