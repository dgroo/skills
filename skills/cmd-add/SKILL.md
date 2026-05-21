---
name: cmd-add
description: Use when proposing a new Claude Code slash command — gates command-vs-skill, scans for collisions, writes the file at ~/.claude/commands/, and shows the propagation command for dot-claude. Triggers on "/cmd-add <description>", "I want a shortcut for…", "let's add a slash command for…", "make /<name> do X".
argument-hint: <one-line description of what the command should do>
---

# Add a Slash Command

Lighter sibling of `/skill-add`. Slash commands are user-triggered prompt expansions — markdown files at `~/.claude/commands/<name>.md` whose body becomes the prompt sent to Claude. They cost nothing at session start (unlike skills, whose descriptions live in context every session), so they're the right default for "I want a shortcut."

The one decision this skill makes loudly: **command or skill?** A command if you'll always explicitly type `/<name>`; a skill if you'd ever want Claude to invoke it proactively when context matches. When in doubt → command. A command can be promoted to a skill later by adding a `SKILL.md` with a `description:` that tells Claude when to fire. The reverse (skill → command) is harder because Claude has already learned to invoke it.

## How to Invoke

```
/cmd-add /cpush — commit atomically then push
/cmd-add a shortcut that opens the last failing test in $EDITOR
/cmd-add            # no args — ask for the proposal
```

If invoked with no argument, ask: *"What's the command — name and one-line behavior?"*

---

## Phase 1: Capture

Pin down three things:

1. **Name** — the slash trigger (`/<name>`). Lowercase, kebab-case, short. If the user gave it, use it; otherwise propose one.
2. **Prompt body** — what should expand into Claude's input when invoked? Often one sentence; can be a paragraph for richer shortcuts. The user's words are the spec — sharpen only if vague.
3. **Arguments?** — does invocation take input the user types after `/<name>`? If yes, the body should reference `$ARGUMENTS`. If no, skip.

Echo back so the user can correct before evaluation.

---

## Phase 2: Evaluate

### 2a. Should this be a skill instead?

The single most important gate. Ask one question:

> "Would you ever want Claude to invoke this on its own — when the situation matches — even if you didn't type `/<name>`?"

- **No, only when I type it** → proceed as command (default).
- **Yes, proactively in matching situations** → defer to `/skill-add`. Recommend it explicitly and do not proceed here.

If the user is unsure, lean command. Promotion later is cheap; demotion is not.

### 2b. Collision check

```bash
ls ~/.claude/commands/ 2>/dev/null
ls ~/.claude/skills/ 2>/dev/null
```

Look for:

- **Exact name match** in `commands/` — must rename.
- **Same name as an installed skill** — slash commands and skills share the `/<name>` namespace; a command can shadow a skill. Flag it.
- **Near-name match** — flag potential confusion (e.g., `/cpush` vs `/push`).

### 2c. Value check

A two-second sanity gate:

| Check | If yes, suggest instead |
|-------|------------------------|
| **Is this really a rule, not a shortcut?** ("always X before Y") | `/claude-md-add` |
| **Is this just a shell alias in disguise?** (`/build` → `make build`) | A shell alias in `~/.shrc` |
| **Will future-you actually type the trigger?** Abstract verbs (`/do`, `/run`) get forgotten | Concrete verbs (`/cpush`, `/amend`) |

When the value is thin, name the cheaper alternative before recommending against.

---

## Phase 3: Decide

Present findings in one block:

```
**Proposal:** /<name> — <one-line behavior>

**Body:** "<the prompt that will expand>"
**Arguments:** <none / $ARGUMENTS shape>
**Collisions:** <none / list>
**Command vs skill:** command (user-triggered only) — confirmed
**Value:** <earns its keep / borderline (reason) / thin (cheaper alternative is X)>

**Recommendation:** <proceed / rename to Y / use /skill-add instead / use /claude-md-add instead / skip>
```

Wait for: **proceed / modify / abandon.**

---

## Phase 4: Create

1. **Write `~/.claude/commands/<name>.md`.** Minimal frontmatter — only what's actually needed:

    ```markdown
    ---
    description: <one-line for /help listing>
    argument-hint: <only if the command takes arguments>
    ---

    <prompt body — references $ARGUMENTS if applicable>
    ```

    For a one-line shortcut with no arguments, frontmatter is optional. The bare body is enough:

    ```markdown
    Commit all current changes as atomic commits, then push.
    ```

2. **Don't commit.** Show the user the exact command to land + propagate to other machines via dot-claude:

    ```bash
    cd ~/.claude && git add commands/<name>.md && git commit -m "commands: add /<name> — <one-line>" && git push
    ```

    Don't run it. The user runs it (or invokes `/cpush` once they've added that one).

3. **Show the result.** Path, body, and the propagation hint.

---

## Guidelines

- **Default to command, defer to skill only on demand.** Skills cost context every session; commands cost nothing until used. If the value of proactive invocation isn't concrete, it isn't worth the session-tax.
- **One command in, one command out.** Don't propose adjacent commands the user didn't ask for. Mention them only if relevant.
- **Match the user's voice in the body.** The prompt body is what Claude reads — it should sound like the user telling Claude what to do, not a third-party description.
- **Frontmatter is optional.** For a one-liner with no args, just the body. Use `description:` when the command will appear in `/help` listings and benefits from a label; use `argument-hint:` only if `$ARGUMENTS` is referenced.

## Help

When invoked as `/cmd-add help`, print the following block verbatim:

```
cmd-add — Add a Claude Code slash command. Gates command-vs-skill, then writes the file.

Usage: /cmd-add [<pitch>]

Arguments:
  <pitch>           Free-form description of the command. If omitted, the skill asks.

Phases:
  1. Capture        Pin down name, prompt body, arguments.
  2. Evaluate       Command-vs-skill gate, collision check, value check.
  3. Decide         Present findings; user picks proceed / modify / abandon.
  4. Create         Write ~/.claude/commands/<name>.md, show propagation command.

See SKILL.md for full reference.
```

## Related

- **`/skill-add`** — for proposing a *skill* (proactive, context-loaded). Used when the answer to "would you want Claude to invoke this on its own?" is yes.
- **`/claude-md-add`** — for a one-off *rule*, not a shortcut. Used when the user wants behavior, not a trigger.
