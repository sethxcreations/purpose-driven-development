# 4. The Purpose-Driven Development paradigm

In PDD, source code, UI trees, state machines, and API specs are **ephemeral,
replaceable projections** of an authoritative, version-controlled
**Purpose-to-Artifact Property Graph (PAPG)**. No artifact may be created,
changed, or kept unless a directed lineage justifies it back to an explicit
purpose, under constitutional invariants.

## 4.1 The five-tier teleological taxonomy

```
Tier 1  Constitutional Invariants  𝒞   SEC-002, OPS-004, UI-001 …        constitution.yaml
          │ CONSTRAINS
Tier 2  Strategic Purposes         𝒫   the terminal WHY                   spec.md
          │ AND/OR/XOR_REFINES
Tier 3  Functional Intents         ℐ   technology-agnostic capabilities   spec.md
          │ OPERATIONALIZES
Tier 4  Operational Contracts  𝒪  +  Obstacles 𝒳                         plan.md
          │ IMPLEMENTS (upward)          ▲ OBSTRUCTS / RESOLVES
Tier 5  Full-Stack Artifacts       𝒜   ten strata                         tasks.md, code
```

- **Tier 1 — Constitutional Invariants (𝒞).** Each c ∈ 𝒞 is
  ⟨ID, CWE/Policy, Level, Constraint, Pattern, Rationale⟩, Level ∈
  {MUST, SHOULD, MAY} (RFC 2119). Examples: SEC-002 (CWE-89 parameterized SQL),
  OPS-004 (ring-buffer circuit breakers ≤ 480 B per destination), UI-001
  (strict one-way state-to-DOM binding).
  → [templates/constitution.yaml](../templates/constitution.yaml)
- **Tier 2 — Strategic Purposes (𝒫).** Business, domain, or user value that
  justifies the system; KAOS root goals / i\* actor goals.
- **Tier 3 — Functional Intents (ℐ).** The transition space between problem
  and solution: discrete, technology-agnostic capabilities and architecture
  responsibilities, organized in AND/OR/XOR refinement trees.
- **Tier 4 — Operational Contracts (𝒪) and Obstacles (𝒳).** Each leaf
  intent is operationalized into contracts assignable to agents, with DomPre,
  DomPost, ReqPre, ReqPost, ReqTrig, and attached obstacles (poison messages,
  third-party timeouts, invalid payloads) with mitigation links.
- **Tier 5 — Artifacts (𝒜)** across all ten strata:
  𝒜 = 𝒜_block ∪ 𝒜_screen ∪ 𝒜_elem ∪ 𝒜_state ∪ 𝒜_api ∪ 𝒜_worker ∪
  𝒜_workflow ∪ 𝒜_class ∪ 𝒜_method ∪ 𝒜_import.

## 4.2 Formal graph

𝒢_PAPG = (𝒱, ℰ, τ_V, τ_E, **X**)

- 𝒱 = 𝒞 ∪ 𝒫 ∪ ℐ ∪ 𝒪 ∪ 𝒳 ∪ 𝒜
- τ_V : 𝒱 → Σ_V assigns node types; τ_E : ℰ → Σ_E assigns edge types
- **X** ∈ ℝ^{|𝒱|×d} is the multimodal embedding matrix of all nodes

Edge vocabulary Σ_E, in three regimes:

| Regime | Edges | In `purpose-graph.yaml` |
|--------|-------|-------------------------|
| Downward elaboration ℰ_HOW | CONSTRAINS(c, o), AND_REFINES(p, i), OR_REFINES, XOR_REFINES, OPERATIONALIZES(i, o), OBSTRUCTS(x, o) | `constrained_by`, `refines` + `refinement`, `operationalizes`, `obstructs` |
| Upward justification ℰ_WHY | IMPLEMENTS(a, o), RESOLVES(o′, x), SATISFIES(i, p) | `implements`, `resolves`, `refines` read upward |
| Horizontal dependency ℰ_DEP | CONTAINS(screen, elem), BINDS_STATE(state, elem), INVOKES_API(method, api), TRIGGERS_WORKER(api, worker), ORCHESTRATES(workflow, worker), IMPORTS(class, import) | `depends_on: [{relation, target}]` |

Schema: [schemas/purpose-graph.schema.json](../schemas/purpose-graph.schema.json).

## 4.3 The three teleological laws

### Law 1 — Teleological Completeness (the zero-orphan invariant)

∀a ∈ 𝒜, ∃o ∈ 𝒪, ∃i ∈ ℐ, ∃p ∈ 𝒫 :
(a —IMPLEMENTS→ o) ∧ (i —OPERATIONALIZES→ o) ∧ (p —REFINES*→ i),
with o constrained by every applicable invariant and p active.

An artifact with no upward edge (deg⁺_WHY(a) = 0), or whose dependency closure
is unreachable from any active contract, is **teleological bloat**: orphan
widgets, zombie workers, dead methods, unused imports. It is removed.

*Enforced by:* `pdd check` (rules `zero-orphan`, `constitution-scope`),
[pdd-trace-gate](../skills/pdd-trace-gate/SKILL.md).

### Law 2 — Minimal Sufficiency

Let S_A(o) be the artifacts implementing contract o with verification suite
I_o. S_A(o) is minimal iff

(∀x ∈ I_o : Exec(S_A(o), x) ⊨ ReqPost(o)) ∧
(∀a_k ∈ S_A(o), ∃x′ ∈ I_o : Exec(S_A(o) \ {a_k}, x′) ⊭ ReqPost(o)).

If removing a_k preserves behaviour across all functional, robustness, and
security cases, a_k is structural bloat.

*Enforced by:* [pdd-debloat](../skills/pdd-debloat/SKILL.md) (needs execution,
so it is a procedure rather than a static check) and
[pdd-contract-coverage](../skills/pdd-contract-coverage/SKILL.md) (reverse
direction: code mapped to no clause).

### Law 3 — Obstacle-Grounded Centralization

An exception or environmental failure is a Tier-4 obstacle x obstructing o
({x, Dom} ⊨ ¬o). Its mitigation is defined **once** as a resolution contract
o_res with RESOLVES(o_res, x), implemented by **one** canonical mechanism (a
ring-buffer circuit-breaker middleware, a dead-letter partition router).
Downstream classes and methods may not write their own retries or fallbacks.

*Enforced by:* `pdd check` (rule `obstacle-centralized`), OPS-002, and
[pdd-resilience-harnesses](../skills/pdd-resilience-harnesses/SKILL.md).

## 4.4 How this repository represents the graph

- `constitution.yaml`: Tier 1.
- `purpose-graph.yaml`: Tiers 2–5 and all edges.
- In-code tags, for artifacts too fine-grained to list by hand:
  `# pdd: implements OC-PAY-AUTH stratum=method id=A-PAY-AUTHORIZE`.
- The embedding matrix **X** is optional: teams that have embeddings can
  compute Sim_sem with them; `pdd` itself computes only the teleological part.

Next: [5. Closeness mapping and merging](05-closeness-and-merging.md)
