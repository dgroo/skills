---
name: delegate-bulk
description: Bulk low-judgement work on a near-free model via pi: mass review, sample data, mechanical rewrites. Non-private data only.
argument-hint: <task>
---

# Delegate: cheap high-volume grunt work

For mountains of simple work that doesn't need much intelligence: reviewing lots of content, generating test/sample data, mechanical rewrites. Never for privacy-sensitive data — use `/delegate-private` for that instead.

```bash
pi -p --provider openrouter --model google/gemini-2.5-flash-lite --no-session "<brief>"
```

**Zero data retention (ZDR):** the user's OpenRouter account rejects non-ZDR endpoints.

- `google/gemini-2.5-flash-lite` is near-free, reliable, and passes the account's ZDR policy. Truly free models exist (`pi --list-models ":free"`, e.g. `z-ai/glm-5.2:free`) but are shared-pool rate-limited (frequent 429s) and most lack ZDR endpoints, so the account rejects them. Prefer flash-lite.
- Use `--no-session` — bulk items don't need memory. Add `--no-tools` when the task is pure text generation (faster, no risk of it wandering the filesystem).
- Fan out for volume: split the work into items and run pi calls in parallel (e.g. a small Python script with `concurrent.futures.ThreadPoolExecutor` — see `delegate-image/scripts/image-panel.py` for the pattern), each writing to its own output file. Spot-check a sample of outputs yourself before declaring the batch done.
