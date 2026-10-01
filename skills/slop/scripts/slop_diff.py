#!/usr/bin/env python3
"""Pre-merge shape check for one change. Exit 0 = clean (hints may print). Exit 2 = RETURN TO WORKER, with reasons.

  slop_diff.py [--repo R] <base>..<head> [--require-thesis]

Returns a branch when: a "fix" commit deletes no production lines and names no `Cause:`;
public surface grows and no `Surface:` trailer says why; (--require-thesis) no commit carries `Thesis:`;
a new function's name nearly matches one that already exists (reinvention).
Hints (never decide): multiple theses per commit, copy-pasted added lines, generic names.
"""
import argparse, difflib, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slop_lang import lang_for, is_test

FIX_RE = re.compile(r"\b(fix|fixes|fixed|fixing|hotfix|bugfix|repair|patch)\b", re.I)
ALSO_RE = re.compile(r"\b(and also|; also|, also|plus|as well as)\b|;\s+\w", re.I)
GENERIC_RE = re.compile(r"\b(data|item|result|info|obj|handle\w*|process\w*|utils?|helpers?|manager|misc|temp|tmp)\b", re.I)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("range"); ap.add_argument("--repo", default="."); ap.add_argument("--require-thesis", action="store_true")
    a = ap.parse_args()
    base, _, head = a.range.partition("..")
    head = head or "HEAD"
    returns, hints = [], []

    # --- commits ---
    raw = git(a.repo, "log", "--format=%x1e%H%x1f%s%x1f%b", f"{base}..{head}")
    commits = [c.split("\x1f") for c in raw.split("\x1e") if c.strip()]
    if not commits:
        print("no commits in range"); return
    bodies = "\n".join(c[2] for c in commits)
    has_thesis = bool(re.search(r"^Thesis:", bodies, re.M)); has_surface = bool(re.search(r"^Surface:", bodies, re.M))
    if a.require_thesis and not has_thesis:
        returns.append("no `Thesis:` trailer in any commit — state the one sentence that accounts for the whole change")
    for h, subj, body in commits:
        if ALSO_RE.search(subj) or subj.count(",") >= 2:
            hints.append(f"{h[:8]} subject reads as more than one thesis: “{subj[:70]}”")
        if FIX_RE.search(subj):
            stat = git(a.repo, "show", "--numstat", "--format=", h)
            prod_del = sum(int(p[1]) for l in stat.splitlines() if len(p := l.split("\t")) == 3 and p[1] != "-" and not is_test(p[2]))
            if prod_del == 0 and not re.search(r"^Cause:|root cause", body, re.I | re.M):
                returns.append(f"{h[:8]} is a fix that deletes no production line and names no `Cause:` — "
                               f"a guard around a symptom, or a genuinely missing case? Say which.")

    # --- diff-level: public surface, reinvention, copy-paste, names ---
    diff = git(a.repo, "diff", f"{base}...{head}")
    path, added_pub, removed_pub, new_fns, added_lines = None, [], [], [], []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]; spec = lang_for(path) if not is_test(path) else None; continue
        if line.startswith("--- ") or not path or spec is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            body = line[1:]
            if spec[0].match(body): added_pub.append(f"{path}: {body.strip()[:60]}")
            if (m := spec[1].match(body)) and m.lastindex: new_fns.append((m.group(m.lastindex), path))
            if len(body.strip()) > 30 and not body.strip().startswith(("//", "#", "*", "/*")): added_lines.append(body.strip())
        elif line.startswith("-") and not line.startswith("---"):
            if spec[0].match(line[1:]): removed_pub.append(f"{path}: {line[1:].strip()[:60]}")
    new_pub = sorted(set(added_pub) - set(removed_pub))   # a name whose line merely changed is not new
    gone_pub = sorted(set(removed_pub) - set(added_pub))
    net = len(new_pub) - len(gone_pub)
    if net > 0 and not has_surface:
        returns.append(f"public surface grows by {net} name(s) with no `Surface:` trailer saying why:\n      " + "\n      ".join(new_pub[:6]))
    elif net > 0:
        hints.append(f"public surface +{net} (Surface: trailer present)")
    elif net < 0:
        hints.append(f"public surface shrinks by {-net} — noted as a win")

    # reinvention: new function names vs names already in base
    existing = set()
    for p in git(a.repo, "ls-tree", "-r", "--name-only", base).splitlines():
        spec = lang_for(p)
        if not spec or is_test(p): continue
        for l in git(a.repo, "show", f"{base}:{p}").splitlines():
            if (m := spec[1].match(l)) and m.lastindex: existing.add(m.group(m.lastindex))
    new_names = {n for n, _ in new_fns if n and n not in existing}
    for n in sorted(new_names):
        close = difflib.get_close_matches(n, existing, n=1, cutoff=0.86)
        if close and len(n) > 5:
            returns.append(f"new function `{n}` looks like existing `{close[0]}` — reinvention, or say why both exist")
        if GENERIC_RE.fullmatch(n) or GENERIC_RE.search(n) and len(n) < 12:
            hints.append(f"generic name: `{n}`")

    from collections import Counter
    dup = [(l, k) for l, k in Counter(added_lines).items() if k >= 3]
    if dup:
        hints.append(f"{len(dup)} added line(s) appear 3+ times in this diff — copy-paste over abstraction? e.g. “{dup[0][0][:60]}” ×{dup[0][1]}")

    # --- verdict ---
    print(f"# slop diff {a.range}  ({len(commits)} commit(s))")
    if returns:
        print("\n## RETURN TO WORKER")
        for r in returns: print(f"  • {r}")
    if hints:
        print("\n## hints (not graded)")
        for h in hints: print(f"  • {h}")
    if not returns and not hints:
        print("  clean")
    sys.exit(2 if returns else 0)


if __name__ == "__main__":
    main()
