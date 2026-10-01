#!/usr/bin/env python3
"""Git-history signals for /slop: is this codebase the residue of understanding,
or the residue of attempts?

Computes accretion signals over a repo's history and, when AI-attributed commits
are present, splits them into a hand-written era and an AI era for comparison.

Usage:
  slop_history.py [repo] [--since YYYY-MM-DD] [--split ai|YYYY-MM-DD|none] [--flags N]

Every number here is a PROXY. Read the flagged commits before believing any of it.
"""
import argparse, re, statistics, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone

AI_RE = re.compile(r"co-authored-by:.*(claude|copilot|cursor|gemini|devin|codex|aider|chatgpt|openai)"
                   r"|generated with \[?claude|claude-session:|🤖", re.I)
FIX_RE = re.compile(r"\b(fix|fixes|fixed|fixing|hotfix|bugfix|repair|patch)\b", re.I)
TRIVIAL_RE = re.compile(r"\b(typo|comment|rename|whitespace|format|formatting|lint|spelling)\b", re.I)
RENAME_RE = re.compile(r"\{(.*?) => (.*?)\}|^(.*) => (.*)$")
# Files that change with every fix by design, or aren't code at all. Excluded from fix signals.
REGISTRY_NAME_RE = re.compile(r"(^|/)(CHANGES|CHANGELOG|HISTORY|NEWS|SCORECARD|TODO|ASKS|DIARY|LESSONS|Cargo\.lock|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|go\.sum|poetry\.lock|Gemfile\.lock)[^/]*$|known_bugs|\.md$", re.I)
# Tests, docs, tooling, examples: additions here are not accretion in the production code.
NONPROD_RE = re.compile(r"_test\.|(^|/)(test|tests|testdata|qa|spec|specs|docs?|examples?|bench|website|release|scripts?|tools?)/|\.(md|txt|rst)$", re.I)

CHURN_DAYS = 14
LEGACY_DAYS = 365
BIG_DIFF = 200


def rename_target(path):
    m = re.search(r"\{(.*?) => (.*?)\}", path)
    if m:
        return path[:m.start()] + m.group(2) + path[m.end():]
    m = re.match(r"^(.*) => (.*)$", path)
    return m.group(2) if m else path


def parse_log(repo, since):
    args = ["git", "-C", repo, "log", "--numstat", "--no-merges", "--date=unix",
            "--format=@@C@@%n%H%n%at%n%P%n%an%n%s%n%b%n@@E@@"]
    if since:
        args.append(f"--since={since}")
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    commits, cur, state = [], None, None
    for line in out.splitlines():
        if line == "@@C@@":
            cur = {"files": [], "body": []}
            state = "hash"; continue
        if cur is None:
            continue
        if state == "hash":
            cur["hash"] = line; state = "ts"
        elif state == "ts":
            cur["ts"] = int(line); state = "parents"
        elif state == "parents":
            cur["parents"] = line.split(); state = "author"
        elif state == "author":
            cur["author"] = line; state = "subject"
        elif state == "subject":
            cur["subject"] = line; state = "body"
        elif state == "body":
            if line == "@@E@@":
                state = "stat"; commits.append(cur)
            else:
                cur["body"].append(line)
        elif state == "stat":
            parts = line.split("\t")
            if len(parts) == 3:
                a, d, p = parts
                is_rename = " => " in p
                a = 0 if a == "-" else int(a); d = 0 if d == "-" else int(d)
                cur["files"].append({"path": rename_target(p), "add": a, "del": d, "rename": is_rename})
    for c in commits:
        text = c["subject"] + "\n" + "\n".join(c["body"])
        c["ai"] = bool(AI_RE.search(text))
        c["fix"] = bool(FIX_RE.search(c["subject"]))
        c["add"] = sum(f["add"] for f in c["files"])
        c["del"] = sum(f["del"] for f in c["files"])
        c["renames"] = sum(1 for f in c["files"] if f["rename"])
        c["date"] = datetime.fromtimestamp(c["ts"], tz=timezone.utc).strftime("%Y-%m-%d")
    commits.sort(key=lambda c: c["ts"])  # oldest first
    return commits


def analyse(commits, all_commits):
    """Per-era metrics. `all_commits` (whole history) is used for file-touch timing
    so era boundaries don't fake churn/legacy numbers."""
    touched = [c for c in commits if c["files"]]
    n = len(touched)
    if n == 0:
        return None
    adds = sum(c["add"] for c in touched); dels = sum(c["del"] for c in touched)
    prod = [f for c in touched for f in c["files"] if not NONPROD_RE.search(f["path"])]
    prod_adds = sum(f["add"] for f in prod); prod_dels = sum(f["del"] for f in prod)
    sizes = [c["add"] + c["del"] for c in touched]
    fixes_raw = [c for c in touched if c["fix"]]
    # Registry files: touched by a large share of fix commits — a changelog, a
    # known-bugs test index. They're MEANT to change with every fix, so their
    # presence says nothing about the fix itself. Exclude them from fix signals.
    fix_file_counts = defaultdict(int)
    for c in fixes_raw:
        for path in {f["path"] for f in c["files"]}:
            fix_file_counts[path] += 1
    registry = {path for path, k in fix_file_counts.items()
                if len(fixes_raw) >= 5 and k / len(fixes_raw) >= 0.3}
    registry |= {f["path"] for c in touched for f in c["files"] if REGISTRY_NAME_RE.search(f["path"])}
    def code_files(c):
        return [f for f in c["files"] if f["path"] not in registry]
    fixes = [c for c in fixes_raw if code_files(c)]  # a changelog-only commit isn't a code fix
    zero_del_fix = [c for c in fixes if sum(f["del"] for f in code_files(c)) == 0]
    add_only = [c for c in touched if c["del"] == 0]
    big_trivial = [c for c in touched
                   if c["add"] + c["del"] > BIG_DIFF and (TRIVIAL_RE.search(c["subject"]) or len(c["subject"]) < 30)]

    # File-touch timeline over the WHOLE history, so we can look back across era edges.
    timeline = defaultdict(list)  # path -> [(ts, commit)]
    for c in all_commits:
        for f in c["files"]:
            timeline[f["path"]].append((c["ts"], c))
    for v in timeline.values():
        v.sort(key=lambda x: x[0])

    era_hashes = {c["hash"] for c in touched}
    touches = churn = legacy = fix_of_fix = 0
    fof_list = []
    for path, tl in timeline.items():
        if path in registry:
            continue
        for i, (ts, c) in enumerate(tl):
            if c["hash"] not in era_hashes:
                continue
            touches += 1
            if i > 0:
                gap = (ts - tl[i - 1][0]) / 86400
                if gap > LEGACY_DAYS:
                    legacy += 1
                prev = tl[i - 1][1]
                if c["fix"] and prev["fix"] and gap <= CHURN_DAYS and prev["hash"] != c["hash"]:
                    fix_of_fix += 1
                    fof_list.append((prev, c, path))
            if i + 1 < len(tl) and (tl[i + 1][0] - ts) / 86400 <= CHURN_DAYS and tl[i + 1][1]["hash"] != c["hash"]:
                churn += 1

    hot = defaultdict(int)
    for c in fixes:
        for path in {f["path"] for f in code_files(c)}:
            if not NONPROD_RE.search(path):
                hot[path] += 1
    fix_hotspots = sorted(hot.items(), key=lambda kv: -kv[1])[:8]

    pct = lambda a, b: (100.0 * a / b) if b else 0.0
    return {
        "fix_hotspots": fix_hotspots,
        "commits": n, "adds": adds, "dels": dels,
        "add_del_ratio": (adds / dels) if dels else float("inf"),
        "prod_adds": prod_adds, "prod_dels": prod_dels,
        "prod_ratio": (prod_adds / prod_dels) if prod_dels else float("inf"),
        "nonprod_share": (100.0 * (adds - prod_adds) / adds) if adds else 0.0,
        "median_lines": statistics.median(sizes),
        "fix_commits": len(fixes), "zero_del_fix": zero_del_fix,
        "zero_del_fix_pct": pct(len(zero_del_fix), len(fixes)),
        "add_only_pct": pct(len(add_only), n),
        "renames": sum(c["renames"] for c in touched),
        "churn_pct": pct(churn, touches), "legacy_pct": pct(legacy, touches),
        "fix_of_fix": fix_of_fix, "fof_list": fof_list, "big_trivial": big_trivial,
        "registry": sorted(registry),
        "span": f"{touched[0]['date']} → {touched[-1]['date']}",
    }


def fmt_ratio(r):
    return "∞ (no deletions)" if r == float("inf") else f"{r:.2f}"


def print_table(eras):
    rows = [
        ("commits (non-merge, with diffs)", lambda m: f"{m['commits']}"),
        ("span", lambda m: m["span"]),
        ("lines added : deleted", lambda m: f"{m['adds']} : {m['dels']}  (ratio {fmt_ratio(m['add_del_ratio'])})"),
        ("  …production code only", lambda m: f"{m['prod_adds']} : {m['prod_dels']}  (ratio {fmt_ratio(m['prod_ratio'])})"),
        ("  …share of additions in tests/docs/tooling", lambda m: f"{m['nonprod_share']:.0f}%"),
        ("median lines / commit", lambda m: f"{m['median_lines']:.0f}"),
        ("addition-only commits", lambda m: f"{m['add_only_pct']:.0f}%"),
        ("'fix' commits", lambda m: f"{m['fix_commits']}"),
        ("  …that deleted nothing", lambda m: f"{len(m['zero_del_fix'])}  ({m['zero_del_fix_pct']:.0f}% of fixes)"),
        ("  …fix-of-a-fix within 14d", lambda m: f"{m['fix_of_fix']}"),
        (f"churn (file re-touched ≤{CHURN_DAYS}d)", lambda m: f"{m['churn_pct']:.0f}% of touches"),
        (f"legacy (file untouched >{LEGACY_DAYS}d, then edited)", lambda m: f"{m['legacy_pct']:.0f}% of touches"),
        ("renames/moves (refactor proxy)", lambda m: f"{m['renames']}"),
        ("big diff, trivial message", lambda m: f"{len(m['big_trivial'])}"),
    ]
    names = list(eras.keys())
    w0 = max(len(r[0]) for r in rows) + 2
    w = 34
    print("".ljust(w0) + "".join(nm.ljust(w) for nm in names))
    print("-" * (w0 + w * len(names)))
    for label, fn in rows:
        print(label.ljust(w0) + "".join(fn(eras[nm]).ljust(w) for nm in names))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--since", help="only consider commits since this date")
    ap.add_argument("--split", default="auto", help="ai | YYYY-MM-DD | none | auto (ai if any AI commits)")
    ap.add_argument("--flags", type=int, default=12, help="how many flagged commits to list per category")
    a = ap.parse_args()

    commits = parse_log(a.repo, a.since)
    all_commits = parse_log(a.repo, None) if a.since else commits
    if not commits:
        sys.exit("no commits found")

    ai_n = sum(1 for c in commits if c["ai"])
    split = a.split
    if split == "auto":
        split = "ai" if ai_n else "none"

    eras = {}
    if split == "ai":
        eras["hand-written"] = analyse([c for c in commits if not c["ai"]], all_commits)
        eras["AI-attributed"] = analyse([c for c in commits if c["ai"]], all_commits)
    elif split != "none":
        cut = int(datetime.strptime(split, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
        eras[f"before {split}"] = analyse([c for c in commits if c["ts"] < cut], all_commits)
        eras[f"from {split}"] = analyse([c for c in commits if c["ts"] >= cut], all_commits)
    eras["all"] = analyse(commits, all_commits)
    eras = {k: v for k, v in eras.items() if v}

    print(f"# /slop history — {a.repo}  ({len(commits)} non-merge commits; {ai_n} AI-attributed)\n")
    span_days = (commits[-1]["ts"] - commits[0]["ts"]) / 86400
    if span_days < CHURN_DAYS * 2:
        print(f"⚠ history spans only {span_days:.0f} days — the {CHURN_DAYS}-day churn and {LEGACY_DAYS}-day legacy "
              f"signals are not meaningful here; read the ratios and fix signals instead.\n")
    print_table(eras)

    focus = eras.get("AI-attributed") or eras.get(next(k for k in eras if k.startswith("from ")), None) or eras["all"]
    print("\n## Flagged — go read these before grading anything\n")
    if focus["registry"]:
        reg = focus["registry"]
        shown = ", ".join(reg[:6]) + (f", … +{len(reg) - 6} more" if len(reg) > 6 else "")
        print(f"(excluded from fix signals — changelogs, docs, bug registries: {shown})\n")
    print(f"### 'fix' commits that deleted nothing ({len(focus['zero_del_fix'])})")
    for c in sorted(focus["zero_del_fix"], key=lambda c: -c["add"])[:a.flags]:
        print(f"  {c['hash'][:8]}  {c['date']}  +{c['add']:<5} {c['subject'][:80]}")
    print(f"\n### fix-of-a-fix chains within {CHURN_DAYS} days ({focus['fix_of_fix']})")
    seen = set()
    for prev, c, path in focus["fof_list"][:a.flags]:
        key = (prev["hash"], c["hash"])
        if key in seen: continue
        seen.add(key)
        print(f"  {prev['hash'][:8]} → {c['hash'][:8]}  {path}")
        print(f"      '{prev['subject'][:60]}'  →  '{c['subject'][:60]}'")
    print(f"\n### fix hotspots — production files most often touched by fix commits")
    for path, k in focus["fix_hotspots"]:
        print(f"  {k:4d}  {path}")
    if not focus["fix_hotspots"]:
        print("  (none)")

    by_key = defaultdict(list)
    for c in commits:
        by_key[(c["subject"], c["ts"])].append(c)
    dups = [v for v in by_key.values() if len(v) > 1 and len({tuple(c.get("parents", [])) for c in v}) > 1]
    print(f"\n### duplicate landings — same subject and timestamp, different parents ({len(dups)})")
    for group in dups[:a.flags]:
        print(f"  {' / '.join(c['hash'][:8] for c in group)}  {group[0]['date']}  {group[0]['subject'][:70]}")
    if dups:
        print("  (the same work reached main by two paths — usually harmless after merge, but check nothing landed twice)")

    print(f"\n### big diff, trivial message ({len(focus['big_trivial'])})")
    for c in sorted(focus["big_trivial"], key=lambda c: -(c["add"] + c["del"]))[:a.flags]:
        print(f"  {c['hash'][:8]}  {c['date']}  +{c['add']}/-{c['del']}  {c['subject'][:70]}")
    print("\nProxies, not verdicts. A fix that only adds lines may be a genuinely missing case;"
          "\na big diff with one thesis is not slop. The question for each: could the author say why?")


if __name__ == "__main__":
    main()
