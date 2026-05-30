---
name: humanize-text
description: Use when asked to strip AI "tells" from written prose — "humanize this", "de-slop this writing", "does this read as AI-written", "make this sound like me", "/humanize-text". Detects AI fingerprints (em-dash clusters, "it's not just X, it's Y", rule-of-three cadence, reflexive hedging, banned vocab) and proposes voice-preserving edits that do not change meaning. Calibrates against the author's own writing corpus and surfaces any meaning-affecting word choice separately for sign-off. NOT for code (see /humanize-code) or visual/UI slop (see /design-review).
argument-hint: "[<file> | review | profile [show|edit|add] ]"
---

# /humanize-text

Take a piece of prose and remove the fingerprints that make it read as AI-written — **without changing what it says, and without flattening the author's actual voice.** This is a propose-then-apply editor, not a rewriter. It shows you a diff and a rationale before it touches anything.

The hard part is not detecting AI tells; a regex can do that. The hard part is not stripping the tells that are _genuinely the author's_. An em-dash is an AI fingerprint in one person's writing and a load-bearing habit in another's. So this skill is **voice-first**: it calibrates against a corpus of text the author actually wrote before it proposes a single cut.

Companion to (not replacement for):

- `/claude-md-add` — same iron discipline (_copy editor, not rewriter_; every clause traces to the original; show the diff before writing), applied to single CLAUDE.md entries. This skill borrows that contract wholesale.
- `/humanize-code` — the sibling for source code (functional-identity guarantee, branch-isolated). Different verification model; different risk class.
- `/design-review` — AI-slop detection for _rendered_ visual/UI output, not prose.

---

## The two iron rules

**1. Content-preserving.** The proposed text says exactly what the original said. Removing an em-dash, breaking a tricolon, or swapping a banned word for a plain one does not change meaning. If a proposed edit _could_ shift meaning, emphasis, or register, it does not go in the silent-cleanup diff — it goes in a **separate "word-choice changes" list** that needs explicit sign-off (see Phase 4). This is the prose analog of code's functional-identity guarantee: mechanical de-slop is safe to batch; semantic edits are not.

**2. Voice-preserving.** A "tell" is only a tell if it is _not_ how this author writes. Calibrate against the author's real corpus (`~/.claude/voice/profile.md`). **Never calibrate from text the author did not personally type** — a CLAUDE.md, a committed README, a prior "humanized" doc. AI-authored text in the author's own repo is the single most common way to mistake a fingerprint for a fountain pen.

---

## Safety gate — runs before any edit

Editing prose in place is destructive if there's no way back. Before proposing edits:

- **Target is under version control (clean or committed):** proceed.
- **Target is tracked but dirty:** note it; the diff is recoverable via `git`, so proceed.
- **Target is NOT under version control** (loose file, pasted text being written back to an unversioned path): **stop and require confirmation that a backup exists.** Offer to copy it to `<file>.bak` first. Do not silently overwrite unversioned prose.
- **Pasted text with no file target:** no gate needed — output the proposed version, write nothing.

---

## How to invoke

```
/humanize-text <file>          # de-slop a file, propose a diff
/humanize-text                 # de-slop the most recent pasted/selected text
/humanize-text review          # dry run — report tells, propose nothing
/humanize-text profile         # show the active voice profile
/humanize-text profile edit    # open the voice profile for editing
/humanize-text profile add     # append new samples / observed tells to the profile
/humanize-text help            # usage
```

| Verb / arg     | What it does                                                                |
| -------------- | --------------------------------------------------------------------------- |
| `<file>`       | Run the full workflow on a file; propose a diff, apply on approval.         |
| `(none)`       | Same, on the most recent pasted or quoted text in the conversation.         |
| `review`       | Detect-and-report only. No proposal, no write. Good for "how bad is this?". |
| `profile`      | Print the active voice profile.                                             |
| `profile edit` | Edit `~/.claude/voice/profile.md` directly.                                 |
| `profile add`  | Add real writing samples or confirmed personal tells to the profile.        |
| `help`         | Print usage (see Help section).                                             |

---

## Workflow

### 1. Locate the target and clear the safety gate

Resolve the file or grab the pasted text. Run the safety gate above. For pasted text, skip straight to detection — nothing gets written.

### 2. Load the voice profile

Read `~/.claude/voice/profile.md`. It records, per author, the tells that are _actually theirs_ and a few real writing samples for calibration.

If the profile is **missing or empty**, do not guess from the repo. Bootstrap it: ask the author to paste 2–3 samples of writing they personally typed (chat messages, emails, Slack), extract the recurring habits, write them to the profile, and _then_ run detection. A first run is allowed to be a profile-building run.

### 3. Detect the tells

Load `references/ai-tells.md` (on demand — it's a long list) and scan the target across its layers: vocabulary, phrase templates, sentence openers, structural rhythm, punctuation, formatting leaks, and fabrication risks. For each candidate hit, **check it against the voice profile**: if this is a habit the author genuinely has, it is not a tell — leave it.

### 4. Triage every candidate into two buckets

| Bucket                        | Criterion                                                                                                                                                 | Where it goes                    |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| **Mechanical (safe)**         | Removing it cannot change meaning, emphasis, or register. (em-dash → comma; "delve into" → "look at"; break a forced tricolon into two clauses.)          | The silent-cleanup diff.         |
| **Semantic (needs sign-off)** | The fix could alter what's said, how strongly, or the tone. (deleting a hedge that was a real qualification; swapping a word with different connotation.) | The separate "word-choice" list. |

When in doubt, it's semantic. The cost of asking is one line; the cost of silently changing meaning is trust.

### 5. Show the review

```
**Target:** <path or "pasted text">
**Voice profile:** <loaded / bootstrapped this run / none>
**Tells found:** <N mechanical, M semantic>  (or "None — reads clean")

**Original:**
> <verbatim>

**Proposed (mechanical only):**
> <de-slopped version — meaning identical>

**Mechanical changes:** <one line per change, tied to a tell category>

**Word-choice changes (need your call):**
- "<original phrase>" → "<suggested>" — <why it might shift meaning; what you'd be agreeing to>
- (or "None")
```

### 6. Get approval, then apply

Ask: **accept mechanical / accept mechanical + selected word-choice / use original / tweak / cancel.** On accept, apply via Edit. Don't restructure surrounding content. Don't fold separate changes together. If you changed register anywhere, say so explicitly — silent voice changes are the failure mode.

---

## The voice profile

**Location:** `~/.claude/voice/profile.md` (default author = the user). Multiple authors live as `~/.claude/voice/<name>.md`; select with `/humanize-text profile <name>` or by naming the author when editing someone else's text.

**Why a persistent file, not per-run inference:** voice is stable and slow to change; rebuilding it from scratch every run is wasted effort and drifts. The file grows: every time the author corrects a false positive ("that em-dash is mine"), append it.

**Shape:** real samples + a list of confirmed-personal habits. Keep it small and concrete. It is not documentation — it's calibration data.

**Tracking:** `~/.claude/voice/` can be tracked in the dot-claude repo so the profile follows the author across machines. Surface that on first creation; don't assume it.

---

## Why voice-first — the em-dash trap

The instinct is to treat the em-dash as the canonical AI tell and strip it on sight. That's wrong twice over. First, plenty of real writers lean on em-dashes — strip them and you've erased a voice, not a fingerprint. Second, the actual signal is never one token; it's the **constellation**: em-dash _plus_ "it's not just X, it's Y" _plus_ a steady drumbeat of three _plus_ "Here's the thing" _plus_ hedges on every claim. Any one in isolation is human. The cluster is the model. So: detect the cluster, calibrate the single tokens against the author, and only cut what's both a tell _and_ not theirs.

---

## Common mistakes

- **Calibrating from repo text.** A CLAUDE.md or README the author "wrote" was probably AI-drafted. Its em-dashes are the model's, not the author's. Only ever calibrate from text typed by hand.
- **Treating word-choice swaps as mechanical.** "Robust" → "solid" can carry a different claim. Semantic bucket, every time it's arguable.
- **Stripping single tokens because they're on the list.** The list finds candidates. The voice profile and the constellation decide. A lone em-dash in an em-dash user is not a hit.
- **Silent register changes.** If the cleaned version is colder, terser, or more formal than the original, that's a voice change — surface it, don't ship it quietly.
- **Adding prose.** Same as `/claude-md-add`: every clause in the proposed version traces to a clause in the original. De-slopping removes; it does not author.
- **Overwriting unversioned text without a backup.** The safety gate is not optional.

---

## Help

When invoked as `/humanize-text help`, print the following block verbatim:

```
humanize-text — Strip AI "tells" from prose without changing meaning or flattening the author's voice.

Usage: /humanize-text [verb | <file>]

Verbs:
  <file>            De-slop a file; propose a diff, apply on approval.
  (none)            De-slop the most recent pasted/selected text (writes nothing).
  review            Detect-and-report only — no proposal, no write.
  profile           Show the active voice profile.
  profile edit      Edit ~/.claude/voice/profile.md.
  profile add       Append real writing samples / confirmed personal tells.
  help              Show this message.

Two iron rules:
  Content-preserving   Mechanical de-slop only in the silent diff; meaning-
                       affecting word choices are listed separately for sign-off.
  Voice-preserving     Calibrate against ~/.claude/voice/profile.md — text the
                       author actually typed. Never from repo/CLAUDE.md text.

Safety:
  Unversioned target   Refuses to overwrite until a backup is confirmed.

Detection layers live in references/ai-tells.md (loaded on demand).

Companion skills:
  /claude-md-add    Copy-editor pass for single CLAUDE.md entries.
  /humanize-code    The sibling for source code (functional-identity, branch-isolated).
  /design-review    AI-slop detection for rendered visual/UI output.

See SKILL.md for full reference.
```

## Related

- **`/claude-md-add`** — the discipline precedent: copy editor, not rewriter; trace test; show-the-diff.
- **`/humanize-code`** — sibling skill for code; strongly prefers a clean dedicated branch + atomic commit so the diff is trivially reviewable and revertable.
- **Prior art:** `references/ai-tells.md` adapts the banned-word/phrase/pattern lists from [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing), adding the voice-calibration and meaning-preservation contracts it lacks.
