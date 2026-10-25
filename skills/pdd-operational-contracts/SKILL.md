---
name: pdd-operational-contracts
description: Turn leaf Functional Intents into Operational Contracts (DomPre, DomPost, ReqPre, ReqPost, ReqTrig) and run KAOS obstacle analysis, defining one resolution contract per obstacle. Use when planning how a capability will behave, before implementation, or when edge-case handling is scattered.
---

# Write operational contracts and obstacles (Tier 4)

An **Operational Contract** makes a leaf intent precise enough to implement
and verify. An **Obstacle** is a condition that is consistent with the domain
yet entails the contract's violation ({O, Dom} ⊭ false and {O, Dom} ⊨ ¬G).
Each obstacle is mitigated by a **Resolution Contract**, defined once.

## Contract fields

| Field | Meaning | Example |
|-------|---------|---------|
| `operationalizes` | Leaf intent(s) | `I-PAY-CARD` |
| `agent` | Who is responsible | `payments-service` |
| `dom_pre` | Domain state before | Cart is priced and locked |
| `dom_post` | Domain state after | One authorization exists for the cart |
| `req_pre` | What the software must check before acting | caller holds `payments:authorize` |
| `req_post` | What the software must guarantee after | idempotent per cart id; event emitted |
| `req_trig` | Event that obliges the operation | shopper submits payment |
| `constrained_by` | Constitutional invariants that apply | `SEC-003`, `OPS-001` |
| `tools` | Agent tools allowlisted for this contract | `[]` |
| `verification` | Tests that prove `req_post` (the suite I_o) | `test_authorize_idempotent` |

Write `req_pre` and `req_post` as separate, individually testable clauses.
They are what the contract-coverage check and the trace gate verify.

## Procedure

1. For each leaf intent, write one contract per responsible agent. If a
   contract would need two agents, the intent was not a leaf.
2. Attach every in-scope invariant to `constrained_by`. The checker fails the
   build if an artifact in an invariant's scope implements a contract that
   omits a MUST invariant.
3. **Obstacle analysis.** For each `req_post` clause, negate it and ask what
   state of the world would make that negation true. Walk this list:
   - dependency unavailable, slow, or returning errors;
   - input malformed, oversized, duplicated, out of order, or hostile;
   - partial failure between two writes;
   - concurrent actors on the same entity;
   - an authorized user misusing the capability;
   - a poison message on a partitioned stream;
   - retry storms and traffic spikes;
   - an AI agent pursuing a proxy goal (passing tests, silencing errors).
   Record each as an obstacle with `obstructs:` and a likelihood.
4. **Resolve each obstacle once.** Search existing resolution contracts first;
   most systems need only a handful (dependency failure, poison event, invalid
   input, unauthorized caller, duplicate request). Link with `resolves:`. The
   resolution contract is implemented by exactly one canonical mechanism,
   usually a harness (`pdd-resilience-harnesses`). Downstream code calls it and
   adds nothing of its own.
5. **Name the verification suite** for each contract: functional cases,
   robustness cases (one per obstacle), and security cases (one per
   constraining invariant). This suite is I_o in the Law of Minimal Sufficiency.
6. Update `purpose-graph.yaml` and `plan.md`; run `python tools/pdd.py check`.

## Signs a contract is wrong

- `req_post` says "handles errors gracefully": not testable. Name the errors and outcomes.
- Two contracts with the same `dom_post` on the same entity: likely duplicates.
- An obstacle mitigated inside the contract's own implementation with a
  try/except and a retry: move it to a resolution contract.
- No obstacles at all: the analysis was skipped.

## Output

- `contracts:` and `obstacles:` in `purpose-graph.yaml`, passing `pdd check`.
- The Operational contracts, Obstacles, and Resolution contracts sections of `plan.md`.
