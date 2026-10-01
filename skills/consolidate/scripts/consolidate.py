#!/usr/bin/env python3
"""Rebuild an unpushed range into the commits a reader would choose: one per feature or fix,
in order, tree byte-identical at the tip.

  consolidate.py [--repo R] [<base>..<head>]            propose (default range: @{upstream}..HEAD)
  consolidate.py [--repo R] [<base>..<head>] --check    exit 0 if already reader-ready, else print the plan, exit 1
  consolidate.py [--repo R] [<base>..<head>] --apply [--messages FILE]
        FILE: JSON list, one message per group; or {"<group#>": "msg"} to override only some.

What a "commit" is here: the range is walked FIRST-PARENT, so a merge (a fleet landing) is one
unit whose files are its diff to main and whose message comes from the commits it merged. The
rebuild is linear -- merges disappear.

Grouping: a unit joins the previous group when it shares a "prefix:" subject, is fixup-shaped
(fix/wip/typo/...) and touches files that group touched, or heavily overlaps its files. A unit
may also fold BACK into an earlier group -- "work landed, then improved three landings later" --
when it is fixup-shaped or overlapping AND touches no file that any commit between them
touched. That disjointness is what makes the move exact: the group's rebuilt tree is its home
commit's tree with the moved unit's files taken from the moved unit, and no commit in between
could have seen those files differently.

Safety: refuses on a dirty tree, on any commit already reachable from the upstream, and -- for
--apply -- while any go-team lease is held (workers' branches are based on the history you would
be rewriting). A backup tag backup/consolidate-<ts> points at the old tip; the new tip is
verified byte-identical to it before the tag is reported.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from datetime import datetime

def git(repo, *a, check=True, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=check, env=e).stdout

PREFIX = re.compile(r"^([a-z][\w./-]{1,30}):\s", re.I)
FIXY = re.compile(r"^(fix|fixup|wip|oops|typo|revert|address review|tweak|cleanup|lint|fmt|format|follow-?up|polish|nit)\b", re.I)
TRAILER = re.compile(r"^[A-Za-z][\w-]*: \S")

def units(repo, rng):
    """First-parent walk; a merge is one unit carrying the commits it merged."""
    out = git(repo, "log", "--first-parent", "--reverse", "--format=%H%x1f%P%x1f%s%x1f%b%x1e", rng)
    rows = []
    for rec in out.split("\x1e"):
        if not rec.strip(): continue
        h, parents, subj, body = (rec.strip("\n").split("\x1f") + ["", "", ""])[:4]
        ps = parents.split()
        files = set(git(repo, "diff", "--no-renames", "--name-only", ps[0], h).split()) if ps else set(git(repo, "show", "--format=", "--name-only", h).split())
        u = {"hash": h, "subject": subj, "body": body.strip(), "files": files, "merge": len(ps) > 1}
        if len(ps) > 1:
            inner = git(repo, "log", "--reverse", "--format=%s%x1f%b%x1e", f"{ps[0]}..{ps[1]}")
            merged = [((r.strip("\n").split("\x1f") + [""])[:2]) for r in inner.split("\x1e") if r.strip()]
            u["merged"] = [(s, b.strip()) for s, b in merged if not s.startswith("Merge ")]  # back-merges of main are not changes
            if len(u["merged"]) == 1:
                u["subject"], u["body"] = u["merged"][0]
            else:
                m = re.match(r"Merge (?:branch ')?([^\s']+)", subj)
                u["subject"] = f"{m.group(1) if m else 'landing'}: {len(u['merged'])} changes"
                u["body"] = "\n".join(f"- {s}" for s, _ in u["merged"])
        rows.append(u)
    return rows

def theme(u):
    m = PREFIX.match(u["subject"])
    return m.group(1).lower() if m else None

def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0

def related(u, group, home, rows, contiguous):
    """Why u belongs with group: 'fixup' (objective: a fix/wip/typo of files the group touched),
    'prefix' (adjacent, same subject prefix) or 'overlap' (heavy file overlap) -- or None."""
    gfiles = set().union(*(rows[i]["files"] for i in group))
    if FIXY.match(u["subject"]) and (u["files"] & gfiles): return "fixup"
    if contiguous and theme(u) and theme(u) == theme(rows[home]): return "prefix"
    if jaccard(u["files"], gfiles) >= 0.5: return "overlap"
    return None

def propose(rows):
    """Returns groups as lists of row indices. group[0]..the last contiguous member is the run;
    members with index > home are moved back from later in the range."""
    groups, homes, why = [], [], {}
    for i, u in enumerate(rows):
        r = groups and homes[-1] == i - 1 and related(u, groups[-1], homes[-1], rows, contiguous=True)
        if r:
            groups[-1].append(i); homes[-1] = i; why[i] = r; continue
        moved = False
        for gi in range(len(groups) - 1, -1, -1):
            g = groups[gi]
            between = [j for j in range(homes[gi] + 1, i) if j not in g]
            r = related(u, g, homes[gi], rows, contiguous=False)
            if r and all(not (u["files"] & rows[j]["files"]) for j in between):
                g.append(i); moved = True; why[i] = r; break
        if not moved:
            groups.append([i]); homes.append(i)
    return groups, homes, why

def split_trailers(body):
    lines = body.splitlines()
    k = len(lines)
    while k > 0 and TRAILER.match(lines[k - 1]): k -= 1
    return "\n".join(lines[:k]).strip(), "\n".join(lines[k:]).strip()

def default_message(g, rows):
    members = [rows[i] for i in g]
    primary = next((u for u in members if not FIXY.match(u["subject"])), members[0])  # the first substantive commit names the change
    rest, trailers = split_trailers(primary["body"])
    parts = [primary["subject"]]
    if rest: parts += ["", rest]
    others = [u for u in members if u is not primary]
    if others:
        parts += ["", "Folds the follow-ups into the final form:"] + [f"- {u['subject']}" for u in others]
        for u in others:  # keep any Co-Authored-By the primary lacks
            _, t = split_trailers(u["body"])
            for line in t.splitlines():
                if line not in trailers and line.startswith("Co-Authored-By:"): trailers = (trailers + "\n" + line).strip()
    if trailers: parts += ["", trailers]
    return "\n".join(parts)

def leases_held(repo):
    d = os.path.join(git(repo, "rev-parse", "--git-common-dir").strip(), "leases")
    if not os.path.isabs(d): d = os.path.join(repo, d)
    return sorted(os.listdir(d)) if os.path.isdir(d) else []

def print_plan(rows, groups, homes, why):
    merges = sum(u["merge"] for u in rows)
    print(f"{len(rows)} commits" + (f" ({merges} merges, linearized)" if merges else "") + f" -> {len(groups)} groups\n")
    for n, (g, home) in enumerate(zip(groups, homes), 1):
        print(f"[{n}] {default_message(g, rows).splitlines()[0]}")
        if len(g) > 1:
            for i in g:
                tags = [why[i]] if i in why else []
                if i > home: tags.append("moved back")
                print(f"      {rows[i]['hash'][:8]}  {rows[i]['subject'][:70]}" + (f"  ({', '.join(tags)})" if tags else ""))

def rebuild(repo, base_sha, rows, groups, homes, msgs):
    """Build each group's commit from its home tree plus the files of members moved from later."""
    idx = tempfile.NamedTemporaryFile(prefix="consolidate-idx-", delete=False).name; os.unlink(idx)
    env = {"GIT_INDEX_FILE": idx}
    parent = base_sha
    order = sorted(range(len(groups)), key=lambda gi: homes[gi])
    for gi in order:
        home = homes[gi]
        git(repo, "read-tree", "--reset", rows[home]["hash"], env=env)
        # overlay: files touched by any member (of any group placed so far) that sits after this home
        overlay = {}
        for gj in order[:order.index(gi) + 1]:
            for i in groups[gj]:
                if i > home:
                    for f in rows[i]["files"]: overlay[f] = max(overlay.get(f, -1), i)
        for f, i in overlay.items():
            entry = git(repo, "ls-tree", rows[i]["hash"], "--", f).strip()
            if entry:
                meta, path = entry.split("\t", 1); mode, _, sha = meta.split()
                git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{sha},{path}", env=env)
            else:
                git(repo, "update-index", "--force-remove", "--", f, env=env)
        tree = git(repo, "write-tree", env=env).strip()
        parent = subprocess.run(["git", "-C", repo, "commit-tree", tree, "-p", parent, "-F", "-"],
                                input=msgs[gi], capture_output=True, text=True, check=True).stdout.strip()
    if os.path.exists(idx): os.unlink(idx)
    return parent

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("range", nargs="?"); ap.add_argument("--repo", default=".")
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--messages", help="JSON list of commit messages, one per group (default: generated)")
    a = ap.parse_args(); repo = a.repo
    rng = a.range or "@{upstream}..HEAD"
    base, _, head = rng.partition(".."); head = head or "HEAD"
    base_sha = git(repo, "rev-parse", base).strip(); head_sha = git(repo, "rev-parse", head).strip()
    rows = units(repo, f"{base_sha}..{head_sha}")
    if not rows:
        print("nothing to consolidate"); return
    groups, homes, why = propose(rows)
    merges = sum(u["merge"] for u in rows)
    if a.check:
        # The gate refuses only on objective signals: merges, and fixup-shaped commits amending work in
        # the range. Prefix/overlap joins are proposals -- two distinct changes to one file are legitimate.
        fixups = sum(1 for r in why.values() if r == "fixup")
        if merges == 0 and fixups == 0:
            print(f"{len(rows)} commits, reader-ready" + (f" ({len(rows) - len(groups)} optional joins; run without --check to see)" if len(groups) < len(rows) else "")); return
        print_plan(rows, groups, homes, why)
        print(f"\nNOT READER-READY: {merges} merge(s), {fixups} fixup(s) amending work in this range. Run:\n"
              f"  python3 ~/.claude/skills/consolidate/scripts/consolidate.py {base_sha[:12]}..{head} --apply\n"
              f"and pass --messages FILE so each commit says what the change IS.")
        sys.exit(1)
    if git(repo, "status", "--porcelain").strip():
        sys.exit("refusing: working tree is not clean")
    up = git(repo, "rev-parse", "@{upstream}", check=False).strip()
    if up and subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", head_sha, up], capture_output=True).returncode == 0:
        sys.exit("refusing: this range is already pushed")
    print_plan(rows, groups, homes, why)
    if not a.apply:
        print("\n(dry run -- pass --apply to rebuild; --messages FILE to supply your own messages)"); return
    held = leases_held(repo)
    if held:
        sys.exit(f"refusing: {len(held)} go-team lease(s) held ({', '.join(held[:4])}) -- workers' branches are based on this history. Consolidate at the stop condition, when no lease is held.")
    if head_sha != git(repo, "rev-parse", "HEAD").strip():
        sys.exit("refusing: --apply rewrites HEAD, so <head> must be HEAD")
    msgs = [default_message(g, rows) for g in groups]
    if a.messages:
        spec = json.load(open(a.messages))
        if isinstance(spec, dict):
            for k, v in spec.items(): msgs[int(k) - 1] = v
        else:
            assert len(spec) == len(groups), "one message per group"; msgs = spec
    tag = f"backup/consolidate-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    git(repo, "tag", tag, head_sha)
    new_tip = rebuild(repo, base_sha, rows, groups, homes, msgs)
    if git(repo, "diff", "--stat", tag, new_tip).strip():
        sys.exit(f"VERIFY FAILED: rebuilt tree differs from {tag}; HEAD untouched, nothing to undo")
    git(repo, "update-ref", "-m", "consolidate", "HEAD", new_tip, head_sha)
    git(repo, "reset", "-q")   # refresh the index against the (identical) new tree
    print(f"\nrebuilt {len(rows)} -> {len(groups)} commits; tree identical to {tag}")
    print(git(repo, "log", "--oneline", f"{base_sha}..HEAD"))
    print(f"backup: {tag}  (git tag -d {tag} once pushed)")

if __name__ == "__main__":
    main()
