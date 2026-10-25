---
name: pdd-closeness-mapping
description: Measure closeness between two or more artifacts in the same stratum (screens, design blocks, UI elements, state, APIs, workers, workflows, classes, methods, imports) with Φ = α·structural + β·semantic + γ·teleological similarity, and consolidate true duplicates with the right stratum-specific merge. Use when you suspect duplication, before merging similar code, or when cleaning up clones.
---

# Closeness mapping and consolidation

Bottom-up clone detection fails both ways: things that look alike may serve
different purposes, and AI-generated Type-4 clones look different but do the
same thing. PDD fuses three signals:

**Φ(a_i, a_j) = α·Sim_struct + β·Sim_sem + γ·Sim_teleo**, α+β+γ = 1
(default 0.3 / 0.3 / 0.4).

**Teleological closeness** is the specificity-weighted Jaccard similarity of
the two artifacts' ancestor contracts, intents, and purposes:

Sim_teleo = Σ_{u ∈ T(a_i) ∩ T(a_j)} Spec(u) / Σ_{v ∈ T(a_i) ∪ T(a_j)} Spec(v),
Spec(u) = 1 / |Desc(u)|

A shared narrow contract counts a lot; a shared broad purpose counts little.

```bash
python tools/pdd.py closeness A-1 A-2 --struct 0.4 --sem 0.7 --scan src
python tools/pdd.py lens A-1 --scan src     # lists nearest teleological neighbours
```

## Per-stratum signals

| Stratum | Sim_struct | Sim_sem | Merge move |
|---------|-----------|---------|------------|
| Screens, design blocks | DOM TreeBLEU (shared height-1 subtrees), tree edit distance, Container Match (IoU of containers); visually SSIM/CLIP | Screen2Vec-style text + component + layout embedding | Hoist the shared subtree into one component; turn the differences into typed props or keyframes keyed on `userRole`, `viewportSize`, `workflowStage` (FrameKit) |
| Screen elements | Subtree isomorphism, prop/CSS overlap | label and role text | Replace with a design-system primitive with variants |
| Application / UI state | State-transition graph isomorphism, overlapping binding paths | slice and identifier names | Collapse flags and mirrored slices into one normalized state machine; derive the rest with selectors |
| APIs | JSON Schema tree match on params and responses, same verb | embedding of summary, description, operationId, path tokens; whole-service responsibility | Unify routes; union response fields behind a projection parameter; deprecate the duplicate behind a gateway rewrite |
| Workers, workflows | CFG similarity; equivalent post-states (weakest precondition) | event schema and trace similarity | Merge handlers into one consumer group with shared dead-letter and breaker harnesses |
| Classes, methods | AST/PDG similarity | code embeddings of the essential statements | Extract an interface ("can-do") and inject it; replace clones with calls to the canonical one; prefer built-ins |
| Imports | call-graph reachability of used symbols | package purpose and API surface | Rewrite call sites to the lowest-bloat, lowest-CVE package; remove the other |

An agent without these tools estimates each on 0–1 by reading both artifacts
side by side, and states the evidence ("both validate card number with Luhn,
same inputs and outputs, different loops: Sim_sem ≈ 0.9").

## Procedure

1. **Pick candidates** in one stratum: `pdd lens` neighbours, name and entity
   search, or a clone detector's output (jscpd, PMD CPD, Simian, SonarQube).
2. **Score** Sim_struct, Sim_sem, Sim_teleo and Φ. Show the numbers.
3. **Decide.**
   - Φ ≥ τ_merge (default 0.85) **and** same or nested contracts: merge.
   - High Sim_struct but low Sim_teleo (different purposes, conflicting
     invariants, for example an internal audit formatter and a customer GDPR
     export): **do not merge**. Record why, so nobody merges them later.
   - 0.65–0.85: extract the shared part only.
4. **Prove equivalence before merging.** Both artifacts' verification suites
   must pass against the merged artifact. For state machines and workflows,
   compare transitions on every reachable state, not a sample.
5. **Merge** with the stratum move above, update every caller, update
   `purpose-graph.yaml` (one artifact, union of `implements`), delete the
   duplicate, and run `pdd check`.
6. **Open one consolidation PR per cluster** with before/after, Φ scores,
   and the tests that prove equivalence.

## Scheduled consolidation

Run this skill on a schedule (weekly is typical) over the whole graph, a
stratum at a time, and open consolidation PRs for clusters above τ_merge. The
goal is to keep the refactoring-to-clone ratio above its historical baseline
(`pdd-governance-kpis`).
