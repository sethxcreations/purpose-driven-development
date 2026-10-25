# Glossary

**Ateleological process** — Piecemeal, local adaptation pursuing immediate
functional survival without global coherence. Unguided AI code generation is
one, accelerated.

**Teleological process** — Purpose-driven, top-down, architecturally bounded
development.

**Teleology** — The hierarchy of purposes, constraints, and invariants that
explains why a system and each of its parts exist.

**PAPG (Purpose-to-Artifact Property Graph)** — 𝒢 = (𝒱, ℰ, τ_V, τ_E, X): the
authoritative, versioned graph from constitution to artifacts.
`purpose-graph.yaml` plus `constitution.yaml`.

**Constitutional Invariant (Tier 1)** — ⟨ID, CWE/Policy, Level, Constraint,
Pattern, Rationale⟩ with Level ∈ {MUST, SHOULD, MAY}.

**Strategic Purpose (Tier 2)** — The terminal WHY: business, domain, or user
value. Active or retired.

**Functional Intent (Tier 3)** — Technology-agnostic capability in the
transition space between problem and solution; refined by AND/OR/XOR.

**Operational Contract (Tier 4)** — Precise, agent-assignable operation with
DomPre, DomPost, ReqPre, ReqPost, ReqTrig.

**Obstacle (Tier 4)** — Condition consistent with the domain that entails a
contract's violation ({O, Dom} ⊭ false, {O, Dom} ⊨ ¬G).

**Resolution Contract** — The single contract that RESOLVES an obstacle,
implemented by one canonical mechanism.

**Artifact (Tier 5)** — A concrete entity in one of ten strata: block, screen,
elem, state, api, worker, workflow, class, method, import.

**AND / OR / XOR refinement** — All children needed / any child suffices /
exactly one child chosen.

**DomPre, DomPost** — Domain conditions before and after an operation.
**ReqPre, ReqPost, ReqTrig** — Strengthened conditions the software must check
before, guarantee after, and the trigger obliging the operation.

**Minimal reduction** — A subgoal set that suffices for its parent, where
removing any element makes it insufficient.

**Teleological bloat** — An artifact with no valid upward path to an active
purpose (an orphan).

**Structural bloat** — An artifact whose removal preserves all verified
behaviour of its contract (violates Minimal Sufficiency).

**Type I / Type II bloat** — Unneeded dependency or library code / unneeded
application features and paths.

**Clone types** — Type-1 exact; Type-2 renamed identifiers; Type-3 near-miss
edits; Type-4 syntactically different, semantically identical.

**Φ (closeness)** — α·Sim_struct + β·Sim_sem + γ·Sim_teleo, within one stratum.

**Sim_teleo** — Specificity-weighted Jaccard similarity of two artifacts'
governing ancestors.

**Specificity** — Spec(u) = 1 / |Desc(u)|; a node governing many artifacts is
less discriminative.

**τ_reuse, τ_extend, τ_merge** — Decision thresholds; defaults 0.85, 0.65, 0.85.

**Transition space** — Intermediate abstractions (capabilities, architecture
components) that make requirement-to-code tracing possible.

**VTRG (Validated Trace Responsibility Graph)** — TraceRank's combination of
retrieval, semantic-structural, dependency, and hypergraph evidence with
partially validated traces.

**c-generality / r-generality** — Whether a reduced program stays correct /
robust on inputs outside the reduction's input set.

**Comprehension debt** — The gap between how fast code is generated and how
fast humans can understand it (Addy Osmani).

**Goodhart's Revenge / reward hacking** — Optimizing a proxy (passing tests)
at the expense of the real objective.

**Vassilev incompleteness** — A finite guardrail checker cannot correctly
enforce all constraints over an unbounded input space (Theorem 2), and finite
context windows tighten the limit (Theorem 3).

**Six-layer runtime guardrails** — Input, retrieval, planning, inference,
action, and output/continuous enforcement around deployed agents.

**Constitutional harness** — A pre-verified, canonical implementation agents
must bind to (circuit breaker, partition consumer) instead of writing their own.

**Teleological Governance KPIs** — Teleological Coverage, Refactoring-to-Clone
Ratio, Attack Surface Reduction, AI Debt Survival Rate.
