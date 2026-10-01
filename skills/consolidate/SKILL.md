---
name: consolidate
description: Rebuild unpushed commits into one per feature or fix, tree-identical; also the machine-wide pre-push gate. Use before any push.
argument-hint: [<base>..<head>] [--check | --apply [--messages FILE]]
---

# Consolidate: commit often, push what a reader would choose

A human reads every commit. Commit as often as you like while working — checkpoints are cheap and `commit as you go` is a go-team rule for good reason — but what gets **pushed** is one commit per feature or fix, describing the final form of the work, not the learning steps that led there. When work lands and is then improved three landings later, the reader gets one commit, not "add X", "fix X", "X: actually handle the empty case".

## The gate

A **machine-wide git pre-push hook** refuses any push whose range isn't reader-ready (`hooks/dispatch.py`, installed once via `git config --global core.hooksPath ~/.claude/skills/consolidate/hooks`). It applies to every repo on the machine and every process that runs git — Claude sessions, pi agents, the human — with nothing to install per project. It chains to any repo-local `.git/hooks/<name>` so per-repo hooks keep working. The only bypass is `git push --no-verify`, which Claude sessions are denied; the human can, with a reason a reader would accept.

Reader-ready means: no merge commits in the range, and nothing the tool would fold. The refusal prints the plan and the exact command.

```bash
python3 ~/.claude/skills/consolidate/scripts/consolidate.py --check          # what the hook runs; exit 0 = ready
python3 ~/.claude/skills/consolidate/scripts/consolidate.py                  # propose, on @{upstream}..HEAD
python3 ~/.claude/skills/consolidate/scripts/consolidate.py --apply --messages msgs.json
```

## What it does

- **Linearizes.** The range is walked first-parent, so a fleet landing (a merge) is one unit whose files are its diff to main and whose message comes from the commits it merged. Merges disappear. Itch's 196 unpushed commits became 41.
- **Folds follow-ups back into the work they amend**, even when unrelated commits sit between — if and only if nothing in between touched any of the follow-up's files. That disjointness is what makes the move exact rather than a rebase with conflicts; a follow-up that shares a file with an intervening commit stays where it is, and that's correct.
- **Groups by theme**: same `prefix:` subject when adjacent, a fixup-shaped subject (`fix`, `wip`, `typo`, `polish`…) touching the group's files, or heavy file overlap.
- **Verifies the tip byte-identical** to the old one before reporting; a `backup/consolidate-<ts>` tag points at the old history until you delete it.

## Messages: the part that needs judgement

Propose first (`--check` or no flag). Read the groups. Then **write the messages** and pass `--messages FILE` — a JSON list, one per group, or `{"3": "msg"}` to override some. A consolidated message says what the change *is* in its final form: title, why, `Thesis:`/`Surface:` trailers carried from the primary commit. The generated default (the first substantive subject, then "Folds the follow-ups into the final form:" and a list) is honest but is a fallback — and for a multi-commit landing it is only `<branch>: N changes`. Don't push that.

## Refusals — all deliberate

- **Dirty tree.** Commit or stash first.
- **Already pushed.** Never rewrite what others may have pulled.
- **A go-team lease is held.** Workers' branches are based on the history you'd be rewriting; merging them afterwards would resurrect it. Consolidate main at the **stop condition**, when no lease is held — go-team does this itself.
- **`<head>` isn't `HEAD`** for `--apply`.

## Where it runs

- **You, before `git push`** — and the hook will insist.
- **go-team's gate**, on each worker branch before `git merge --no-ff` (`references/gate.md`), so a branch lands as the two or three changes it was.
- **go-team at the stop condition**, on main's unpushed range, so the human who pushes in the morning finds one commit per thing rather than a night of merges.
