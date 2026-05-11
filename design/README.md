# Design — dgroo/skills

Design artifacts for this skill fork. Most thinking about how the fork is organized lives here rather than at the repo root, to keep the root clean for skill bootstrapping (which is what people land on).

## What's here

```
design/
├── README.md           # this file
├── DESIGN.md           # high-level shape of the fork (what we keep vs override from joewalnes/skills)
├── stories/            # feature specs, readiness-by-directory (drafts/ready/done) — see stories/README.md
├── plans/              # dated implementation plans, when a change is non-trivial
├── helping-hands/      # asks needing the human
└── notes/              # informal materials
```

This subtree follows the same convention `/groot-project` bootstraps elsewhere, so the fork dogfoods its own model.

## Why a design/ here

Two reasons:

1. **Parking lot for revisits.** Ideas that aren't ready to act on but shouldn't be forgotten live in `stories/drafts/`.
2. **Self-consistency.** If the convention is good enough to bootstrap into projects, it's good enough to use on the tool that bootstraps it.
