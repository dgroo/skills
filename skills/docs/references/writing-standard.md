# docs — the writing standard

Part of the `/docs` skill; read before writing or reviewing a page. Adapt into the project as its own `STYLE.md` — binding rules, "if a page breaks a rule here, the page is wrong." Built on [Diátaxis](https://diataxis.fr/) for structure and the [Google developer documentation style guide](https://developers.google.com/style) for voice.

## 1. One mode per page

Every page is exactly one of tutorial, how-to, reference, explanation, and its mode determines its shape. The commonest failure is a how-to that teaches or an explanation that drifts into steps. Split and link.

**The worked example that matters most in any project:** the single largest source of support requests splits across two modes and must stay split — a how-to that gives the fix with no theory ("Your script's output isn't appearing. Add `-u`."), and an explanation of why the runtime behaves that way with no steps. Each links to the other. Neither repeats the other.

## 2. Voice

1. **Second person, active voice, present tense.** "You pass `--port`", not "the port may be passed".
2. **Front-load the answer.** The first sentence says what the reader gets or what is true. Justification comes after.
3. **One idea per sentence.** Split stacked facts.
4. **Conditions before instructions.** "If you're behind a proxy, set X."
5. **Sentence case headings.**
6. **Define jargon on first use, or link it.** The reader arrived from a search engine, not the previous page.

## 3. Never write about the documentation

Do not open a page or a section by describing how the documentation was produced, verified, generated, or kept accurate:

> ❌ This page is generated from the tool's own flag definitions, so it can't drift.
> ❌ Verified line-by-line against `config.go`.
> ❌ The project went through one hardening pass, followed by a second wave adding…

The reader came for the subject. Where provenance genuinely helps (a generated page, so they know not to hand-edit), it is one line at the *foot*. Don't narrate development history in user docs either — "was requested many times and declined" belongs in an explanation page about design decisions, and nowhere else.

## 4. Write as if the current release is current

No "coming soon", no "not yet released", no version-gap caveats, no apologising for a missing binary. State what is true of the release the reader has.

## 5. Mode-specific shape

- **Tutorial:** one path, numbered, every step's expected result shown, no options or alternatives, ends with the reader having done the thing. Traps a newcomer hits go *here*, at the step where they hit them.
- **How-to:** title is the task ("Serve over TLS"), opens with the fix, assumes competence, links theory rather than including it, lists prerequisites as conditions.
- **Reference:** complete and uniform — every flag, every field, the same shape; generated from the source of truth where one exists; no recommendations (link a how-to instead).
- **Explanation:** why, trade-offs, what was considered; may reference history and decisions; no steps.

## 6. Cross-linking

Every how-to links the explanation behind it; every explanation links the how-to that acts on it; reference pages link nothing but other reference. A page never repeats another page's content — it links.

## 7. Nothing that identifies a machine

No hostnames, home directories, usernames, or local paths in examples or generated output. A test that fails the build on the current machine's own identifiers is the mechanism.

## 8. The FAQ is a signpost, not a section

Each FAQ entry is one sentence and a link to the page that actually answers it. If the answer needs more than a sentence, it is a how-to or an explanation that doesn't exist yet — write it.
