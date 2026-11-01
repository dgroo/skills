# The Executive summary block

_Authored by Claude Fable 5.1 with Derek · Last updated 2026-11-01._

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

The block is written by a fresh reader, not the session that wrote the body: a Sonnet subagent that has seen only the brief and the document (the trial on 2026-10-23 showed the grammar and the budget set the quality, not the model). The invoking session reads the block back against the doc, writes it, and checks it with the reader. One procedure, run from three skills; none of them restates it.

**When, and on which stories.** `/wrapup` runs it on the stories this session edited (Phase 3, after the body edits and before anything lands); `/pm`'s pass on the stories it demoted, rewrote or reprioritised (`review.md` §4); `/cleanup-design` on every live story the reader marks `missing` or `stale` (its `refresh-summary` bucket). `/ponder` is the exception: the author writes the first block so the doc has a top from birth, and the next pass replaces it. `/pm` intake does not run it: a captured addition bumps the stamp and leaves the block, so the story reads amber until the next `/wrapup` or pass, which is the board doing its job. Always skipped: `done/` stories (the board shows them no amber and the backfill does not reach them) and `/story` stubs, recognised by their marker line (`**Captured via `/story` — not yet pondered.**`): a stub has no block until it is pondered, the reader reports it `missing`, and the pass leaves it alone.

**The procedure, per story.** Several stories get one writer each, spawned in one message.

1. **Spawn the writer.** `Agent`, `model: "sonnet"`, `subagent_type: "general-purpose"`. The prompt is the brief below, verbatim, followed by one line: `The document is <absolute path>. Read it in full yourself.` Nothing else: no session context, no hint of what changed, no paste of the document. A reader with no sunk cost in the body is the mechanism.
2. **Read it back** against the doc, yourself:
   1. Facts: every date, count and increment number in the block appears in the body.
   2. Completeness: every open mark and every `· open` heading has a bullet; no bullet points at anything closed.
   3. Labels: Decide / Look / Do match what the item actually asks.

   One slip: fix the line yourself. More than one: spawn the writer once more; if that block slips too, write the block yourself and say so in the recap.
3. **Write it.** Replace the existing section from the `## Executive summary` heading up to the next `#` or `##` heading; when there is none, insert the block directly under the stamp and the `**Epic:**` line, a blank line on each side. Keep the two trailing spaces. Change nothing else in the file, and do not bump the stamp for this: the block is the doc's top, not a substantive edit of the record. An identical block means nothing to write.
4. **Check it with the reader.** From the project root, the story's `summary_status` must be `ok`:

   ```sh
   backlog-scan --json | jq -r '.stories[] | select(.path == "design/stories/<tier>/<slug>.md") | "\(.summary_status) \(.summary_issues)"'
   ```

   The reader parses the grammar and counts the doc's open marks and `· open` headings against the bullets, so this catches what the read-back missed. Anything but `ok` goes back to step 2; the issues say what is wrong.
5. **Land it last.** The pass is the final write to a story before it lands: the reader calls a block stale when the stamp's date is newer than the block's last commit, so a stamp bumped after the block was committed turns the card amber. In a design-synced repo the watcher commits it; elsewhere commit with a pathspec (`docs(design): refresh the Executive summary on <slug>`).

## Brief for the fresh writer

> You are writing the top of a design document for its reader: a CEO who switches between seventeen projects and other life all day and needs to understand this document in ten seconds without reading it. Read the document in full. If it already has a `## Executive summary`, disregard it and write from the body; your block replaces it. Then write ONLY the block below, nothing else.
>
> `## Executive summary` · `**What:**` one sentence · `**Where it stands:**` one line · `**Needs you:**` bullets.
>
> `What` and `Where it stands` together at most 40 words; end each of those two lines with two trailing spaces so they stay separate lines. `Needs you`: exactly one bullet for every open `<!-- derek(…): … -->` mark (a mark is closed when it reads `derek✓`) and for every decision heading marked `· open`; none for anything else. Each bullet at most 20 words, starts with **Decide**, **Look** or **Do**, names the heading it refers to. If there are none, write `**Needs you:** nothing`. If there are more than five, write `**Needs you:** N decisions open, § Decisions` instead. No rationale, no history, no hedging, no "comprehensive". Do not invent an item.
