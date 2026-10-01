# scorecard — a finished report

Part of the `/scorecard` skill; read once to learn the shape of the output. The process is in `SKILL.md`.

## Worked Example

```
# Codebase Scorecard: payment-service

**Audited**: 2026-03-06 | **Size**: 42 files, 8.2 KLOC | **Language(s)**: TypeScript

| # | Category          | Grade | Key Finding |
|---|-------------------|-------|-------------|
| 1 | Architecture      | A-    | Clean adapter pattern, single responsibility |
| 2 | Code Quality      | B+    | One off-by-one in retry logic |
| 3 | Consistency       | A     | Uniform error handling and naming throughout |
| 4 | Security          | A     | Input sanitized, no secrets in code |
| 5 | Performance       | B     | Minor: unbatched DB reads in reconciliation |
| 6 | DRY               | B     | Validation logic duplicated in 2 handlers |
| 7 | Testability       | A     | DI throughout, pure business logic functions |
| 8 | Test Coverage     | B     | 80% coverage, needs E2E for webhook flow |
| 9 | Type Safety       | A     | Full TypeScript strict, no `any`, proper generics |
| 10| Documentation     | B-    | Missing JSDoc on PaymentProcessor class |
| 11| Error Handling    | B+    | Good custom error classes, add retry for transient |
| 12| Extensibility     | A     | Easy to add new payment providers via adapter |
| 13| Repo Hygiene      | A-    | Clean history, CI configured, one stale branch |

**Overall: B+**

### Top Strengths
- Adapter pattern in `src/providers/` makes adding payment providers trivial — add one file, register in factory
- Custom error hierarchy (`PaymentError` → `ValidationError` | `ProviderError` | `TimeoutError`) with proper propagation
- Comprehensive TypeScript strict mode, zero `any` usages, well-typed generics on `Result<T, E>`

### Critical Issues
- **MEDIUM [Bug]** `src/retry.ts:45` — off-by-one in exponential backoff: `delay = baseDelay * (2 ** attempt)` should be `2 ** (attempt - 1)` since `attempt` is 1-indexed. First retry waits 2x too long.
- **MEDIUM [Performance]** `src/reconciliation.ts:112-130` — reconciliation handler loads transactions one-by-one in a loop instead of batching. Will hit N+1 at scale.

### Architecture Assessment
Clean layered architecture. The provider adapter pattern (`src/providers/base.ts` → Stripe, PayPal, etc.) is well-designed and follows open/closed principle. Business logic is properly separated from I/O in `src/domain/`.

The one concern is that `src/handlers/webhook.ts` (340 lines) is doing too much — parsing, validation, idempotency checking, event dispatching, and error recovery. This should be split into a webhook parser and an event dispatcher.

### Quick Wins
1. Extract `src/validation.ts:45-89` shared logic from `src/handlers/charge.ts:23-67` — removes duplication, DRY grade → A-
2. Add JSDoc to `PaymentProcessor` and `ProviderFactory` public methods — Documentation grade → B+
3. Fix retry off-by-one — Code Quality grade → A-
```

