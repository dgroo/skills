---
name: relay-setup
description: Initialize a project for the Roci↔Serenity Relay — the cross-host Claude Code handoff protocol that lets two CCs on different machines pass work to each other via git commits, without a human relaying messages by hand. Creates `design/relay/STATE.md`, `design/relay/handoffs/`, `design/relay/config.toml`, and the `.gitignore` entries needed. Run once per project that participates in the relay. Idempotent (refuses to clobber if already initialized). Use when asked to "set up the relay", "initialize relay", "enable cross-host handoff", or `/relay-setup`.
argument-hint: [--hosts host1,host2] [--branch BRANCH] [--initial-active HOST]
---

# Relay setup — per-project initializer

For a project that two (or more) hosts will collaborate on via the Roci↔Serenity Relay, generate the mailbox files committed to the project repo:

- `design/relay/STATE.md` — single source of truth for who has the ball. Bootstrap content puts `active: human-required` so the human sets the first holder.
- `design/relay/handoffs/.gitkeep` — empty dir for handoff docs to land in.
- `design/relay/config.toml` — participating hosts, mailbox branch, poll interval, default wait timeout. Edited rarely.
- `.gitignore` updates — gitignores the relay's per-host working files (`.wait-status`, `.wait-exit`).

After the skill runs, Derek reviews + pushes, then either edits STATE.md to flip `active` to a real host (or uses the `--initial-active` flag at skill time to bake that into the same commit).

## How this fits with neighbors

- **Relay scripts** live in dotfiles at `~/bin/relay-*` (`relay-status`, `relay-handoff`, `relay-wait`, `relay-flag-human`). The skill DOES NOT install them — they're a dotfiles dependency. It does check for them and warns if missing. Install via `dotpull` if needed.
- **Design doc** for the protocol: `~/code/groot-claude-coord/design/relay/DESIGN.md`. Read that first if you're not familiar with the relay.
- **`/groot-project`** may eventually offer this as a Phase X option for newly bootstrapped projects. For now, run `/relay-setup` separately after `/groot-project` if you want the relay.

## When NOT to run this

- If `design/relay/` already exists in the project — the skill will refuse. To re-initialize, the human deletes the dir first (deliberate action; nothing here should ever be silently clobbered).
- In a non-git directory or one without a remote origin — the relay needs the repo's remote to poll.

## How to invoke

```
/relay-setup
/relay-setup --hosts rocinante24,serenity26
/relay-setup --initial-active rocinante24
```

Run from anywhere inside the target project (the script discovers the project root via `git rev-parse --show-toplevel`).

Before invoking the worker script, **ask Derek**:

1. Which hosts participate? Default: `rocinante24,serenity26`. (Detect his answer; he may add Studio or others.)
2. Which host should hold the ball first? Default: the current host (`hostname`). Optional — if omitted, STATE.md starts at `human-required` and Derek picks later.
3. Which branch is the mailbox? Default: the current branch (usually `master` or `main`).

These prompts use `AskUserQuestion` for cleanest UX. Skip the prompts entirely if the user passed them as CLI args.

## What the worker script does

`~/.claude/skills/relay-setup/relay_setup.py` does:

1. Verify we're in a git working tree with an origin remote. Error out if not.
2. Verify `design/relay/` doesn't exist. Error out if it does (with the message: "already initialized; rm the dir manually to reinitialize").
3. Verify the local hostname is in the chosen hosts list. Warn (not error) if not — Derek may be running setup from a third machine.
4. Create the four files (STATE.md, handoffs/.gitkeep, config.toml, .gitignore additions).
5. `git add` everything that's new or changed.
6. Print a summary: what was created, what the next step is.

Does NOT commit (let Derek review the staged changes first). Does NOT push.

## Smoke test after setup

Once `/relay-setup` runs in the test bed (`remote-coding-setup`) and Derek pushes the bootstrap:

1. On the host that holds the ball, run `relay-status` — should print the current state cleanly.
2. On the other host, after `git pull`, run `relay-status` — same output, confirming the file landed everywhere.
3. Ball-holder runs `relay-handoff test-ack` with a noop body. The script stages a commit. Derek pushes.
4. Other host's `relay-wait` (started after the push) picks up. Cycle confirmed.

## Help

When invoked as `/relay-setup help`, print the following block verbatim:

```
relay-setup — Per-project initializer for the Roci↔Serenity Relay
(cross-host Claude Code handoff protocol).

Usage: /relay-setup [flags]

Flags:
  --hosts <a,b>         Participating hosts. Default: rocinante24,serenity26.
  --branch <name>       Mailbox branch. Default: current branch.
  --initial-active <h>  Bake initial ball-holder into the bootstrap commit.
                        Default: STATE.md starts at "human-required".
  help                  Show this message.

Creates in the project:
  design/relay/STATE.md           Single source of truth for ball-holder.
  design/relay/handoffs/          Where handoff docs land.
  design/relay/config.toml        Hosts, mailbox branch, poll, timeout.
  .gitignore additions            Per-host working files (.wait-status, .wait-exit).

Refuses to clobber:
  Errors out if design/relay/ already exists. Delete the dir manually to
  re-initialize.

Prerequisites:
  Git working tree with an origin remote (the relay polls origin).
  Relay scripts in dotfiles (relay-status, relay-handoff, relay-wait,
  relay-flag-human). Skill checks and warns if missing; install via `dotpull`.

Does NOT commit (lets you review staged changes first). Does NOT push.

Protocol design doc:
  ~/code/groot-claude-coord/design/relay/DESIGN.md

See SKILL.md for full reference.
```

## Background

Full design: `~/code/groot-claude-coord/design/relay/DESIGN.md`. Decision rationale, state machine, failure modes, and the four resolved design questions live there. This skill is just the per-project init step from the "Sequencing for build" footer of that doc.
