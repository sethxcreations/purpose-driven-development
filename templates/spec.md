# Spec: <feature name>

> Tier 2–3 of the spec cascade. States WHY and WHAT, never HOW.
> Constitution version: `<x.y.z>` · Sealed: run `pdd seal <dir>` after review.

## Strategic purpose

| ID | Statement | Stakeholders | Success measure | Status |
|----|-----------|--------------|-----------------|--------|
| P-… | <who gets what value> | <roles> | <observable outcome> | active |

**WHY does this matter now?** <one paragraph; if you cannot answer, stop here>

## Functional intents

Refine the purpose by asking **HOW?** until each leaf is a capability one agent
(a service, a worker, a UI, or a person) can own. Ask **WHY?** of every leaf to
confirm it climbs back to the purpose.

| ID | The system can… | Refines | Refinement | Entities |
|----|-----------------|---------|------------|----------|
| I-… | <capability, technology-agnostic> | P-… | AND | <entities> |

```
P-…
└─ AND
   ├─ I-…
   └─ OR
      ├─ I-…
      └─ I-…
```

## Existing capabilities that already serve these intents

Fill this from the reuse gate (`pdd-reuse-gate` skill) before writing the plan.

| Intent | Closest existing artifact | Φ | Decision (reuse / extend / new) |
|--------|---------------------------|---|-------------------------------|
| I-… | `path::symbol` | 0.00 | |

## Applicable constitutional invariants

| Invariant | Level | Why it applies |
|-----------|-------|----------------|
| SEC-003 | MUST | <reason> |

## Out of scope

- <explicitly excluded capability, so no agent builds it>

## Open questions

- <question> — owner, due date
