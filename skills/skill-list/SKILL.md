---
name: skill-list
description: List installed Claude Code skills, grouped by source. Use when asked to "list skills", "what skills do I have", "show my skills", "/skill-list", or "/skill-list <group>". Subcommands — (no arg) same as `make list`; `all` everything grouped; `groups` available group names; `<group>` one of mine/gstack/installed/plugins/upstream. Fast — just shells out to a script and prints the output verbatim.
argument-hint: "[all | groups | mine | gstack | installed | plugins | upstream]"
allowed-tools: Bash
---

# Skill List

Run the script and print its output **verbatim**. No analysis, no commentary, no summary. The script is the answer.

```bash
bash ~/code/claude/skills/scripts/skill-list.sh "$ARGUMENTS"
```

That's it. One bash call, print the output, stop.
