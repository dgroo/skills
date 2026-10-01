---
name: delegate-private
description: Run a task on a local Ollama model so data never leaves the device. Use for personal notes, PII, or confidential files.
argument-hint: <task, referring to files by path only>
---

# Delegate: on-device only (local qwen3.6)

For tasks over data the user never wants leaving the device. The model runs locally via Ollama (127.0.0.1); `--offline --no-extensions` keeps `pi` itself from any network calls.

```bash
pi -p --offline --no-extensions --provider ollama --model qwen3.6:35b-mlx \
  --session-id delegate-private "<brief>"
```

## Privacy protocol — this is the entire point of this agent

1. **Never read the private material yourself** — no Read, cat, grep, head on it. Anything that enters your context leaves the device. Refer to it by path only.
2. Brief the local agent with paths, not content: "Read ~/notes/medical.md and summarize action items into ~/notes/medical-summary.md."
3. **Tell it to write output to a file and reply with only the file path and a one-line non-sensitive status.** Its stdout comes back into your context, so sensitive content must not appear there.
4. Don't read its output files afterward. Report the path to the user and stop.
5. If the user asks you to look at the content directly, point out it would leave the device via your context, and confirm before proceeding.

The 35B model takes ~30s to load if cold and generates slower than cloud models — use a long timeout or `run_in_background`.

## Continuity

Always pass `--session-id delegate-private`. Follow-up delegations continue with full memory of prior exchanges. Use a new id (`delegate-private-2`) to start fresh.
