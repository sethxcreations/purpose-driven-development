# Plan: <feature name>

> Tier 4 of the spec cascade: Operational Contracts and Obstacles.
> Derived from `spec.md`. Every contract operationalizes exactly the leaf intents named.

## Operational contracts

### OC-… — <summary>

- **Operationalizes:** I-…
- **Agent:** <service / worker / UI / role>
- **DomPre:** <domain state before>
- **DomPost:** <domain state after>
- **ReqPre:** <conditions the software checks before acting>
- **ReqPost:** <conditions the software guarantees after>
- **ReqTrig:** <event that obliges the operation>
- **Constrained by:** SEC-…, OPS-…
- **Tools allowlisted (agents):** <tool names, or none>
- **Verification suite (I_o):** <tests that prove ReqPost, including robustness and security cases>
- **Implementation strata:** <which of block, screen, elem, state, api, worker, workflow, class, method, import>
- **Reuse:** <existing artifacts this contract will call or extend, from the reuse gate>

## Obstacles

For each contract ask: *what could be true of the world that makes ReqPost false?*
Consider unavailable dependencies, malformed or hostile input, timeouts,
duplicates, partial failure, concurrency, misuse by an authorized user, and an
agent pursuing the wrong goal.

| ID | Condition | Obstructs | Likelihood | Resolved by |
|----|-----------|-----------|------------|-------------|
| X-… | <assertion that entails violation> | OC-… | high | OC-RES-… |

## Resolution contracts

Each obstacle is mitigated **once**, by a resolution contract with a single
canonical implementation (usually a harness). Downstream code must not add its
own retries, fallbacks, or defensive checks for the same obstacle.

| ID | Resolves | Canonical mechanism | Already exists? |
|----|----------|---------------------|-----------------|
| OC-RES-… | X-… | `harnesses/…` | yes / no |

## Minimal sufficiency notes

<Why the planned artifact set is minimal: which artifact covers which ReqPost
clause, and what would break if any were removed.>

## Graph update

<The purpose-graph.yaml diff this plan introduces.>
