---
author: claude
priority: medium
---

# Walkthrough rework: iteration-toward-design spine

## Why

Today's `/walkthrough` has grown into a Swiss army knife: 6 verbs (bare / new / integrate / check / clean-comments / follow-ups), a 4×3 scoping grid (modes × registers), a heavyweight 4-artifact `trajectory` mode, and a sibling `/integrate-comments` skill that exists to keep "comment iteration is generic" abstractly true but in practice is only ever called on walkthroughs. The user has stopped using `/integrate-comments` entirely, and the multi-verb surface has accumulated faster than the underlying mental model crystallized.

The mental model the user actually has is simpler and worth being the spine of the skill: **use a human-readable story of the app to iterate on the design**. Draft (CC or human-authored or both) → review → branch (write more analysis / re-imagine the story / push insights into the design) → loop until satisfied → apply changes → archive. The rework collapses the verb surface and scoping ceremony onto that spine.

## Design

### Verb surface (5 verbs)

| Invocation | Action |
|---|---|
| `/walkthrough` (bare) | Smart-route. No walkthrough in expected location → draft. Walkthrough with unseen `@user:` markers anywhere in the dir → `review`. Walkthrough exists, no unseen markers → ask: revise / apply / draft new? |
| `/walkthrough new` | Force-fresh draft regardless of existing state. Used when you want a parallel artifact (e.g., a CC draft alongside your own human draft for the two-input `review` case). |
| `/walkthrough review` | Analyze current state. Auto-detects single-CC / single-human / two-input (compare) cases. Produces analysis in conversation and surfaces the three branches as options. |
| `/walkthrough revise` | Re-imagine `walkthrough.md` from current state + comments + design surface. Marker-acks the prior file, version-asides it, writes a fresh `walkthrough.md`. |
| `/walkthrough apply` | Propose diff of design-surface mutations (story creates / edits / deletes + supporting doc updates), batch-approve, apply, then offer to archive the whole walkthrough dir. |

The three iteration branches (`write review file`, `revise`, `apply`) are reachable both as continuations of `review` and as standalone verb invocations. `revise` and `apply` are top-level verbs; `write review file` is only a continuation of `review` (it's the "persist this analysis" action, not its own operation).

### Retired

- **`/walkthrough integrate`** — old meaning (integrate review comments into prose) gone. Name not reused for the new "integrate into design" semantics; that's `apply` instead, to avoid muscle-memory collisions.
- **`/walkthrough check`** — absorbed into `review`'s auto-detect. When `review` sees a human-authored walkthrough, it runs the 3-way gap-analysis that `check` used to.
- **`/walkthrough clean-comments`** — absorbed into `revise`. Marker-ack (`@user:` → `@user+seen:`) happens automatically on the prior `walkthrough.md` before version-aside.
- **`/walkthrough follow-ups`** — superseded by `apply`. `follow-ups` only staged candidates; `apply` does the diff-first batch-approve + write.
- **`/walkthrough trajectory` mode** — deleted entirely. The 4-artifact build doesn't fit the iteration-toward-design spine. `trajectory.md` sub-file removed.
- **`/integrate-comments` sibling skill** — deleted entirely (not retired-with-shim). The user never calls it; Derek is the only user of this skills directory.

### Draft-time scoping

**Modes survive.** Three options: `current` / `planned` / `infinity` (default). Constrain *sourcing*:

- `current` — code + README + shipped behavior only. Refuses to extrapolate. No `[extrap]` tags.
- `planned` — `current` sources + near-term stories (`stories/ready/`, `stories/drafts/`). `[planned]` tags for not-yet-shipped items.
- `infinity` (default) — everything: code + all stories + speculative design + extrapolation past spec. `[extrap]` tags for anything past spec.

Mode-load is real (sourcing rules affect content correctness), so this stays a scoping question at draft time.

**Registers retired as a formal axis.** Today's `spec` / `grounded` / `storied` triple becomes a one-paragraph guideline in the Draft step:

> Default voice: **grounded** — named protagonist as anchor only. No supporting cast, no sensory micro-scenes (origin stories, screenshots, atmospheric texture). Hold this default unless the user's prompt pins otherwise — "make it spec-shaped" / "concise" / "no fluff" → strip the protagonist to phases; "have fun with it" / "make it a story" / "with characters" → permit cast and texture.

The failure-mode bullet about cast/texture drift survives (it was earned content from the kids-and-partner dogfood case that motivated registers in the first place). Just no longer a four-corner scoping question.

### Iteration mechanics: `review`'s auto-detect + three branches

`review` opens by inspecting the walkthrough dir to choose its mode:

| Dir state | Action |
|---|---|
| 0 walkthroughs | Ask: draft? |
| 1 walkthrough, CC-authored | Standard analysis of `walkthrough.md` + any comments + any `review-N.md` files |
| 1 walkthrough, human-authored | 3-way gap-analysis (narrative ↔ design ↔ code) — today's `check` behavior |
| 1 CC + 1 human walkthrough | Compare-style synthesis review |

**Authorship detection signals** (any one is sufficient):
- Frontmatter declares author/source
- Marker style: `@user:` review markers → CC-authored target of review; `[[design-actionable]]` / `((aside))` markers → human-authored intent doc
- Filename convention if present (`walkthrough.md` vs `walkthrough-human.md`)
- Fallback: ask

Output: analysis in conversation. CC then surfaces the three branches:

1. **Write review file.** Persist the analysis as `review-<N+1>.md` (next available number). Before writing, marker-ack any `@user:` markers on prior files (`walkthrough.md`, `review-1.md..N.md`). The new review file is now a comment-able artifact in its own right — adding `@user:` markers to it and re-running `review` continues the loop.
2. **Revise.** See below.
3. **Apply.** See below.

### Revise mechanics

When `/walkthrough revise` fires:

1. Read `walkthrough.md` (with any `@user:` markers).
2. Rewrite those markers to `@user+seen:` in place. Preserves provenance — the prior file shows what was considered, even if the user never re-reads it.
3. Read all `review-N.md` files; marker-ack their `@user:` too.
4. Move the current `walkthrough.md` to `walkthrough-v<N+1>.md` (next available number). Review files stay in place — they're already chained.
5. Write a fresh `walkthrough.md`, re-imagining the story informed by: prior walkthrough content, all comments (now seen-marked), all review files, current design surface.
6. Surface a brief summary in conversation of what shifted vs. the prior version (1-3 bullets, not a diff).

**Not a surgical weave.** This is a genuine re-draft — fresh prose informed by the conversation, not edits-in-place. The prior version is preserved on disk (with seen markers) and in git.

### Apply mechanics

When `/walkthrough apply` fires:

1. Synthesize from current `walkthrough.md` + all `review-N.md` + comments into a **proposed diff** covering:
   - Story file creates (`design/stories/drafts/<slug>.md`, with frontmatter matching repo convention)
   - Story file edits (existing `drafts/` or `ready/` stories)
   - Story file moves (e.g., draft → ready, ready → done, or → archived)
   - Updates to supporting design docs the project treats as canonical (`README.md`, `CLAUDE.md`, `DESIGN.md`, etc.)
2. Surface the full diff in conversation. The user can:
   - Approve the batch
   - Reject individual items (CC re-renders the remaining set)
   - Ask for revisions to a specific item
3. On approval, CC applies all changes.
4. CC asks: "Move `design/walkthroughs/<date>-<slug>/` to `design/walkthroughs/archived/<date>-<slug>/`?" User confirms; CC moves (or doesn't).

### Artifact model

Flat versioned dir:

```
design/walkthroughs/<YYYY-MM-DD>-<slug>/
  walkthrough.md           ← current
  walkthrough-v1.md        ← prior, with @user+seen: markers preserved
  walkthrough-v2.md        ← prior-prior
  review-1.md              ← chained, never overwritten
  review-2.md
  review-3.md
```

After archival, the whole dir moves to `design/walkthroughs/archived/<YYYY-MM-DD>-<slug>/`. Per the global rule about `archived/` directories, future sessions treat its contents as read-with-permission.

### Bare smart-route logic

`/walkthrough` (bare) decides what to do by inspecting the expected walkthrough dir:

- No dir / no walkthroughs in expected locations → draft (run scoping pass)
- Walkthrough dir exists with unseen `@user:` markers in `walkthrough.md` or any `review-N.md` → `review`
- Walkthrough dir exists, no unseen markers → ask: `revise` / `apply` / draft new?

The expected dir is determined by the existing auto-discovery rules: `design/walkthroughs/`, falling back to `design/notes/`, `notes/`, `docs/walkthroughs/`, `docs/`. When multiple candidates exist, ask (don't guess).

## Out of scope

- Pre-/post-rework migration of existing in-flight walkthroughs. The user's existing walkthrough dirs use today's conventions and can be left alone (they're either already shipped or already archived); the new conventions apply to walkthroughs drafted after the rework lands.
- A new LLM-companion doc shape. The current optional LLM-companion artifact survives unchanged if needed; it's orthogonal to the iteration spine.
- Multi-author review markers. The skill assumes one reviewer (Derek). If multi-user review ever becomes a thing, the `@user:` namespacing already supports it; nothing in the rework precludes it.

## Migration / cleanup

When the rework lands:

1. Edit `skills/walkthrough/SKILL.md` — rewrite Routing, Modes (drop trajectory + register sections), Draft / Iterate sections, retire Check / Follow-ups / Clean-comments / Integrate sections. Update Help block and Quick Reference.
2. Delete `skills/walkthrough/trajectory.md`.
3. Delete `skills/integrate-comments/` entirely.
4. Update `README.md` Skills table to remove `integrate-comments` row.
5. Update `MAINTAINERS.md` to remove `integrate-comments` row.
6. Update any cross-references in other skills (e.g., `/walkthrough` mentions in `cleanup-design`, `sup`, etc.).
7. `make install` to refresh symlinks.
8. DIARY entry capturing the rework rationale and the retired-skill decision.

## Related

- `skills/walkthrough/SKILL.md` — target of the rework
- `skills/integrate-comments/SKILL.md` — to be deleted
- `skills/walkthrough/trajectory.md` — to be deleted
- DIARY 2026-05-23 — `/walkthrough integrate` alias decision (the "I keep forgetting integrate-comments exists" precedent that motivates the full retirement here)
- `MAINTAINERS.md` — ownership manifest
