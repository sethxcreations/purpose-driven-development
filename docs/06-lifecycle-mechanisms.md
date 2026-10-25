# 6. Proactive, reactive, and practical mechanisms

A paradigm only works if it fits existing workflows without worsening the
review bottleneck. PDD runs as defense in depth across the lifecycle.

```
 PROACTIVE (before generation)        REACTIVE (CI/CD)                 PRACTICAL (IDE + runtime)
 ─────────────────────────────        ────────────────                 ─────────────────────────
 constitution.yaml                    Trace gate (orphans,             Teleological lens
   → spec.md → plan.md → tasks.md       reward hacking, seals)         Six-layer runtime guardrails
 Reuse gate  (Φ ≥ 0.85 reuse,         Multi-advisor debloating         Constitutional harnesses
              0.65–0.85 extend)       Scheduled clone consolidation    Governance KPIs
 Contract coverage check
```

## 6.1 Proactive: pre-generation synthesis control

**Constitutional spec cascade.** Every repository keeps a machine-readable
`constitution.yaml` (RFC 2119 + CWE). A planning agent or architect elaborates
each requirement through the KAOS refinement graph into `spec.md` (intents),
`plan.md` (contracts and obstacle mitigations), and `tasks.md` (atomic work).
Because these files steer agents, they are authored defensively and
checksum-validated so indirect prompt injection cannot subvert them.
→ [pdd-spec-cascade](../skills/pdd-spec-cascade/SKILL.md), `pdd seal`

**Pre-Synthesis Closeness Gate (Intent-to-Artifact RAG).** Before an agent
executes a task, a planning guardrail embeds the target intent and contract
into a query vector p and searches all ten strata for
ã = argmax_{a ∈ 𝒜} Φ(p, a).
- Φ ≥ **0.85** (hard reuse): block new files and functions, inject ã's
  signature into context, force the agent to import or call it.
- **0.65** ≤ Φ < 0.85 (parametric extension): refactor ã through interface
  parameterization or keyframe extension instead of cloning it.
→ [pdd-reuse-gate](../skills/pdd-reuse-gate/SKILL.md)

**Gradient-guided prompt reformulation.** During generation, gradient
attribution between code tokens and contract clauses (North et al.) detects
overlooked clauses (RBAC checks, retry limits, telemetry) and rewrites the
prompt until the contract is fully covered before commit. Agents without
gradient access do the attribution explicitly, clause by clause.
→ [pdd-contract-coverage](../skills/pdd-contract-coverage/SKILL.md)

## 6.2 Reactive: CI/CD verification and debloating

**Automated TLR gate.** Every PR passes a gate combining TransArC
(intermediate architecture components extracted from code and docs; 0.86–0.87
weighted F1) and TraceRank's VTRG (92.8% recall with partial validated traces).
Every added or modified AST node, DOM container, state hook, and API route must
establish an IMPLEMENTS link to its contract in `tasks.md`. Orphans fail the
build, as do test changes with reward-hacking signatures such as hardcoded
return constants.
→ [pdd-trace-gate](../skills/pdd-trace-gate/SKILL.md), `pdd check`, `pdd guard`,
[templates/pdd-ci.yml](../templates/pdd-ci.yml)

**Multi-advisor debloating** on every release branch, to remove the 24.2% of
AI debt that otherwise survives:
- backend and libraries: Trimmer constant propagation and Cov (llvm-cov, gcov)
  find unexercised paths; Negativa finds unused library functions;
- the LEADER arbiter: coverage and static-vulnerability advisors propose
  pruning diffs to an LLM arbiter bound by the constitution, so null checks,
  bounds validators, and obstacle handlers survive;
- reductions are verified by SMT weakest-precondition equivalence for c- and
  r-generality. Reported gains: up to −74.6% peak host memory, −69.6% GPU
  memory, 44.6% faster execution, 20–87% fewer exploitable gadgets;
- frontend and PWAs: DeView record-and-replay over end-to-end journeys strips
  unused browser and REST bindings (up to 91.8% of reachable API surface,
  preventing 76.3% of known exploits); DesignCoder refinement collapses
  redundant DOM wrappers.
→ [pdd-debloat](../skills/pdd-debloat/SKILL.md)

**Asynchronous clone consolidation.** Off-peak agents scan the graph's
embedding space; when a cluster of methods, screens, or endpoints drifts above
Φ ≥ τ_merge they open a consolidation PR, pushing the refactoring-to-clone
ratio back above the 21% baseline.
→ [pdd-closeness-mapping](../skills/pdd-closeness-mapping/SKILL.md) (scheduled)

## 6.3 Practical: IDE ergonomics, runtime guardrails, telemetry

**In-IDE teleological lenses.** Humans act as the final arbiters of agent
output. Hovering any class, method, UI element, or worker shows its WHY
lineage (contract → intent → purpose), governing invariants, and nearest
semantic neighbours (ARDoCo REST API, TraceView, TraceViz). In-IDE trace
visualization measurably speeds comprehension during maintenance.
→ [pdd-teleological-lens](../skills/pdd-teleological-lens/SKILL.md), `pdd lens`

**Six-layer runtime guardrails.** Because no build-time guardrail or finite
context can guarantee safety over an infinite input space (Vassilev Theorems
2–3), every deployed agent and service is wrapped by: input and retrieval
guardrails (authentication, injection detection, RBAC-filtered RAG); planning
and inference guardrails (audit goal decomposition and intermediate steps);
**action guardrails** between tool-call output and execution across APIs,
databases, and MCP servers (tool on the active contract's allowlist, arguments
satisfy schema and constitution); and output and continuous guardrails
(sensitive-data scanning, OpenTelemetry decision traces, drift detection).
→ [pdd-runtime-guardrails](../skills/pdd-runtime-guardrails/SKILL.md)

**Constitutional infrastructure templates.** Pre-verified, immutable harnesses
agents must bind to:
- ring-buffer circuit breaker: 60 one-second buckets per destination, two
  4-byte counters each, **480 B per destination**, ~25 MB for 40,000
  destinations regardless of retry-storm velocity, **20-attempt** minimum
  sample floor;
- partition-resilient consumer: verifies transactional-outbox relay state,
  monitors per-partition lag, routes poison events to a dead-letter store and
  advances offsets to prevent head-of-line blocking.
→ [pdd-resilience-harnesses](../skills/pdd-resilience-harnesses/SKILL.md),
[harnesses/python/](../harnesses/python/)

**Teleological governance KPIs** replace volume metrics (commits, lines added)
that reward debt: Teleological Coverage (CompleteRate@30, LinkRecall@30),
Refactoring-to-Clone Ratio, Attack Surface Reduction, AI Debt Survival Rate
(target well below 24.2%).
→ [pdd-governance-kpis](../skills/pdd-governance-kpis/SKILL.md), `pdd kpi`

## 6.4 Summary

| Regime | Mechanism | Lifecycle stage | Core implementation | Reported impact |
|--------|-----------|-----------------|---------------------|-----------------|
| Proactive | Constitutional spec cascade | Requirements and architecture planning | `constitution.yaml` → spec → plan → tasks | −73% vulnerabilities; 56% faster first secure build; 4.3× compliance coverage |
| Proactive | Intent-to-Artifact RAG gate | Task planning and synthesis | Planning guardrail queries graph embeddings (Φ ≥ τ_reuse) | Stops Type-4 clones, duplicate endpoints, cloned screens at inception |
| Proactive | Gradient prompt reformulation | Token generation | Token-to-requirement gradients | Removes omitted constraints (telemetry, RBAC, retry bounds) before commit |
| Reactive | TransArC + VTRG trace gate | PR verification | SAM extraction + validated trace graph | 92.8% LinkRecall@30, 0.86–0.87 F1; blocks orphans and reward-hacked tests |
| Reactive | Multi-advisor debloating | Release build | LEADER + Cov/Trimmer + DeView + DesignCoder | −91.8% unused web APIs, −74.6% RAM, −44.6% runtime, −87% ROP gadgets |
| Practical | In-IDE lenses | Review and maintenance | ARDoCo REST API + TraceViz / TraceView | Lowers comprehension debt and review load |
| Practical | Runtime action guardrails & harnesses | Production and agent tool calls | Six-layer interception + 480 B breakers + DLQ isolation | Mitigates incompleteness gaps; bounds memory; prevents partition stalls |

Next: [7. Adoption guide](07-adoption-guide.md)
