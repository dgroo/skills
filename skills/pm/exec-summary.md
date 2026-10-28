# The Executive summary block

_Authored by Claude Fable 5.1 with Derek · Last updated 2026-10-23._

Every story and epic opens with this block, directly under the provenance stamp and the `**Epic:**` line. It is the layer Derek reads with his CEO hat on, between projects; the record below it stays complete. Contract: grootPM `design/stories/ready/at-a-glance-doc-tops.md` (D1–D7) and `work-model-contract.md` § The contract.

## Grammar

```markdown
## Executive summary

**What:** <one sentence: what this document decides or does>  
**Where it stands:** <one line: open / decided <date> / built through increment N of M>  
**Needs you:**

- **Decide** <one line, naming the heading> · **Look** <…> · **Do** <…>
```

- `What` and `Where it stands` together: at most 40 words. Plain words, no rationale, no history.
- The `What` and `Where it stands` lines each end in **two trailing spaces** (a Markdown hard break). Without them the three label lines are one paragraph, and the fleet's `prettier --prose-wrap never` pre-commit hook joins them into a single run-on line (Tessera, 2026-10-28).
- `Needs you` is complete by construction: one bullet per open `<!-- derek(<source>): … -->` mark in the doc and per decision heading marked `· open`, nothing else. Each bullet at most 20 words, opening with a verb label: **Decide** (an answer is wanted), **Look** (a sign-off on something built), **Do** (his hands, a helping-hand). If nothing waits, the line is `**Needs you:** nothing`.
- More than five bullets means the doc is the problem, not the block: write `**Needs you:** N decisions open, § Decisions` and let the one-line decisions list carry them.
- Decision headings carry a status word (`· open`, `· decided 2026-10-19`, `· built`) so Obsidian's Outline shows the state of every decision; the `## Decisions` block is one line per decision (status, pick or recommendation, link) and the full argument lives under `## Decision records`.

## The pass

The block is written by a fresh reader, not the session that wrote the body: a Sonnet subagent that has seen only this brief and the document (the trial on 2026-10-23 showed the grammar and the budget set the quality, not the model). The invoking session then reads the block back against the doc before saving:

1. Facts: every date, count and increment number in the block appears in the body.
2. Completeness: every open mark and every `· open` heading has a bullet; no bullet points at anything closed.
3. Labels: Decide / Look / Do match what the item actually asks.

Run it whenever a skill touches a story: `/ponder` (write), `/pm` (stories it reprioritises), `/wrapup` (stories edited this session), `/cleanup-design` (sweep). The author session writes the first draft at ponder time so the doc has a top from birth; the next pass replaces it.

## Brief for the fresh writer

> You are writing the top of a design document for its reader: a CEO who switches between seventeen projects and other life all day and needs to understand this document in ten seconds without reading it. Read the document in full. Then write ONLY the block below, nothing else.
>
> `## Executive summary` · `**What:**` one sentence · `**Where it stands:**` one line · `**Needs you:**` bullets.
>
> `What` and `Where it stands` together at most 40 words; end each of those two lines with two trailing spaces so they stay separate lines. `Needs you`: exactly one bullet for every open `<!-- derek(…): … -->` mark (a mark is closed when it reads `derek✓`) and for every decision heading marked `· open`; none for anything else. Each bullet at most 20 words, starts with **Decide**, **Look** or **Do**, names the heading it refers to. If there are none, write `**Needs you:** nothing`. If there are more than five, write `**Needs you:** N decisions open, § Decisions` instead. No rationale, no history, no hedging, no "comprehensive". Do not invent an item.
