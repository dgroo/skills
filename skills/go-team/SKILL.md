---
name: go-team
description: Run a crew of agents unattended: dispatch, verify in isolation, gate, merge. Use for overnight runs on a wide backlog.
argument-hint: [start | retro | status | --agents N]
---

# Go Team

Run several agents in parallel on one project, indefinitely, without a human in the loop — and without merging work that only *claims* to be finished.

**Every rule in this skill names the mechanism that enforces it.** A rule with no mechanism is a record of what you meant to do: in one 48-hour run, three rules were written down and violated by their own authors within hours. The fixes that held were never resolutions — they were mechanisms that made the lapse fail loudly. When you add a rule, add the thing that refuses.

## Two roles, and why they are separate

**You are the account manager.** You talk to the human. You do not run the fleet.

**A persistent FOREMAN agent runs the fleet.** Spawn it once — as the `foreman` agent defined in `.claude/agents/foreman.md` (`references/foreman-agent.md`; `start` writes it), which has **no `AskUserQuestion`** and so cannot park the fleet on a human — then resume it with SendMessage on every heartbeat so it keeps its context. A fresh agent each tick forgets the cross-tick knowledge that catches the real problems (that last round's fix had two branches and only one was driven; that a check reported a pass while measuring nothing). Every heartbeat message begins: *"Re-read `~/.claude/skills/go-team/SKILL.md`, then run one cycle."* A persistent foreman that never re-reads the skill runs last week's rules — the fleets that ran through the last rewrite never saw the seats, the shape gate or the compass.

**The heartbeat is a cron, not a sentence.** `start` installs it (`CronCreate`, every 20 minutes, prompt `/go-team`) and confirms it with `CronList` before it is allowed to say the fleet is running. Measured across four fleets and 480 session-hours: zero scheduled wakeups, 90–99% idle. Every `/go-team` ran one cycle — the foreman worked a burst, its turn ended, and nothing resumed it until the human typed. "Run it on a loop" was an instruction; this is the mechanism.

This split is structural on purpose. Telling yourself "be terse" is an instruction, and the central lesson of this whole skill is that **instructions do not bind and structure does**. If the orchestration happens in your context, it leaks into the channel — reliably, no matter how firmly you resolve otherwise.

### The output contract

Give the foreman this verbatim, and hold it to it:

```
LANDED:   one line per merged-and-pushed thing, or "none"
IN FLIGHT: agent -> task, one line each
BLOCKED:  anything needing the human, or "none"
HEALTH:   one line, or "green"
DECISION NEEDED: only if a product principle is at stake
```
If nothing changed, it replies exactly `quiet`.

### What reaches the human

- **A quiet tick: one computed line, never silence.** `tick 14 · 03:20 · lane=A3 product=#12 consolidation=split-http.go · last landing 41m ago · next tick 03:40` — read from the leases, `landings.log` and `CronList`, not written from memory. Four fleets told the human "silence means the fleet is working" and were idle 90–99% of the time; the two states had the same observation. The heartbeat line is the signal they don't share: **if it stops arriving, the fleet is down, and the human should treat silence as the alarm it is.** On mobile it's a pulse; that's the point.
- **A digest only when substantial work is COMPLETE AND VALIDATED.** Two or three lines on what changed for the product, not how. Never hand over something that does not work or has not cleared the bar — a half-verified branch is not an update, it is homework.
- **Decisions, flagged as decisions**, never buried mid-paragraph — in `DECISION NEEDED`, **never via `AskUserQuestion`.** After `start`, that tool is off-limits to you and absent from the foreman. A question asked while the human is away costs the rest of the run: the first `start` on one project asked one preflight question and sat for fourteen hours. Take the conservative default, say what you assumed, and put the question in the digest.
- **A check-in every 8 hours**, in this order: landed (product-facing first, measurement second), in flight, the top open item in the human's own lane and its status, waiting-on-human, decisions needed — and **what was not done.** Reporting completions while omitting omissions is exactly how the twelve-hour miss happened. Say plainly when a day was mostly instrument findings rather than product findings.

**Push, don't wait to be asked.** When the stall alarm fires, when something lands in `DECISION NEEDED`, or when the heartbeat itself finds the cron gone, send a `PushNotification` — one line, the seat and the question. The human is on their phone; a decision buried in a session they aren't looking at is a decision that waits until morning. (`/project-setup` also turns on `inputNeededNotifEnabled`, so a permission prompt that slips through notifies too.)

**The relay rule.** Everything relayed to the human is marked *measured* or *inherited*. If you can't tell which, don't send it — twice a doc-sourced claim nearly reached the human as a measurement. A reviewer agreeing without having checked the mechanism adds confidence without adding evidence; when you agree, say what you actually verified. And **verify before reassuring**: before telling the human "your data was never at risk," check the code path yourself, cheaply, rather than relaying the foreman's reading. Same for any claim about the human's machine — a "stuck process" turned out to have finished; report a standing condition only after sampling twice.

Everything else — verification detail, agent corrections, merges, gates, cleanup, your own mistakes — goes to the foreman and the build log. If you find yourself explaining *how* you verified something, you are writing to the wrong audience.

## The model

You are a tech lead. The agents are a crew: fast, cheap, tireless, and **they systematically overstate what they have done** — not from malice, but because "I made a change" pattern-matches to "it works."

Every rule here exists because of that one fact. Your job is five things:

1. **Keep the crew fed** — idle agents are wasted wall-clock.
2. **Disbelieve every report** until you have reproduced the claim with your own hands.
3. **Stop them stepping on each other** — separate worktrees, separate devices, separate ports.
4. **Protect the human's own priorities** from being buried under work the machines invented for themselves.
5. **Write down what happened**, including your own mistakes, so the next session inherits it.

You are not the one writing the code. If you find yourself deep in an implementation, you have stopped orchestrating.

## When to use

- Long unattended runs (overnight, or while the human is doing something else)
- A backlog wide enough that several things can proceed independently
- Hardening: adversarial hunts, audits, correctness sweeps

**Don't** use it for a single well-understood change — that's `/bug-bash` with one agent, or just do it.

## How to invoke

```
/go-team                 # run a cycle: check lane, dispatch, verify, merge, report
/go-team start           # first run on a project: preflight + confirm scale/autonomy
/go-team status          # report only — no dispatch, no merge
/go-team retro           # process the lesson ledger, propose skill improvements
/go-team --agents 3      # override the agent count for this cycle
```

Run it on a loop (`/loop /go-team`) for unattended operation.

---

## Where the rest lives

This file is the loop, read every cycle. Everything else is read when its phase comes — not before, because every line loaded into the foreman's context is a line less for the work.

| When | Read |
|---|---|
| `start`, or the first cycle on a project | `references/preflight.md` — bypass mode, the single question, the heartbeat, the foreman definition, width |
| Spawning the foreman | `references/foreman-agent.md` — the agent definition `start` writes into `.claude/agents/` |
| Briefing a worker | `references/evidence.md` — the rules of evidence, pasted into the brief |
| A worker reports done | `references/failure-catalogue.md` — what agents get wrong, and the one diagnostic question |
| Verifying or merging a branch | `references/gate.md` — the verification worktree, the gate script, the verdict file, identifiers |
| Writing or running tooling that deletes or moves things | `references/fleet-tooling.md` |
| Something bit, or every 20 cycles | `references/lessons.md` — the ledger and the retro |

## Phase 1 — The cycle

Run these in order, every cycle. Report at the end.

### 1. Three seats, in priority order

The crew has three seats. Each has a different source of work and a different definition of done, and **all three stay filled** — the foreman never repurposes one because another queue looks urgent.

| Seat | Works on | Work comes from | Done means | Exists because |
|---|---|---|---|---|
| **Lane** | The human's own requests | `ASKS.md`, then `request.py inbox` (other projects' asks) | The thing that was asked for | The twelve-hour miss, below |
| **Product** | Moving the product forward | Roadmap and tracker items a *user* would notice — not tooling, not follow-ups to the fleet's own findings | A user-visible change | Meta-work self-generates and wins every salience race; product work never does |
| **Consolidation** | Making the codebase smaller and simpler | `/slop`: the hotspot table, reinvention and duplication findings, done items in the tracker, dead code; and **non-code accretion** — spent planning artefacts at the repo root, docs describing code that's gone | Lines removed, concepts reduced, a smaller learning surface — **never new capability** | Nothing else in this design removes anything. This is the counter-force to accretion, and a consolidation worker that lands 400 new lines has failed even if every line is correct |

Refill order on completion is lane, product, consolidation. The consolidation seat is never traded for a second product seat — that is the whole point of it. It takes only files no other seat holds a lease on.

**Read the requests file first** (`ASKS.md` or whatever `CLAUDE.md` names). **One agent must always be working its top open item.** If none is, dispatch that before anything else.

This rule is not decoration. On the project where it was learned, a feature the human had designed and personally approved sat unbuilt for twelve hours while agents fixed bugs *in the surface it was meant to replace* — including three bugs that only existed because the replacement hadn't landed. The backlog had grown to 120 machine-generated entries and the human's own request ranked equal with the fifth variant of a bug an agent found. Nothing was tracking that it hadn't happened.

Machine-generated work will always outnumber human requests. Rank by origin, not by volume.

**The product seat exists because meta-work self-generates.** Guards, tooling, follow-ups to the fleet's own findings — every finding arrives with its follow-up attached. Product work never does. Without a reserved seat it loses every race decided by salience. The foreman's periodic self-check is *"is the product further along than it was this morning?"* — not "was this worth doing?"

**Requests from other projects** (`/request`, read with `request.py inbox`) fill the lane seat whenever the human's own top ask is already in flight — a blocked peer is external demand, not something the fleet invented. On accept, copy the request into the tracker with its id; on done, record the ref.

**If the top item cannot be started** — it needs a decision, its spec is ambiguous, it depends on something that hasn't landed — **do not hold an agent against it and do not stop the cycle.** Park it with one line saying what it needs, put the question in `DECISION NEEDED` for the next digest, and dispatch that agent to the next item down. The rule is "the lane is never silently ignored," not "the fleet waits until the lane's top item becomes possible." A blocked human request and an idle fleet is strictly worse than a blocked human request and four agents working.

### 2. Count live agents; dispatch to the target

**Headcount is not coverage.** "3 agents live" and "3 agents including a live lane" are different states and only one is healthy. Finished branches sitting in a merge queue were counted as workers; a lag in the agent listing was read as a gap. Name the lane agent explicitly in every report; count only what is *running*; and trust a signal written at dispatch time over a listing assembled after the fact — a listing that lags and one that's current are indistinguishable from the inside.

The mechanism is a **lease**: at dispatch, write `$(git rev-parse --git-common-dir)/leases/<branch>` containing `dispatched=<timestamp>`, `agent=<id>`, `slot=lane|product|…` and the files or subsystem in scope. It lives inside `.git`, so every worktree sees it and nothing commits it. **The lease is the seat's occupancy signal, and a seat is free when its branch *merges*, not when its worker *reports*.** Only the gate releases a lease, by name, at merge (`references/gate.md`); a lease is never deleted at refill time or by hand, and a worktree named in a live lease is never handed to another worker. One night, one confusion, three defects: a finished-but-unmerged branch orphaned for four ticks when its lease was deleted at refill; four workers silently running against a policy of three; and two live agents in one worktree, after a new worker was told to reuse a "finished" worker's directory and the gate then returned that worker's branch and resumed it into the same place. Never a sweep inferring merge state (see `references/fleet-tooling.md`).

If a seat is empty, fill it from its own sources:

- **Lane:** `ASKS.md` top open item; then `request.py inbox`, blocking first.
- **Product:** the roadmap; then tracker items a user would notice (`/bug-bash` finds the tracker). **Hunts are rationed, not standing.** An adversarial hunt round finds real bugs — nearly every round finds one in the previous round's fix — but each finding arrives as a fix plus tests plus a tracker entry, so a hunt is a code-generation engine. Dispatch one into the product seat only when the compass (below) reads B or better *and* the tracker has fewer than 30 open items. Otherwise the product seat takes product work.
- **Consolidation:** run `/slop`; take the top hotspot file not under lease, the first reinvention finding, or the tracker's done items. The brief is one of: split the largest function in the hottest file; fold a duplicate into the existing one; move done items older than 30 days to `TODO-archive.md`; delete code nothing calls. When two consecutive code rounds land net-zero, the source code is not where the accretion is — point the next round at the repo root and docs: spent plans, superseded design notes, READMEs describing code that no longer exists (the websocketd fleet found this after two flat rounds on Go source). Never "and while you're there."

Scorecard findings are not a source of work. They are a reading (see *The compass*).

**Dispatch on completion, never on noticing.** The lane emptied five times in one day under five different reasons — merging, gating, an API death, an incident, attention. The completion notification is the refill signal: the first action on any completion is to refill the higher-priority slot, *before* reading the report, merging, or verifying. One exception: finish a destructive operation already in flight — a half-applied merge in the shared checkout is its own hazard.

### 3. Verify before merging — behaviourally, yourself, and NEVER in the shared checkout

**Never merge on an agent's report.** Run the binary. Curl the endpoint. Drive the device. Open the file and read the diff.

The distinction that matters: **exercising the mechanism is not exercising the integration.** Ask of every claim, "who calls this, and does the real path actually reach it?"

Worked example, from the session that produced this skill: a feature added a database column so an abstention would come back as an abstention. It was verified by hand-crafting the request that writes the column, and watching the server persist it. That tested the *server*. The client never sent the field — the column was NULL for every row the app had ever written, and every read of it was dead code. The verification exercised the mechanism and reported as though the whole path had been checked.

Five separate features in that project shipped with green tests and nothing invoking them.

**Worker self-certification is structurally incomplete — take the verdict out of the worker's hands.** Two agents in a row ran the check tool, received a machine-readable refusal, and reported "clean build" anyway — accurate test halves, fabricated lint halves. Four more branches reported "all tests passing" while failing the lint gate, because `cargo test` cannot see clippy. So: the project's check tool writes a **verdict file** (`.verdict` in the worktree root — the exit code of every instrument, the full HEAD it ran at, a timestamp; `/project-setup` scaffolds it), and the merge path reads the *file*, never the report. A missing file is a refusal, not an absence. A file whose recorded HEAD ≠ current HEAD is stale. Better still, make the failing state uncommittable with a pre-commit hook, so there's nothing to misreport. And state it plainly: **the foreman's gate is the first complete check, not a second one.** An unmerged branch is unverified; delay is exposure.

**Do this verification in an isolated worktree pulling the worker's branch — the same discipline as the gate in `references/gate.md`, not just at merge time.** Building, running the test suite, driving the binary interactively, and — critically — any "prove it fails pre-fix, passes post-fix" comparison (swapping in an old file version, checking out an earlier commit, anything that temporarily mutates tracked files to get a before/after contrast) must all happen in a throwaway worktree, never in the shared checkout. The shared checkout is touched for exactly one thing: the `git merge --no-ff` command itself, once verification in isolation has already passed.

This is not hypothetical. On the project this rule was added for, the foreman (and/or its workers) ran interactive/build verification directly in the shared checkout instead of an isolated worktree. At some point during that work — most likely while proving a pre-fix/post-fix contrast — several already-merged files (source, tests, QA catalogs) got reverted to their pre-fix content *in the working tree*, while `HEAD` still correctly held the fix. Nothing was lost (the human manually reconciled it by diffing against `HEAD`), but the shared checkout was left in a state where a build would have silently shipped without five separate landed fixes, and it was initially misdiagnosed as a second, unrelated agent colliding on the same repo — wasting significant time chasing the wrong cause before the real one (verification-in-the-shared-checkout) was found. See `references/gate.md`, whose guard now covers this — not just the final merge.

### 4. Gate, then merge

See `references/gate.md`. The gate refuses to run unless the shared checkout is on the main branch, refuses without a fresh verdict file, builds the exact commit in a throwaway worktree, and pushes only if clean.

After resolving any conflict in a code file, **check structure** — brace balance, a parser, the linter. Concatenating both sides of a conflict has silently nested one test inside another.

### 5. Health

Check whatever the project's `CLAUDE.md` declares as long-running: daemons, ports, model servers, disk. Never kill something you did not start.

### 6. Report

Call `/sitrep`, and add two things it does not cover:

- **The top open item in the requests lane, and whether a `slot=lane` lease exists for it** — computed (`grep -m1 '^- \[ \]' ASKS.md`; `ls .git/leases`), not remembered. One fleet spent 48 hours and 67 commits polishing an ask that was already done while the top open ask sat untouched, and logged every landing as `asks`. The first line of every report is the lane, and it is not allowed to be wrong.
- **What you did *not* do.** Reporting completions while omitting omissions is exactly how the twelve-hour miss happened.

If everything is healthy, the crew is full, and the lane is covered, say so in one line and stop. A quiet tick needs no narration.

---

## Blocked work must never block the fleet

An unattended run has one failure mode that looks exactly like success: nothing is broken, no agent has crashed, and no work is happening because something is waiting for an answer nobody is awake to give. The human wakes to a green status and an empty night.

In order of importance:

1. **A blocked item parks; its agent redispatches.** Never hold an agent idle against a question. Write down the blocker, move that agent to the next available work, raise the question in `DECISION NEEDED` for the next digest.
2. **Never ask what you can safely assume.** If a choice is reversible and one option is clearly the conservative one, take it and report the assumption. Reserve `DECISION NEEDED` for product principles and irreversible calls — where being wrong costs more than a night of throughput.
3. **Prefer a reduced-scope run to a stopped one.** Missing recipe, missing permission, ambiguous spec: there is nearly always adjacent work — hunts, audits, tests, findings — that needs none of the missing thing.
4. **Nothing here is a stop condition except the gate.** The gate refuses to merge, and it should; that is the one place where stopping is the correct answer. Everything else degrades instead: fewer agents, narrower scope, report-only. A refusing gate still leaves the rest of the crew working.

The morning test is not "was each stall legitimate?" — each one usually is. It is **"was there anything else the fleet could have been doing?"** There almost always was.

---

## The compass, and when to stop

A fleet with one objective — verified throughput — and no counter-force converts compute into accretion. On the project that showed this, six days of fleet work added 140K production lines and removed 18K; the only net-deleting commits were the human's. Every commit was chosen and every one passed the gate. The *codebase* still got worse to work in. Correctness is not the objective; it is a constraint. The objective is that the product is further along **and** the codebase is no harder to change than it was this morning.

**The compass.** Every 10 cycles, append the output of `python3 ~/.claude/skills/slop/scripts/slop_surface.py --at HEAD --compass` — verbatim, it is one line — to `$(git rev-parse --git-common-dir)/compass.log`, then run `/slop --quick` and add its grade to that line. A compass line that is not script output is a fabricated measurement: one fleet wrote `slop=not-taken scorecard=not-taken` and moved on, the record present and the reading absent, the same shape as a worker's invented lint half. The check-in refuses a compass line with no numbers in it. Compare to the previous line. A slop grade that fell, or sits below B, redirects the next product-seat dispatch to consolidation and suspends hunts until it recovers. This is scorecard and slop used as a *measurement of whether the fleet is helping*, not as a source of more tasks.

**Provenance.** Every merge appends to `$(git rev-parse --git-common-dir)/landings.log`: `<sha> <seat> <source: asks|inbox|roadmap|tracker|hunt|consolidation>`. **Source is the queue the item was pulled from at dispatch.** A follow-up to a done ask is `tracker`, not `asks` — polish on finished work is work the fleet invented, however good. This is what makes the next two rules mechanical instead of moods.

**The stall alarm.** A seat whose lease is older than six hours with no landing from it is not making progress, whatever its worker reports. The foreman's next message to that seat is not "continue" — it is a step-back brief: *stop; write down what you have tried and what each attempt showed; find how others solve this; come back with three approaches and a recommendation.* Lease age is `dispatched=` in the lease file, so this is computed, not felt. A worker that has revised the same artefact five times is the strongest possible signal that the approach, not the execution, is wrong.

**The stop condition** (a pre-commitment of the binding kind — it must not yield to "but the queue is full"): if the last 20 landings include none from `asks` or `inbox`, and the compass has not improved across its last two readings, **pause the fleet** and report: *"the fleet is feeding itself."* The human decides whether it continues. A team that cannot stop is not one you can leave unattended.

**Leave main readable.** A human reads every commit, and a night of `Merge core/shot` landings with their fix-the-fix trails is not what they should find. Whenever the fleet pauses or stops — the stop condition, an empty queue, the human's `stop` — and **no lease is held**, run `python3 ~/.claude/skills/consolidate/scripts/consolidate.py --apply --messages FILE` on main's unpushed range: it linearizes the landings and folds follow-ups into the work they amend, tree byte-identical. Write the messages — one per commit, what the change *is* in its final form — the default `<branch>: N changes` is a placeholder, not a message. Never do this while a lease is held (the script refuses: workers' branches are based on that history), and never push it: pushing is the human's, and the machine-wide pre-push gate refuses a range that isn't reader-ready, so an unconsolidated main is a morning chore for the human, not a mystery.

**The 8-hour check-in reports outcome, not activity.** Add to the format in *What reaches the human*, all of it computed from git and therefore *measured*: production lines added and deleted since the last check-in; public surface delta; slop and scorecard grade movement; and **the share of landings from `asks`/`inbox` versus the machine's own queue.** "In 8 hours: +12K lines, −400, surface +8%, 0 of 14 landings were things you asked for" is the sentence that tells the human whether the night was worth it.

---

## Dispatching an agent

Every brief carries five things. The body of the work can be an existing skill — tell the agent to run `/bug-bash` or `/scorecard` in its worktree where that fits, rather than restating the loop.

**1. Isolation — non-negotiable, and state it explicitly every time.**

```
Work in your OWN git worktree, branched from main:
  git worktree add <path> -b <branch> main
NEVER switch the shared checkout off its main branch.
NEVER use `git stash` — refs/stash is shared across every worktree of the
same repo (they share one .git dir), so a concurrent sibling agent's own
stash/pop can clobber or cross-apply into yours. For any "set this aside
and compare" need (including proving a fix's guard fails pre-fix and
passes post-fix), use a second throwaway worktree, a plain file copy, or
`git diff > file` instead.
NEVER edit any repository other than this one. If you need a change in
another project, file it: `request.py send <project> "<title>" --body …`
(the /request skill). A hook refuses Edit/Write into foreign repos.
Commit as you go. An agent lost all its work to `git checkout --` during
a tamper/restore cycle; a commit before any tamper is the cheapest guard.
```

Also name the project's shared singletons and how to avoid them (create your own device, use a private port, don't touch the shared instance), and the global-blast-radius files from `CLAUDE.md` that must not change without their marker.

**2. Scope** — one well-bounded task, with the specific files or subsystem named. **If the project has never built this kind of thing before** — a docs site, a benchmark harness, a TUI, a release pipeline — **the first brief is a research brief, not a build brief:** how do three comparable projects do it, what are the trade-offs, one recommendation, and the actions only the human can take named up front. One fleet spent a day producing documentation pages that read as development notes, rewrote four of them, and only then found Diátaxis — after the human read a page and said "the text is gibberish… how are they meant to understand it?" The research would have cost an hour. **Workers run only the tests scoped to their change**; the foreman re-establishes the full workspace gate before every merge regardless. Anything inherently long — simulator batches, fuzzers, full evals — is chunked per invocation with an internal wall-clock budget, and **the brief hands the worker the form, not a warning**: nine agents have stalled the same way (a command outlived the tool's foreground timeout, was auto-backgrounded, and the agent ended its turn waiting for a notification that never comes), and two of the last three had been warned in prose in their own briefs. The warning is the defect: telling an agent what not to do leaves it to invent the alternative under time pressure. Paste the long-command block from `references/fleet-tooling.md` into the brief. A run killed from outside and a run that found nothing look identical.

**3. Observation and goal, hypothesis last.** Five briefs in one day carried a false mechanism as their premise; every one was caught by the worker despite the framing, at the cost of disproving the dispatcher before starting. A diagnosis at the top doesn't just risk being wrong — it tells a capable agent where to look, and they look there (two rounds were spent fixing a normaliser when the data was already stored elsewhere). So: the brief states what was observed and what must be true afterwards; the dispatcher's hypothesis goes at the *end*, labelled as a hunch to check after forming their own view. Every factual claim in the brief is marked `(measured)` or `(assumed)`, and an assumed premise is the worker's *first task*, not the foundation. Read the target file's conventions before briefing work that writes to it.

**4. Rules of evidence** — `references/evidence.md`. Paste them in; do not assume they are known.

**5. Deliverable** — branch name, where findings go, the ask's `Done:` line restated (an ask without one is not dispatched; `start` asks for the missing ones), and *"an honest list of what you did not fix and why."* Ask for this explicitly and it usually arrives; omit it and it never does. **And the thesis, before implementing:** the worker's first commit body carries `Thesis: <one sentence that accounts for the whole change>` and `Surface: <public names, options, special cases added or removed, and why>`, and **any fix-shaped commit that deletes no production line carries a literal `Cause: <the defect, not the symptom>` trailer** — the gate's `slop_diff.py` looks for the token `^Cause:`, and a paragraph of prose explaining the cause does not satisfy it. Not "make it small" — "make it chosen." The gate refuses a branch without them, so it is a mechanism, not a request. (One fleet had four branches returned in a night for the missing `Cause:` token; every worker had explained the cause in prose, and 0 of 28 briefs had named the trailer. The gate enforces N things; the brief must name N, not N−1.) A consolidation brief adds: *lines removed and concepts reduced are the deliverable; new capability is a failure.*

### Model tiering

| Role | Tier |
|---|---|
| Architects, UX/design, contract review | opus |
| Coders, cross-cutting/protocol/async work | sonnet |
| Writing evals and tests; anything that reads a lot | haiku |

**Override for judgement-heavy work.** Reading volume is the wrong axis when being wrong is expensive and hard to detect. Adversarial hunting, interpreting a measurement, and reviewing someone else's merge all get sonnet or opus regardless of how much reading they involve. In the originating session, an agent interpreting eval results on a cheap tier needed **five rounds of correction** — a category error comparing metrics across differently-sized corpora, a gate that could not fail, an exemplar that failed its own test, and numbers silently carried between rounds — while heavy-reading hunters on a higher tier returned real bugs with honest omission lists.

---

## Commits

Write the reasoning, not the diff. A good message records: what was found, how it was verified, what was deliberately *not* fixed and why, and any correction to something previously claimed. Follow the project's own commit conventions for structure and trailers.

---

## Cost

Three workers and a foreman running continuously is not cheap; five is far more than five-thirds of it, because contention taxes every agent. Say so plainly on the first run of a project, and make the count easy to change. Throughput is the point, but an unattended overnight run is a real spend and the human should choose it deliberately.

---

## Safety

- Never touch a production instance: its ports, its data directory, its credentials, its process manager. Have the project name them in `CLAUDE.md` and treat that list as guard-blocked.
- Never edit another project's repository. File a `/request`; a hook refuses the write anyway.
- Credentials and personal data stay out of agent context. Agents work against fixtures. If a model must read real data, delegate to a local one and orchestrate without seeing it.
- Real-data findings become synthetic fixtures plus a regression test — never a copy of the real data.
- Never kill a shared process you did not start.
