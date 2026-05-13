---
author: claude
priority: low
---

# Ownership-at-a-glance rework (parked)

## Problem

When `ls`ing the local skills directory, Derek can't tell at a glance which skills are his vs Joe Walnes's upstream. The current solution is `MAINTAINERS.md` at the repo root — a hand-maintained manifest that lists ownership but isn't visible from `ls`.

This is fine today (only 5 Derek-authored skills, and the manifest table is easy to glance at), but if the count grows or import sources multiply (e.g., vendoring from mattpocock/skills or domengabrovsek/claude), the at-a-glance question may sharpen.

## Status

**Parked.** Derek explicitly decided in May 2026 to keep the simple paradigm rather than reorganize. This story exists so the decision is recoverable later.

## Options considered

1. **Parallel top-level dir** (`groot-skills/` next to `skills/`) — clean at-a-glance, requires a small companion Makefile and a 5-skill move.
2. **Naming prefix** (`derek-<name>`) — sorts together, uglifies invocation (`/derek-iterm-setup`).
3. **Description-tag** — per-skill `(derek)` suffix in the SKILL.md description (the mattpocock pattern used by domengabrovsek/claude). Visible in `/`-menu, not at `ls`. Could be added on top of any other option.
4. **Plugin namespacing** — restructure as a proper plugin so invocations become `/groot:<skill>`. Larger structural change; not investigated in depth.

## Trigger to revisit

- Derek-authored skill count crosses ~10
- A second external source is vendored in
- `MAINTAINERS.md` drifts from git history more than once

## Related

- `../../MAINTAINERS.md` — current source of truth for ownership
- domengabrovsek/claude README — pattern for tagging imported skills with their origin
