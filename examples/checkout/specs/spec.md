# Spec: Checkout payment

> Constitution version: `1.0.0` · Sealed in `.pdd-seal.json`

## Strategic purpose

| ID | Statement | Stakeholders | Success measure | Status |
|----|-----------|--------------|-----------------|--------|
| P-CHECKOUT | Shoppers can pay for their cart quickly and safely, so completed orders grow without fraud losses growing. | shopper, finance, support | Checkout conversion ≥ 62% with chargeback rate < 0.3% | active |

**WHY now?** Conversion fell after the payment provider migration; support sees
duplicate charges when shoppers press Pay twice.

## Functional intents

| ID | The system can… | Refines | Refinement | Entities |
|----|-----------------|---------|------------|----------|
| I-REVIEW-CART | let the shopper review and edit the cart before paying | P-CHECKOUT | AND | Cart |
| I-PAY | take payment for a cart | P-CHECKOUT | AND | Cart, Payment |
| I-PAY-CARD | authorize a card payment | I-PAY | OR | Payment |
| I-PAY-WALLET | authorize a wallet payment | I-PAY | OR | Payment |
| I-CONFIRM | confirm a paid order to the shopper and fulfilment | P-CHECKOUT | AND | Order |

```
P-CHECKOUT
└─ AND
   ├─ I-REVIEW-CART
   ├─ I-PAY
   │  └─ OR
   │     ├─ I-PAY-CARD
   │     └─ I-PAY-WALLET
   └─ I-CONFIRM
```

## Existing capabilities that already serve these intents

| Intent | Closest existing artifact | Φ | Decision |
|--------|---------------------------|---|----------|
| I-PAY-CARD, I-PAY-WALLET | `src/payments/authorize.py::authorize_payment` | 0.91 (same contract for both methods) | reuse: one authorizer for both, method is a parameter |
| I-REVIEW-CART | `src/ui/CheckoutScreen.tsx` | 0.78 (agent-assisted variant requested) | extend: `variant` prop, no copied screen |
| I-CONFIRM | none | — | new worker, bound to the partition consumer harness |

## Applicable constitutional invariants

| Invariant | Level | Why it applies |
|-----------|-------|----------------|
| SEC-002, SEC-004 | MUST | SQL and external input in payments and the order worker |
| SEC-003 | MUST | the authorize endpoint |
| OPS-001, OPS-002, OPS-004 | MUST | calls to the payment provider |
| OPS-003 | MUST | the order worker |
| UI-001 … UI-004 | MUST / SHOULD | checkout screen and store |

## Out of scope

- Saved cards, refunds, the retired spring-promotion banner (P-SPRING-PROMO).
