---
name: docs
description: Plan and write user documentation — Diátaxis structure, audience first, a reader test before merge. Use when creating or restructuring docs.
argument-hint: [plan | write <page> | review <page-or-dir>]
---

# Docs: write for the reader who arrived from a search engine

Documentation fails in one specific way when agents write it: it comes out as development notes. Pages open by describing how they were generated and verified, narrate the project's history, stack three facts into one sentence, and mix a tutorial's hand-holding with a reference's precision until they do neither. Every one of those pages was technically accurate. A human read one and said "the text is gibberish — how are they meant to understand it?" Four pages were rewritten. This skill exists so that happens zero times, not once.

## Before writing anything: research, then plan

If this project has never had real docs, do not start by writing pages. **Look at how three comparable projects document themselves** — structure, tooling, what a first-time reader lands on — and write down what you'd take from each. Then plan:

1. **Who reads this, in the order they show up.** Name them: the evaluator deciding in ten minutes, the newcomer with a terminal open, the implementer who needs the exact contract, the operator deploying it, the stuck person who needs the answer in thirty seconds. Every page is written for one of them.
2. **Inventory what needs documenting** from the code, the issue tracker's recurring questions, and the old docs — recurring support questions are the highest-value pages.
3. **Choose the four Diátaxis sections** (below) and place every inventory item in exactly one.
4. **Tooling as an options table** — generator, hosting, single-sourcing of generated reference (flags, config, API) so it *cannot* drift, link checking — with a recommendation, and **the actions only the human can take** (a DNS record, a domain, a secret) called out first, so they're never a surprise.

The plan is a file in the repo. Get it read before building.

## The structure: Diátaxis, and why a page is only one thing

| Mode | Reader's state | The page answers | Shape |
|---|---|---|---|
| **Tutorial** | "I've never used this" | "Take me through it once, successfully" | Numbered steps, one path, guaranteed outcome, no options |
| **How-to** | "I have a specific job" | "The steps for this exact task" | Task-titled, fix first, theory linked not included |
| **Reference** | "I need a precise fact" | "What exactly does X do?" | Complete, consistent, generated where possible, no advice |
| **Explanation** | "I want to understand why" | "Why does it work this way?" | Prose, context, trade-offs, no steps |

A page that serves two modes serves neither. The commonest failure is a how-to that teaches, or an explanation that drifts into steps. When a page starts doing both, split it and link — each side links the other, neither repeats it.

## The writing standard

The binding rules are in `references/writing-standard.md`; read it before writing a page. The five that catch the most defects:

- **Never write about the documentation.** No page or section opens by describing how it was produced, generated, or verified. Provenance that helps ("generated — don't hand-edit") is one line at the foot.
- **Front-load the answer.** A reader who stops after one sentence still has it.
- **One idea per sentence.** Three technical facts in one sentence is the house defect.
- **Conditions before instructions.** "If you're behind a proxy, set X" — not the reverse.
- **Define jargon on first use, or link it.** They did not arrive from the previous page.

## The reader test — the gate

Before any docs page merges, **someone who has not seen the code reads it as the target reader** and answers two questions: *what is this page for?* and *what would I do next?* In a fleet, that's a fresh agent with no context and the persona from the plan. If it can't answer, the page goes back — not to be verified against the code again (it was already accurate), but to be rewritten for a person. Run it on your own drafts too: read the page aloud as the newcomer.

## Mechanisms, not intentions

- **Generated reference has a drift check that fails.** If flags, config or API are documented, generate that page from the source of truth and add a CI check that fails when the generated output and the committed page differ — and prove it fails on a hand edit before trusting it.
- **Links are checked in CI**, and the check is proven to fail on an injected broken link.
- **`/llms.txt`** (and `/llms-full.txt`) alongside the site, so agents reading the docs get the plain-text form.
- The writing standard lives in the repo (`docsite/STYLE.md` or equivalent) and says: *if a page breaks a rule here, the page is wrong.*

## Reviewing existing docs

`review <page-or-dir>`: for each page, name its mode (or "two modes — split"), its reader, whether the first sentence is the answer, every sentence that talks about the documentation itself, every undefined term, and whether a stuck reader would find it in thirty seconds. Then apply the reader test. Report as a table, worst first.
