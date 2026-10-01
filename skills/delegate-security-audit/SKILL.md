---
name: delegate-security-audit
description: Security audit by GLM via pi: find and fix vulnerabilities in the user's own code. Use when asked for an audit or vuln hunt.
argument-hint: <scope of the audit>
---

# Delegate: security analysis (GLM 5.3)

For authorized security work on the user's own code: audits, vulnerability hunting, and fixing what's found. GLM runs through `pi`, using the user's OpenRouter key — never ask for or echo API keys.

**Zero data retention (ZDR):** the user's OpenRouter account rejects non-ZDR endpoints. If a model 404s with "No endpoints available matching your … data policy," that's the account's ZDR-only policy working as intended — don't suggest loosening it, pick a different model.

## Running it

```bash
cd <repo-root> && pi -p --provider openrouter --model z-ai/glm-5.3 \
  --thinking high --session-id delegate-sec "<brief>"
```

- This is a full coding agent with read/bash/edit/write tools in the repo — it can apply fixes, not just report.
- Brief it with scope and deliverable, e.g.: "Audit the auth and session-handling code in src/ for vulnerabilities (injection, authz bypass, secrets handling, SSRF). Fix what you find, and summarize each issue, severity, and fix."
- Long audits can run many minutes: use `run_in_background` and report when it finishes.
- Afterward, run `git diff` and review its changes yourself before presenting them — you own the final quality bar.

## Continuity

Always pass `--session-id delegate-sec`. The first call warns "creating a new session" — that's normal. Follow-up delegations continue with full memory of prior exchanges. Use a new id (`delegate-sec-2`) to start fresh.

## Reporting back

- Lead with GLM's findings, clearly attributed ("GLM found 3 issues: …").
- These delegations cost real money — don't loop them unattended without the user asking.
