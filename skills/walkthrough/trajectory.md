# Trajectory mode

Sub-procedure for the `walkthrough` skill. Load when the user has chosen `trajectory` mode during scoping; not needed for `current`, `planned`, or `infinity`.

## Purpose

Produces a four-artifact set in one run, built **iteratively** so the three narratives share spine and only diverge at extrapolation points. Use when the user wants to compare the three eras side-by-side or surface what each next layer unlocks.

## Procedure

1. **Draft `current`.** Generate the `current`-mode walkthrough end-to-end using only shipped behavior. Save as `<date>-walkthrough-<scenario>-<perspective>-current.md`.
2. **Extend to `planned`.** Re-draft using `current` as the spine: keep the same protagonist, scenes, and beats; layer in `[planned]` items where the next milestone changes the experience. Don't rewrite passages the planned work doesn't touch. Save as `...-planned.md`.
3. **Extend to `infinity`.** Re-draft using `planned` as the spine; layer in `[extrap]` for end-state speculation. Save as `...-infinity.md`.
4. **Synthesize.** Write a fourth sibling `...-trajectory.md` that's structurally a *comparison*, not a narrative:
   - **What's real today** — one-paragraph recap of `current`.
   - **What unlocks next** — the deltas from `current` → `planned`, grouped by which user-facing capability they enable.
   - **The long arc** — the deltas from `planned` → `infinity`, called out as aspirational with surfaced spec gaps.
   - **Open questions** — pulled from `[extrap]` density: where the three diverge most aggressively is where the spec is thinnest.

## When the spine diverges

If a `planned` or `infinity` layer fundamentally changes the protagonist's flow (different entry point, different primary loop), don't force the same spine. Call out the divergence in the framing-note of that artifact and let the narrative re-shape. The synthesis surfaces these as "trajectory-breaks."

## Cost

Four artifacts is heavy. Confirm before running unless the user explicitly asked for trajectory mode. Most asks want one mode, not all four.
