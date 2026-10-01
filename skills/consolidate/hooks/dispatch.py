#!/usr/bin/env python3
"""Machine-wide git hook dispatcher. Every hook name in this directory is a symlink to this file.

Installed once with:  git config --global core.hooksPath ~/.claude/skills/consolidate/hooks
so it applies to every repository on the machine and every process that runs git -- Claude
sessions, pi agents, and the human at the terminal -- with nothing to install per repo. (A repo
that sets its own core.hooksPath, e.g. husky, overrides this; that's git's precedence.)

Two jobs:
  1. Chain to the repository's own hook of the same name (.git/hooks/<name>) if one exists, so
     per-repo hooks such as a pre-commit lint keep working. Its exit status is honoured.
  2. On pre-push: refuse a push whose commits are not reader-ready -- merges in the range, or
     fixups and follow-ups that consolidate.py --check would fold into the work they amend.
     The refusal prints the plan and the command. The only bypass is `git push --no-verify`.
"""
import os, subprocess, sys

STDIN_HOOKS = {"pre-push", "pre-receive", "post-receive", "post-rewrite", "reference-transaction"}
HERE = os.path.dirname(os.path.realpath(__file__))
CONSOLIDATE = os.path.join(os.path.dirname(HERE), "scripts", "consolidate.py")
ZERO = "0" * 40

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()

def main():
    name = os.path.basename(sys.argv[0]); args = sys.argv[1:]
    data = sys.stdin.read() if name in STDIN_HOOKS else None

    common = git("rev-parse", "--git-common-dir")
    local = os.path.join(common, "hooks", name)
    if os.path.isfile(local) and os.access(local, os.X_OK) and os.path.realpath(local) != os.path.realpath(__file__):
        r = subprocess.run([local, *args], input=data, text=True)
        if r.returncode: sys.exit(r.returncode)

    if name != "pre-push": return
    remote = args[0] if args else "origin"
    for line in (data or "").splitlines():
        local_ref, local_sha, remote_ref, remote_sha = line.split()
        if local_sha == ZERO or remote_ref.startswith("refs/tags/"): continue
        if remote_sha != ZERO:
            base = remote_sha
        else:  # new branch: compare against the remote's default branch if we know it
            base = git("rev-parse", "--verify", "-q", f"{remote}/HEAD") or git("rev-parse", "--verify", "-q", f"{remote}/main")
            if not base: continue
            base = git("merge-base", base, local_sha) or base
        r = subprocess.run([sys.executable, CONSOLIDATE, "--repo", ".", "--check", f"{base}..{local_sha}"], capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(f"\npre-push: {local_ref} -> {remote_ref} refused. A human reads every commit.\n\n{r.stdout}{r.stderr}\n"
                             "Bypass, if you have a reason a reader would accept: git push --no-verify\n")
            sys.exit(1)

if __name__ == "__main__":
    main()
