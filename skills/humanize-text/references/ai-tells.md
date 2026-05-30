# AI tells — detection reference

Loaded on demand by `/humanize-text`. These are _candidates_, not verdicts. Every hit is checked against the author's voice profile and triaged mechanical-vs-semantic before anything is proposed. A tell that is genuinely the author's habit is not a tell.

Vocabulary and phrase lists adapt [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing); the structural and constellation guidance is this skill's own.

---

## Layer 1 — Vocabulary (single words)

High-frequency LLM register words. Flag; suggest the plain equivalent. **Mechanical** unless the word carries a specific claim (then semantic).

delve, tapestry, landscape (figurative), realm, vibrant, robust, comprehensive, nuanced, multifaceted, pivotal, crucial, essential, vital, intricate, seamless, holistic, underscore, foster, showcase, leverage (verb), utilize, facilitate, garner, myriad, plethora, bustling, testament, beacon, navigate (figurative), embark, unlock, elevate, empower, harness, profound, paramount, cornerstone, gamechanger, ever-evolving, fast-paced, cutting-edge, state-of-the-art.

## Layer 2 — Phrase templates

- "It's not just X, it's Y" / "This isn't about X — it's about Y"
- "more than just a …"
- "In today's fast-paced / competitive / digital world …"
- "It's worth noting that …" / "It's important to note / remember …"
- "When it comes to …"
- "At the end of the day …"
- "needle in a haystack", "tip of the iceberg", "double-edged sword", and similar reflexive idioms
- "plays a crucial/vital role in"
- "stands as a testament to"
- "the world of …" / "the realm of …"
- "Whether you're X or Y …" (false-binary opener)
- "Let's dive in / let's explore / let's take a look"

## Layer 3 — Sentence openers (over-used connectives)

Certainly, Indeed, Moreover, Furthermore, Additionally, Notably, Importantly, Ultimately, Essentially, Crucially, That said, In essence, In conclusion, Overall, Simply put, Rest assured. Flag when they cluster or open consecutive sentences.

## Layer 4 — Structural rhythm

- **Rule of three** — relentless tricolons ("fast, clean, and reliable"; "it's faster, it's cheaper, and it's better"). Humans use one occasionally; the model uses them constantly.
- **Uniform sentence length** — every sentence the same medium length. Human writing varies burst-to-fragment.
- **Reflexive hedging** — "may", "might", "could", "generally", "in some cases", "tends to" stacked onto claims that don't need them.
- **Symmetry / paired clauses** — "not only … but also", balanced antithesis on every point.
- **Section-summary reflex** — restating what was just said before moving on; "In short," mid-paragraph.
- **Signpost overload** — "First, … Second, … Finally," on content that doesn't need enumeration.
- **The "here's the thing" / "the real X is" reveal** — manufactured turn toward a "deeper" point.

## Layer 5 — Punctuation

- **Em-dash clusters** — multiple em-dashes per paragraph used for dramatic asides. (Single, voice-dependent — check the profile.)
- **Exclamation points** in expository prose.
- **Ellipsis** for manufactured suspense.
- **"Quotes" around ordinary words** for unearned irony.
- **Curly-quote / straight-quote inconsistency** that betrays paste-from-model.

## Layer 6 — Formatting leaks

- Markdown bold/headers bleeding into plain-text contexts (email, chat).
- Emoji bullets (✅ 🚀 💡) in prose.
- Hashtag stacks.
- Numbered lists where prose was asked for.
- Bold-label-then-colon on every bullet ("**Speed:** it's fast").

## Layer 7 — Fabrication risk (never "fix" — flag loudly)

- Invented statistics ("studies show 73% …") with no source.
- Fabricated quotes or attributions.
- Plausible-but-unverifiable anecdotes ("I once worked with a team that …").
- Fake specificity (precise numbers standing in for real data).

These are **never** mechanical and **never** silently edited. Surface them; the author decides whether the underlying claim is true.

---

## The constellation rule

No single item here convicts. A lone em-dash, one tricolon, one "moreover" — all human. The signal is **density and co-occurrence**: several layers firing together in a short span. Weight detection toward clusters, not isolated hits, and always let the voice profile veto a token the author genuinely owns.
