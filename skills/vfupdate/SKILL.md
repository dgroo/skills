---
name: vfupdate
description: Sync the Verifact demo (demo-local branches) to upstream sandbox while using the demo as a regression smoke test — run the demo suite before, update the code from upstream, run it again, and report the delta (what got fixed, what newly broke, what's still broken). Use when asked to "catch up the demo", "pull upstream Verifact code", "update and check the demo", "/vfupdate", or to check whether an upstream sync broke anything.
---

# vfupdate — update the Verifact demo and regression-check it

Turns the Verifact demo into a smoke test across an upstream code sync. The demo's `demo-local` branches sit on a snapshot of `origin/sandbox`; upstream moves; this skill pulls the new code and tells you, concretely, what the update fixed and what it broke — so a sync is never a silent regression.

Runs in Derek's `~/code/verifact` workspace. The `misinformation-*` org subrepos each carry a local-only `demo-local` branch with the demo/test/autobot work; **nothing here is pushed to the org**.

## Scope of "the demo" (today)

The full 17-beat demoBot doesn't exist yet, so the smoke suite is the **demo-critical authed e2e specs** run against the local stack with the settlement poller up — currently `uibot-place-cancel` (place+cancel) and `fill-and-sell` (fill → on-chain settle → position; sell-back). Extend `VF_SMOKE_SPECS` / `scripts/vfdemo-smoke.sh`'s default as demoBot grows. As demoBot matures, this skill's "run the demo" step becomes "run demoBot in smoke mode".

## Hard rules

- **Sandbox off for the runs.** The specs and the poller need `.env` + localhost + network, which the CC sandbox blocks. Run the poller and `vfdemo-smoke.sh` with the sandbox disabled.
- **Never force-resolve a rebase conflict.** If `git rebase origin/sandbox` conflicts, STOP and surface the conflicting files. Our footprint is tiny (autobot files, e2e specs, one-line package.json scripts), so conflicts should be rare and are almost always in `fill-and-sell.spec.ts` — show Derek the conflict and let him decide.
- **Don't push `demo-local`.** It stays local (org repos are hands-off).
- **Report faithfully.** A spec that was already failing before the update is NOT a regression; only a spec that went pass→fail is. Keep those distinct.

## Process

### 1. Preflight
- `git -C misinformation-backend fetch origin` and same for frontend (sandbox off). Report drift: `git rev-list --count HEAD..origin/sandbox` per repo.
- Confirm the stack is up: backend `:5001`, orderbooks `:8001`, frontend `:3000`, Docker infra (`docker ps` → `verifact-mongo/redis/localstack`). If anything's down, bring it up (or tell Derek what to start) before proceeding.
- Confirm working trees are clean on both `demo-local` branches (`git status`). If dirty, stop and surface.

### 2. Baseline run (before)
- Start the settlement poller (sandbox off; it must read `.env`):
  `cd misinformation-backend && NODE_ENV=local TS_NODE_TRANSPILE_ONLY=true ./node_modules/.bin/ts-node src/autobot/settlementPoller.ts > ~/code/verifact/scratchpad/autobot.log 2>&1 &` (run in background).
- Run the suite: `scripts/vfdemo-smoke.sh baseline` (sandbox off). This writes `scratchpad/vfupdate/run-baseline.{log,summary}`.
- Read `run-baseline.summary`. Note the current known issues (e.g. as of 2026-07-06: `fill-and-sell` fill passes, sell-back's Confirm-Sell submission fails).

### 3. Update from upstream
- For each of `misinformation-backend`, `misinformation-frontend`: `git rebase origin/sandbox` on `demo-local`. On conflict → STOP, surface, wait for Derek.
- If `package.json`/lockfile changed in the rebase, reinstall: `npm ci` (or `npm install`) in that repo.
- Restart the stack so the new code is live (backend/frontend/orderbooks). Re-init LocalStack queues if needed (`dev/init-localstack-queues.js`). Restart the poller (new handler code).

### 4. After run
- `scripts/vfdemo-smoke.sh after-update` (sandbox off) → `run-after-update.{log,summary}`.

### 5. Diff report
Compare `run-baseline.summary` vs `run-after-update.summary` per spec and render a clear report:

```
## /vfupdate report — <date>
Updated: backend <N> commits, frontend <M> commits (→ sandbox <shorthash>)

| spec | before | after | verdict |
| ---- | ------ | ----- | ------- |
| uibot-place-cancel | ✅ | ✅ | ➖ unchanged |
| fill-and-sell:fill | ✅ | ❌ | ❌ NEWLY BROKEN — <reason/line> |
| fill-and-sell:sell-back | ❌ | ❌ | ⚠️ still broken (pre-existing) |

★ Regressions from this update: <the pass→fail rows, or "none">
Fixed by this update: <the fail→pass rows, or "none">
Still broken (pre-existing): <fail→fail rows>
```
- **Lead with regressions** (pass→fail) — those are what the update broke and need attention. Distinguish clearly from pre-existing failures.
- For each newly-broken spec, read its failure in `run-after-update.log` and give the actual reason (stale selector, changed API, etc.) — upstream churn in the order/sell/settlement code is the usual culprit.
- Stop the poller when done (or note it's left running). Leave the two summary files in place for reference.

### 6. Workaround check
An upstream sync is exactly when the product may have fixed something the demo currently works around — so the workaround becomes dead weight (or actively wrong). Run the checker (no sandbox needed — it only reads files in the org clones):

```
node scripts/vfdemo-check-workarounds.mjs
```

It probes each active demoBot workaround in `scripts/vfdemo-workarounds.json` (e.g. the tile-volume paint keyed to the FE's hardcoded `$0 vol`, the comments stub) and flags any whose underlying product gap looks fixed upstream — exit 1 if there's anything to revisit. Fold its output into the report:

```
Workarounds: <N active, M flagged to revisit — or "all still needed">
```

For each ⚠ flagged item, confirm whether the real code path now works, and if so remove the workaround (and its registry entry) as its own commit. This is the mechanism that stops us shipping a demo that fakes something the product now does for real — the `fee-zero` entry is the archetype (upstream shipped it; we deleted the plan to hack it).

## Notes
- Commit any demo fixes made to un-break things as their own `test(demo)`/`fix(autobot)` commits on `demo-local` (never pushed).
- If the rebase pulls handler-signature changes into the settlement path (`orderServiceV2.ts`, the queue handlers the poller imports), the poller may need updating — the `fill-and-sell:fill` row going red is the signal.
- This is Derek's personal workflow skill; it lives in `dgroo/skills`, not the org repos.
