---
name: subagent
description: Use when asked to delegate a task to a subagent via the Agent / Task tool ("spawn a subagent", "do this in a subagent", "subagent for that", "/subagent"). Runs a four-check evaluation (result-shape, size, context-savings, decision-load) and either spawns with a well-formed prompt OR pushes back with specific reasons. User override always wins; the skill's job is to make the heuristic legible, not to overrule judgment.
argument-hint: [task description]
---

# subagent

Evaluate whether a task is actually suited to a subagent, then either spawn it (with a prompt that gives the subagent enough context to make good calls) or push back with specific reasons. The skill's value is the pushback — without it, this is a manual override that loses Claude's judgment for no gain.

## When to use vs. skip

Use for: "spawn a subagent for X", "do this in a subagent", "delegate to a subagent", "/subagent <task>", "/subagent" (bare → prompt for the task), or when _you_ (Claude) are considering reaching for the Agent/Task tool and want a sanity check first.

Skip if: the user has already weighed the tradeoff out loud and is explicitly directing dispatch ("just spawn it, I've thought about it"). Run the spawn step only — no evaluation theater. The user override case below covers post-hoc overrides; this skip covers pre-emptive ones.

## Routing

| Invocation                                                 | Action                                                              |
| ---------------------------------------------------------- | ------------------------------------------------------------------- |
| `/subagent <task description>`                             | Run the four-check evaluation on the task, then spawn or push back. |
| `/subagent` (bare)                                         | Prompt the user for the task description, then run the evaluation.  |
| User-style: "do X in a subagent" / "spawn a subagent to Y" | Same as `/subagent X` — run the evaluation.                         |

## Four-check evaluation

Run all four. Each comes back **green** (subagent OK), **yellow** (mild concern), or **red** (push back).

### 1. Result-shape

What flows back into the main conversation?

- **Green:** a summary, a list of findings, a short artifact (file path, function signature, a diff), a yes/no answer with citation. Anything that re-enters the parent agent as a discrete payload.
- **Yellow:** a result that the parent will need to ask follow-up questions about, but the follow-ups are factual ("which file was it in again?").
- **Red:** the result is _entangled_ with this conversation's in-flight decisions and taste calls — e.g., the parent has been weighing approach A vs B and the subagent would need to know which way that's leaning to do the work. Subagents start cold; entanglement is the failure mode.

### 2. Size

How much read-only work is the task?

- **Green:** more than ~5 tool calls (deep search, multi-file audit, large doc read, complex grep-then-read chain). Spawning overhead is amortized.
- **Yellow:** 3-5 calls. Borderline. If the result-shape is clean, OK; if not, do it inline.
- **Red:** 1-2 quick reads. Spawning overhead is the entire cost of the task. Just do it.

### 3. Context-savings

Does the work generate heavy output that would pollute the parent's context if done inline?

- **Green:** the subagent will read long files, run big greps, scan dozens of matches, audit a multi-module subsystem — and the parent only needs the conclusion. This is the canonical subagent win: the parent never sees the noise.
- **Yellow:** moderate output (a handful of file reads). The savings exist but aren't dramatic.
- **Red:** the work generates tiny output that wouldn't pollute anything. No context to save.

### 4. Decision-load

Does the task require taste calls / judgment tied to nuance the parent agent has built up in this conversation?

- **Green:** task is mechanical (find all callers of X, list files matching a pattern, summarize a doc). Judgment doesn't depend on conversational nuance.
- **Yellow:** some judgment required, but it can be specified in the prompt up front ("prefer matches in `src/` over `tests/`").
- **Red:** the task requires taste calls the parent has been building toward — "is this the right place to put this?", "does this match the style we've been converging on?", "is this consistent with what we decided 20 turns ago?". The subagent starts cold and **cannot** reconstruct that nuance from a prompt without losing fidelity. **Push back hard.**

## Verdict

| Pattern                          | Action                                                                                                                                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| All green, or 3 green + 1 yellow | **Spawn.** Default to `general-purpose`; recommend a more specialized type if one obviously fits (see below).                                                                              |
| 2+ yellow, no red                | **Spawn with caveats.** Note the yellow flags in the prompt itself so the subagent works around them.                                                                                      |
| 1 red, rest mixed                | **Push back.** Cite the specific check and reason. Offer to either (a) do the task inline, (b) restructure the task so the red flag goes green, or (c) spawn anyway if the user overrides. |
| 2+ red                           | **Push back firmly.** This task wants to be inline. Explain why each red triggered. Spawn only on explicit user override.                                                                  |

**User override always wins.** If Derek says "do it anyway" or "I know, spawn it", spawn. The skill is a heuristic surface, not a gate. Note the override in the spawn prompt so the subagent knows it's operating outside the skill's recommendation (helps it ask for clarification if it hits the entanglement it was warned about).

## Subagent-type selection

Map task shape to subagent type. Recommend the type in the verdict; user can override.

| Task shape                                                                   | Recommended type                                            | Why                                                                             |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Pure search / "find all X" / "where is Y defined"                            | `Explore`                                                   | Optimized for read-only discovery; cheaper than general-purpose for this shape. |
| Planning / architecture exploration / "design how we'd…"                     | `Plan` (if available) or `general-purpose`                  | Result-shape is a plan doc; the parent will review.                             |
| Multi-step research / audit / code-surface analysis                          | `general-purpose`                                           | Catch-all for "read a lot, summarize a little."                                 |
| Implementation of a self-contained slice (rare — usually wants to be inline) | `general-purpose`                                           | Only if the slice is genuinely independent and the result-shape is a diff/PR.   |
| Specialized domain (security review, perf audit, docs writing)               | Domain-specific agent if registered, else `general-purpose` | Check `~/.claude/agents/` or the current session's available agent list.        |

If the user named a type explicitly, use that — don't second-guess type choice unless it's obviously wrong (e.g., `Explore` for an implementation task).

## Prompt-writing guidance

A subagent prompt should give the subagent enough context to make good calls without re-litigating the conversation. The Agent tool's own description in the system prompt covers this; the skill enforces it in practice. Minimum prompt content:

- **What's being accomplished.** The actual goal in one or two sentences. Not "search for X" — "find where X is set so we can decide whether to refactor Y, which depends on X's lifecycle."
- **What's been ruled out / decided already.** If the parent already considered and rejected approach A, say so. Otherwise the subagent will independently rediscover A and propose it.
- **Constraints from the current conversation.** Style conventions, taste calls, scope boundaries the parent has been honoring. ("Don't propose changes to `legacy/` — that subtree is frozen.")
- **Result shape expectations.** "Return a list of file paths with one-line summaries" vs "return a markdown plan doc" vs "return yes/no with citation". The subagent will optimize toward whatever shape it thinks fits; pin it down.
- **Tool constraints if relevant.** "Read-only, don't edit anything." "WebFetch is denied in this session, don't try." "Stay out of `node_modules/`."

When in doubt, **show the prompt to the user before spawning** for non-trivial subagent invocations. A 2-line review beats a 5-minute misfire.

## Common mistakes

- **Spawning a subagent for a 2-file read.** The overhead exceeds the work. Just read the files.
- **Spawning to "save context" when the result-shape would entangle anyway.** If the parent needs the subagent's reasoning, not just its conclusion, you haven't saved context — you've added a round trip.
- **Forgetting to surface the override path.** If the heuristic says push back, the user can still say "do it anyway." Make that path explicit in the pushback, don't make Derek argue with the skill.
- **Default-spawning `general-purpose` when `Explore` would do.** Type selection matters. Pure search wants `Explore`; planning wants `Plan`.
- **Thin prompts.** "Find all callers of foo" gives the subagent no scope. "Find all callers of foo in `src/idm/` so we can decide whether renaming foo is safe — return a list of file:line with the calling function name" is actionable.
- **Skipping the evaluation when _Claude_ is the one reaching for the tool.** This skill applies whether the user invoked it or Claude is about to spawn unprompted. The check is on the _task_, not the _requester_.

## Quick reference

| Check           | Green                                        | Yellow                    | Red                                    |
| --------------- | -------------------------------------------- | ------------------------- | -------------------------------------- |
| Result-shape    | summary / artifact                           | factual follow-ups likely | entangled with in-flight decisions     |
| Size            | >~5 tool calls                               | 3-5 calls                 | 1-2 quick reads                        |
| Context-savings | heavy output (long reads, big greps, audits) | moderate                  | tiny output                            |
| Decision-load   | mechanical                                   | spec-able in prompt       | taste calls from conversational nuance |

| Verdict           | Action                                           |
| ----------------- | ------------------------------------------------ |
| all green / 3G+1Y | Spawn                                            |
| 2+ Y, no R        | Spawn with caveats in prompt                     |
| 1 R               | Push back, offer inline / restructure / override |
| 2+ R              | Push back firmly; spawn only on override         |

| Task shape                             | Recommended type                                        |
| -------------------------------------- | ------------------------------------------------------- |
| Search / discovery                     | `Explore`                                               |
| Planning / architecture                | `Plan` or `general-purpose`                             |
| Multi-step research / audit            | `general-purpose`                                       |
| Self-contained implementation          | `general-purpose` (rare; usually wants inline)          |
| Domain-specific (security, perf, docs) | Specialized agent if registered, else `general-purpose` |

## Help

When invoked as `/subagent help`, print the following block verbatim:

```
subagent — Evaluate whether a task is suited to a subagent; spawn or push back.

Usage: /subagent [task description]

Verbs:
  <task>            Run the four-check evaluation, then spawn or push back.
  (none)            Prompt for the task description, then evaluate.
  help              Show this message.

Four-check evaluation (each: green / yellow / red):
  1. Result-shape       Discrete payload OR entangled with in-flight decisions?
  2. Size               >5 calls (green) / 3-5 (yellow) / 1-2 (red)
  3. Context-savings    Heavy output that pollutes inline? Or tiny?
  4. Decision-load      Mechanical? Or taste-call-from-conversation?

Verdict:
  all green / 3G+1Y    Spawn.
  2+ yellow, no red    Spawn with caveats in prompt.
  1 red                Push back; offer inline / restructure / override.
  2+ red               Push back firmly; spawn only on explicit override.

Subagent-type recommendations:
  Search / discovery                       Explore
  Planning / architecture                  Plan or general-purpose
  Multi-step research / audit              general-purpose
  Self-contained implementation            general-purpose (rare)
  Domain-specific (security, perf, docs)   specialized if registered

User override always wins ("do it anyway" → spawn, noting override in prompt).

See SKILL.md for full reference.
```

## Related

- The Agent / Task tool description in the global system prompt — authoritative for what a good subagent prompt looks like.
- Derek's global CLAUDE.md "Explore before acting" / "Push back when something seems wrong" — this skill is that principle applied to subagent dispatch.
