# go-team — Rules of evidence

Part of the `/go-team` skill; paste into every worker brief. The loop itself is in `SKILL.md`.

## Rules of evidence

Give these to every agent, and hold yourself to them harder.

**Reproduce before fixing.** A baseline and a control, not a reading of the code.

**Every guard must be proven to bite.** Run the new test against the *unfixed* code and paste the failure. A guard not proven to fail before the fix is not evidence — it is decoration, and several have shipped that would have passed either way.

**Every predicate ships with the case that must not trigger it.** Three agents shipped a plausible rule that only failed on input they didn't write, and every one's tests asserted only the positive case — `Alex Chen` matches; nobody wrote `Golden Gate Bridge` doesn't. Review by reading cannot catch this; the code looks reasonable. Review means executing adversarial input.

**Guards assert a class, not a call site.** "No call to `newChat(` anywhere carries an argument" beats "this line looks right." A privacy leak in the originating project was fixed three times at three call sites; the fourth caller was found only when the guard was rewritten to assert the class.

**A test that cannot reach its subject must fail loudly.** Not pass. An early-exiting run leaves telemetry that reads exactly like a result.

**Fixtures are instruments — check them like one.** Six fixture defects in one day, in the one place nobody checks because it's what you check against: a field the real API never returns; a corpus that alternated authors so a multi-revision session was unreachable by construction; two rounds with byte-identical images so the "image changed" path could never fire; a corpus with zero wikilinks making every "no change" result vacuous. Two cheap checks: does every field match what the real API returns (compare against the code's own request mask); and *can this fixture exhibit the property at all* — construct the failing case by hand and confirm the corpus could produce it.

**Name the instrument in every measurement.** A fake or stub backend that approximates the real one is not the real one. Four separate agents measured semantic quality with a word-overlap stub and reported the numbers as findings.

**Measure the quantity the decision needs.** Write down the decision the number will change *before* measuring, then ask what the cheapest quantity is that changes it. The foreman once built a seven-sample rate measurement, contaminated it with its own compile, and reported it unusable — when the decision only needed "is the level still falling?", answerable from numbers already published. And before reporting a discrepancy between two counts, state both predicates: different predicates, no discrepancy.

**Hunt vacuous gates.** A check that cannot fail is worse than no check, because it reports success. If a pipeline is deterministic, running it five times and reporting stddev 0 proves nothing about whether a difference is meaningful — the variance is zero by construction. Ask of every gate: *what input would make this fail?*

**Do not loosen a test to accommodate a bug.** Watch for a threshold set just above a measured failure rate — that enshrines the failure instead of fixing it.

**Say what you did not do.** Reverting an incomplete fix is a respected outcome. So is "I could not determine this."

---

