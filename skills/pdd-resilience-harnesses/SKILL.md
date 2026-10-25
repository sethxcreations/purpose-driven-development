---
name: pdd-resilience-harnesses
description: Apply the Law of Obstacle-Grounded Centralization - bind code to canonical constitutional harnesses (bounded 480-byte ring-buffer circuit breaker with a 20-attempt floor, partition-resilient consumer with idempotency and dead-letter routing) instead of writing retries, fallbacks, breakers, or consume loops by hand. Use whenever code calls a remote dependency, consumes messages, or handles an operational failure mode.
---

# Bind to constitutional harnesses

Left alone, an agent handles each edge case where it notices it: a retry
loop here, a try/except there, a timestamp list for failure rates somewhere
else. The result is scattered, inconsistent, and often unbounded. PDD models
each failure mode once as an obstacle, resolves it once, and implements the
resolution in one harness that everything binds to.

## Reference harnesses (`harnesses/python/`)

### Ring-buffer circuit breaker (OPS-002, OPS-004)

- 60 one-second buckets per destination, each two unsigned 32-bit counters
  (attempts, failures): **480 bytes per destination, fixed**. 40,000
  destinations ≈ 20–25 MB regardless of retry-storm volume.
- Opens only when the window holds **at least 20 attempts** and the failure
  ratio crosses the threshold, so a handful of failures at low traffic cannot
  trip it.
- Half-open single probe after the open interval.
- `call(destination, fn, fallback=…, retries=2)` gives bounded, jittered
  exponential backoff.

Why not a deque of timestamps: it is O(1) amortized per call but its memory
grows with traffic. One destination in a retry storm accumulates hundreds of
thousands of entries and takes the worker down.

### Partition-resilient consumer (OPS-003)

- Idempotency by event key; redeliveries are skipped.
- Bounded retries for transient errors only; validation errors go straight to
  the dead-letter store.
- **The offset always advances**, so one poison event cannot block the other
  events hashed to its partition (a single malformed message otherwise idles
  the consumer while lag climbs into the hundreds of thousands).
- Per-partition lag for alerting. Pair it with a transactional outbox on the
  producing side.

Port these to your language if needed; keep the bounds and behaviour, and
keep the tests in `tests/test_harnesses.py` as the specification.

## Procedure

1. **Identify the obstacle** your code faces (timeout, 5xx, poison event,
   duplicate delivery, invalid input, unauthorized caller). Find it in
   `purpose-graph.yaml`. If it is missing, add it (`pdd-operational-contracts`).
2. **Find its resolution contract and canonical artifact.** Use `pdd lens` on
   the harness, or search `resolves:` in the graph.
3. **Bind, don't re-implement.** Create or reuse one binding per dependency
   (for example `psp_breaker = CircuitBreaker(...)` in `payments/resilience.py`)
   and call through it. Remove any local retry loop, sleep, or bespoke fallback
   you were about to write.
4. **Remove scattered handling** you find nearby: per-call retries, nested
   try/except that swallow errors, duplicate validation. These violate
   OPS-002 and Minimal Sufficiency.
5. **Keep the hot path asynchronous** where the contract allows: move
   expensive remote calls off user-facing request paths into workers (OPS-001),
   or give them a timeout and a fallback.
6. **Test the obstacle**: one robustness test per obstacle in the contract's
   verification suite (timeout, storm, poison event, redelivery).

## Adding a new harness

When the same obstacle appears in three or more contracts with no harness,
propose one: a resolution contract, one implementation with tests that pin its
bounds, a constitution invariant with `harness:` pointing at it, and a
migration PR that replaces the scattered handling.
