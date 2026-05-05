---
name: prior-art
description: 20-minute prior-art check before building a new project. Surfaces 1-3 closest existing tools, asks the forcing question ("what's your honest reason to build anyway?"), and ends with a one-line judgment. Two modes — hobby/learning (light touch, valid honest reasons explicitly include taste, fun, learning) and startup-track (sharper questions about incumbent assumptions and reframes). Use when the user describes a new project idea ("I want to build X", "thinking about a tool that does Y", "is there already something that does this?", "should I build this or use something off the shelf"), or invoked as /prior-art. Run before /office-hours when both apply — prior-art findings sharpen the office-hours conversation. Skip for changes inside an existing project; this is for new project ideation only.
allowed-tools:
  - AskUserQuestion
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Bash
---

# Prior Art Check

A 20-minute structured check before starting a new project. Catches the case where something already does most of what the user wants, *without* talking them out of projects worth building anyway.

This skill is opinionated about its own scope. **It does not decide whether to build.** It surfaces what exists, asks one forcing question, names which research-risk patterns are showing up in the conversation, and ends with a single-line judgment the user can accept or override.

## When this skill applies

- The user is describing a *new* project idea (no code yet, no repo yet, or they've just started one)
- They've used phrases like "I want to build", "thinking about", "should I build", "is there a tool that does"
- Or they invoked `/prior-art` directly

## When to skip

- The work is inside an existing project (feature, refactor, bugfix) — not applicable
- The user has already made it clear they're committed regardless ("I know X exists, I'm building this anyway") — confirm and skip the forcing question, but still surface what exists in case they want to learn from it
- The "project" is a one-off script or throwaway prototype

## Process

### Step 0: Capture the idea

In one or two sentences, what is the user trying to build, and who is it for? If unclear, ask once. Don't enter brainstorming mode — that's `/office-hours`'s job.

If the user has just described an idea that's *also* a fit for `/office-hours`, mention that this skill runs first and `/office-hours` is the natural next step. Don't run both back-to-back without checking.

### Step 1: Pick the track

```
AskUserQuestion: Which track applies here?
  Options:
    - Hobby / learning / fun — I'm building this for me, don't have to justify it commercially
    - Startup-track — I'm considering this as a real product or business
    - Not sure yet — treat as startup-track (sharper questions, less harm if hobby)
```

Track determines question depth. **Don't change tracks mid-flow.**

### Step 2: Find the closest existing tools (max 20 minutes wall-clock)

Use `WebSearch` to find 1-3 things that already exist in this space. **Cap at 3.** More than 3 is research procrastination dressed as thoroughness.

For each, gather only:
- Name and one-line description
- What it does well
- What it does poorly (UX, pricing, OSS health, abandonment, lock-in)
- Whether the user already knows about it

**Hard rules:**
- **No deep source-code reading.** Avoid IP contamination. Read product pages, docs, README, top-level comparison posts. Skip the GitHub source tree.
- **No "comprehensive landscape survey."** You're looking for the closest 1-3, not a market map.
- **Time-box yourself.** If 20 minutes elapses without 1-3 candidates, stop and tell the user the space is either very crowded (different problem — see Risk Callouts) or very empty (worth noting — Status Quo Q from office-hours applies).

If the user already knows the space, ask them for the candidates instead of searching. Their domain knowledge beats web search.

### Step 3: The forcing question

Present the 1-3 candidates in a short table or list. Then ask exactly this:

> What comes closest to what you want to build, and what's your honest reason to build it anyway?

**Valid honest reasons** — name them out loud so the user knows they're allowed:

- **Learning.** "I want to understand how X works by building one."
- **Taste / craft.** "The existing thing is ugly / annoying / wrong-feeling and I want to live in mine."
- **Fun.** "It would be fun to build."
- **Control / ownership.** "I want to own the data, the code, the future direction."
- **Reframe (startup-track).** "The incumbents have framed this problem wrong; my framing is better."
- **Wedge (startup-track).** "There's a specific user segment the incumbents don't serve."
- **Speed of iteration.** "I can ship faster than the incumbent's release cycle."
- **The incumbent is dying.** "Last commit was 2 years ago / company pivoted / pricing got hostile."

**Not valid by themselves** (probe further if these are the answer):
- "It would be fun to add AI to it" — usually differentiation theater (see Risk Callouts)
- "Mine would be better" with no specifics — vague; ask what specifically
- "I'd add features X, Y, Z" without a user need — feature creep dressed as a thesis

### Step 4: Active risk callouts

Watch for these patterns in the user's reasoning. **Name them out loud when they appear** — don't lecture, just flag.

Order roughly by frequency:

1. **Anchoring on incumbent framing.** User describes their idea in the incumbent's vocabulary ("a better Notion", "Slack but for X"). Flag: "you're framing this as incumbent + delta — what would the problem look like if [incumbent] didn't exist?"
2. **Demoralization from competitor count.** "There are like 5 things that already do this." Flag: survivorship bias — they only see live competitors, not the graveyard. Crowded markets often = validated demand + bad incumbents (the YC-favored shape).
3. **Differentiation theater.** "Mine would be the same but with [AI / for vertical / open source]." Flag: positioning-driven, not user-driven. What's the user pain that drives the difference?
4. **Premature competitive paranoia.** Talking about moats and defensibility before product-market fit. Flag: speed of shipping is the only moat that matters early.
5. **The "if it existed I'd use it" fallacy.** "X already does this so I shouldn't build it." Flag: existence ≠ obsolescence. Many incumbents have terrible UX or pricing that excludes real segments. The right question is *what's broken about my relationship with X*, not *does X exist*.
6. **Procrastination disguised as research.** Conversation has been about competitors for >20 minutes. Flag: time's up, make a call.
7. **IP contamination risk** (rare). User is reading source code of a similar OSS tool with intent to commercialize. Flag: clean-room matters if licensing changes later.

Hobby track: callouts 1, 3, 6 still apply. Skip 2, 4, 5, 7 unless the user explicitly raises them.
Startup track: all apply.

### Step 5: One-line judgment

End with exactly one of these shapes (don't hedge into a paragraph):

- **"Use [X]."** — Existing tool covers the user's stated need with no compelling reason to build. The user can override; this is just the call from this skill.
- **"Build it. Honest reason: [reason]."** — Existing tool doesn't cover it, OR it covers it but the user has a valid honest reason that holds up.
- **"Probably build it, but [specific concern]."** — Lean toward building with one named concern to revisit (e.g., "watch for anchoring on Notion's framing during design").
- **"Don't build yet — [missing thing]."** — Used rarely. Reserved for: idea is incoherent, user can't name a target user, user is in research-procrastination mode.

The user can override any of these. **Do not argue past one round.** If they say "build it anyway," accept and move on.

### Step 6: Capture

If the project has a `design/` directory (per the user's CLAUDE.md convention), write findings to `design/prior-art-<short-name>.md` with:

- Date
- One-sentence idea
- Track (hobby / startup)
- Closest 1-3 candidates with the what-it-does-well / what-it-does-poorly notes
- Honest reason from Step 3
- Risk callouts that fired
- Final one-line judgment

If no `design/` directory exists, ask whether to create one or skip writing. Don't silently create files outside an established project.

If `/office-hours` is the natural next step, suggest it after Step 6.

## Voice

Direct, peer-level. No founder cosplay. No "great question!" Don't lecture about competitive dynamics; flag patterns when they appear and move on. The user is technically deep — they don't need market-research jargon.

## What this skill is not

- Not a market sizing tool. Not a competitive intelligence tool. Not a feature-comparison matrix generator. Not `/office-hours` (which handles the broader idea-validation question).
- Not a kill-switch. The default outcome is *build it with eyes open*, not *don't build*.
- Not exhaustive. 1-3 candidates, 20 minutes, done.
