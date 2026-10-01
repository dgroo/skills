#!/usr/bin/env python3
"""Learning-surface measurement at one or two revisions — the tier-2 numbers, done portably.

  slop_surface.py [repo] [--from REV] [--to REV]     (default: --from = oldest commit, --to = HEAD)
  slop_surface.py [repo] --at REV                      (a single reading; used by the compass)

Reports, per revision and as a delta: production LOC (inline test modules separated),
public/exported names, function count, the longest functions, inline-test share,
the largest production files. Approximate by construction — regexes, not parsers.
"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slop_lang import lang_for, is_test, split_inline_tests


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def measure(repo, rev):
    files = [p for p in git(repo, "ls-tree", "-r", "--name-only", rev).splitlines() if lang_for(p)]
    r = {"prod_loc": 0, "test_loc": 0, "inline_test_loc": 0, "public": set(), "fns": 0,
         "longest": [], "biggest": [], "files": 0}
    for path in files:
        spec = lang_for(path)
        try:
            text = git(repo, "show", f"{rev}:{path}")
        except subprocess.CalledProcessError:
            continue
        lines = text.splitlines()
        if is_test(path):
            r["test_loc"] += len(lines); continue
        prod, inline = split_inline_tests(lines, spec)
        r["inline_test_loc"] += len(inline)
        r["prod_loc"] += len(prod); r["files"] += 1
        r["biggest"].append((len(prod), path))
        decls = [(i, m.group(m.lastindex) if m.lastindex else m.group(0)) for i, l in enumerate(prod) if (m := spec[1].match(l))]
        r["fns"] += len(decls)
        for i, l in enumerate(prod):
            if spec[0].match(l):
                r["public"].add(f"{path}:{spec[0].match(l).group(0).strip()}")
        for k, (i, name) in enumerate(decls):
            end = decls[k + 1][0] if k + 1 < len(decls) else len(prod)
            r["longest"].append((end - i, name, path))
    r["longest"].sort(reverse=True); r["biggest"].sort(reverse=True)
    return r


def show(label, r):
    total = r["prod_loc"] + r["inline_test_loc"] + r["test_loc"]
    print(f"## {label}")
    print(f"  production LOC: {r['prod_loc']:,}   inline test modules: {r['inline_test_loc']:,}   test files: {r['test_loc']:,}"
          f"   ({100 * (r['inline_test_loc'] + r['test_loc']) / total if total else 0:.0f}% of all code is tests)")
    print(f"  public/exported names: {len(r['public']):,}   functions: {r['fns']:,}   production files: {r['files']}")
    print("  longest functions:  " + ";  ".join(f"{n} lines {name} ({os.path.basename(p)})" for n, name, p in r["longest"][:4]))
    print("  biggest files:      " + ";  ".join(f"{n:,} {p}" for n, p in r["biggest"][:4]))
    over = sum(1 for n, _, _ in r["longest"] if n > 100)
    print(f"  functions over 100 lines: {over}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--from", dest="frm"); ap.add_argument("--to", default="HEAD"); ap.add_argument("--at")
    ap.add_argument("--compass", action="store_true", help="with --at: one machine-readable line for go-team's compass.log")
    a = ap.parse_args()
    if a.at and a.compass:
        from datetime import datetime, timezone
        r = measure(a.repo, a.at); total = r["prod_loc"] + r["inline_test_loc"] + r["test_loc"]
        big = r["biggest"][0] if r["biggest"] else (0, "-")
        print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} rev={git(a.repo, 'rev-parse', '--short', a.at).strip()} "
              f"prod_loc={r['prod_loc']} test_share={100 * (total - r['prod_loc']) // total if total else 0}% pub_names={len(r['public'])} "
              f"fns={r['fns']} fns_over_100={sum(1 for n, _, _ in r['longest'] if n > 100)} biggest={os.path.basename(big[1])}:{big[0]}")
        return
    if a.at:
        show(a.at, measure(a.repo, a.at)); return
    frm = a.frm or git(a.repo, "rev-list", "--max-parents=0", "HEAD").split()[0]
    A, B = measure(a.repo, frm), measure(a.repo, a.to)
    show(f"{frm[:12]}  ({git(a.repo, 'log', '-1', '--format=%ad', '--date=short', frm).strip()})", A)
    show(f"{a.to}  ({git(a.repo, 'log', '-1', '--format=%ad', '--date=short', a.to).strip()})", B)
    pct = lambda x, y: f"{100 * (y - x) / x:+.0f}%" if x else "n/a"
    print("## delta")
    print(f"  production LOC {A['prod_loc']:,} → {B['prod_loc']:,} ({pct(A['prod_loc'], B['prod_loc'])})"
          f"   public names {len(A['public']):,} → {len(B['public']):,} ({pct(len(A['public']), len(B['public']))})"
          f"   functions {A['fns']:,} → {B['fns']:,} ({pct(A['fns'], B['fns'])})")
    added = sorted(B["public"] - A["public"]); removed = sorted(A["public"] - B["public"])
    print(f"  public names added: {len(added)}   removed: {len(removed)}")
    if len(B["public"]) and A["prod_loc"] and (len(B["public"]) - len(A["public"])) / max(1, len(A["public"])) > (B["prod_loc"] - A["prod_loc"]) / A["prod_loc"] + 0.1:
        print("  ⚠ public surface is growing faster than the code — learning surface is the axis, not lines")
    elif A["prod_loc"] and B["prod_loc"] > A["prod_loc"] * 1.2 and len(B["public"]) <= len(A["public"]) * 1.05:
        print("  ✓ code grew but the public surface held flat — growth without new learning surface")


if __name__ == "__main__":
    main()
