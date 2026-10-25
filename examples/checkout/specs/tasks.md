# Tasks: Checkout payment

## T-001 — Bind the payment provider to the circuit-breaker harness
- **Implements:** OC-RES-PSP-FAILURE · **Constrained by:** OPS-001, OPS-002, OPS-004
- **Reuse gate:** reuse `harnesses/python/circuit_breaker.py` (Φ 1.0)
- **Create:** `src/payments/resilience.py` (workflow)
- **Done when:** breaker has min_samples ≥ 20; no retry loop outside the harness.

## T-002 — Idempotent authorizer for card and wallet
- **Implements:** OC-PAY-AUTH · **Constrained by:** SEC-002, SEC-003, SEC-004, OPS-001
- **Reuse gate:** create (closest Φ 0.41)
- **Create:** `src/payments/authorize.py` (method) · **Must not touch:** tests of other contracts
- **Done when:** all four verification tests pass; `pdd check` and `pdd guard` clean.

## T-003 — Authorize endpoint
- **Implements:** OC-PAY-AUTH · **Constrained by:** SEC-003, SEC-004, API-001
- **Create:** `src/api/orders.py` (api) — the only payment endpoint.

## T-004 — Order confirmation worker
- **Implements:** OC-ORDER-CONFIRM · **Constrained by:** SEC-002, SEC-004, OPS-003
- **Reuse gate:** bind to `partition_consumer.py`
- **Create:** `src/workers/order_events.py` (worker)

## T-005 — Checkout screen with agent-assisted variant
- **Implements:** OC-CART-VIEW · **Constrained by:** UI-001 … UI-004
- **Reuse gate:** extend `CheckoutScreen.tsx` with `variant` (Φ 0.78)

## Compliance traceability matrix

| Invariant / clause | Contract | Artifact | File:line | Test |
|--------------------|----------|----------|-----------|------|
| SEC-003 RBAC | OC-PAY-AUTH | A-PAY-AUTHORIZE | `src/payments/authorize.py:25` | test_authorize_forbidden |
| SEC-002 parameterized SQL | OC-PAY-AUTH | A-PAY-AUTHORIZE | `src/payments/authorize.py:27,32,41` | static (`pdd check`) |
| ReqPost idempotent per cart | OC-PAY-AUTH | A-PAY-AUTHORIZE | `src/payments/authorize.py:32` | test_authorize_idempotent |
| ReqPost event emitted | OC-PAY-AUTH | A-PAY-AUTHORIZE | `src/payments/authorize.py:45` | test_authorize_happy_path |
| X-PSP-TIMEOUT | OC-RES-PSP-FAILURE | A-PSP-BREAKER | `src/payments/authorize.py:37` | test_authorize_psp_timeout |
| SEC-004 boundary validation | OC-PAY-AUTH | A-API-AUTHORIZE | `src/api/orders.py:10` | test_post_authorize_rejects_bad_body |
| OPS-003 consumer harness | OC-ORDER-CONFIRM | A-ORDER-WORKER | `src/workers/order_events.py:18` | tests/test_harnesses.py |
| UI-001 one-way state | OC-CART-VIEW | A-CHECKOUT-STORE | `src/ui/state/checkoutStore.ts:18` | reducer tests |
