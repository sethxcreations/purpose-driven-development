# Plan: Checkout payment

## Operational contracts

### OC-PAY-AUTH — Authorize a card or wallet payment for a cart total

- **Operationalizes:** I-PAY-CARD, I-PAY-WALLET
- **Agent:** payments-service
- **DomPre:** Cart is priced and locked.
- **DomPost:** Exactly one authorization exists for the cart, or none and the cart is unlocked.
- **ReqPre:** caller holds `payments:authorize` for the cart's account; amount equals the locked total.
- **ReqPost:** authorization is idempotent per cart id; outcome emitted as `payment.authorized` or `payment.declined`.
- **ReqTrig:** shopper submits payment.
- **Constrained by:** SEC-002, SEC-003, SEC-004, OPS-001, API-001
- **Verification:** test_authorize_happy_path, test_authorize_idempotent, test_authorize_forbidden, test_authorize_psp_timeout
- **Strata:** api, method

### OC-ORDER-CONFIRM — Confirm the order and notify fulfilment

- **Operationalizes:** I-CONFIRM
- **Agent:** order-worker
- **ReqPre:** event schema is valid.
- **ReqPost:** idempotent per payment id; poison events dead-lettered without stalling the partition.
- **ReqTrig:** `payment.authorized`
- **Constrained by:** SEC-002, SEC-004, OPS-003
- **Strata:** worker

### OC-CART-VIEW — Show the cart with editable quantities and the payable total

- **Operationalizes:** I-REVIEW-CART
- **Agent:** web-client
- **ReqPost:** displayed total equals the server-priced total; one-way state flow; keyboard accessible.
- **Constrained by:** UI-001, UI-002, UI-003, UI-004
- **Strata:** screen, state

## Obstacles

| ID | Condition | Obstructs | Likelihood | Resolved by |
|----|-----------|-----------|------------|-------------|
| X-PSP-TIMEOUT | Provider does not answer within 2 s or returns 5xx | OC-PAY-AUTH | high | OC-RES-PSP-FAILURE |
| X-POISON-EVENT | `payment.authorized` is malformed or names an unknown cart | OC-ORDER-CONFIRM | medium | OC-RES-POISON-EVENT |

Duplicate submissions are not an obstacle here: ReqPost idempotency covers them.

## Resolution contracts

| ID | Resolves | Canonical mechanism | Exists? |
|----|----------|---------------------|---------|
| OC-RES-PSP-FAILURE | X-PSP-TIMEOUT | `psp_breaker` bound to `harnesses/python/circuit_breaker.py` | harness yes, binding new |
| OC-RES-POISON-EVENT | X-POISON-EVENT | `harnesses/python/partition_consumer.py` | yes |

## Minimal sufficiency notes

The authorizer covers both payment methods (OR-refinement served by one
contract). The API handler only validates and delegates. The store holds one
discriminated union; `totalCents` is a selector, not stored state.
