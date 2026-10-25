# 2. Foundations: the genealogy of intent

"Purpose-driven development" has appeared before for local ideas (TDD for
documentation, hybrid loss functions in medical imaging, additive
manufacturing design, socio-ecological digital twins). PDD as defined here is
a full-stack paradigm for governing AI agents in Software Engineering 3.0, and
it synthesizes five research lines.

## 2.1 Goal-Oriented Requirements Engineering (KAOS, i*)

- **i\*** (Yu, Mylopoulos) models intentional actors with goals, beliefs,
  abilities, and commitments, using Strategic Rationale graphs for means–end
  decomposition and dependencies.
- **KAOS** (van Lamsweerde, Letier) is a multi-layer metamodel: **Goals**
  (Requirement, Expectation, DomainProperty, SoftGoal), **Objects** (Agents,
  Entities), **Operations**, and **Obstacles**. Goals are refined into DAGs by
  AND-refinement, OR-refinement, and XOR-reduction, asking **WHY?** to find
  parents and **HOW?** to find children until leaves are assignable to one
  agent.
- **Operationalization** links terminal requirements to operations with
  domain pre/post-conditions (DomPre, DomPost) and required conditions
  (ReqPre, ReqPost, ReqTrig).
- **Minimal reduction:** subgoal set S minimally reduces g if S suffices for g
  and removing any element makes it insufficient.
- **Obstacle analysis:** O obstructs G if {O, Dom} ⊭ false yet {O, Dom} ⊨ ¬G;
  linked by ObstructionLink, mitigated by a new requirement via SolutionLink.
  2026 work applies this to ML alignment failures.
- Model-driven tooling (MDGore with ATL transformations between i\* and KAOS;
  mind-map elicitation) eased modeling, but GORE stayed in early-stage
  documents and lost contact with code once implementation began.

**PDD takes:** the WHY/HOW refinement tree, operationalization, minimal
reduction, and obstacles, and keeps the goal graph live at build time and
runtime instead of in a requirements document.
→ [pdd-purpose-modeling](../skills/pdd-purpose-modeling/SKILL.md),
[pdd-operational-contracts](../skills/pdd-operational-contracts/SKILL.md)

## 2.2 Traceability Link Recovery (TLR) and the transition space

Linking natural-language requirements directly to code fails from vocabulary
mismatch and granularity gaps. The fix is an intermediate **transition space**
of capabilities or Software Architecture Models (SAM): link A→C and B→C and A
and B are transitively linked.

- Classical IR: VSM with TF-IDF and cosine similarity, LSI, LDA, Bayesian
  (COMET); enriched with biterms (TAROT), semantic graphs and spreading
  activation (GeT2Trace, FTLR).
- Learned: contrastive embeddings (T-SimCSE, with a **Specificity** measure
  penalizing artifacts that link to many requirements), LLM ensembles
  (NLTrace, TraceLLM).
- Architecture-level: ARDoCo, LiSSA, TransArC use LLM prompts to extract
  components from architecture docs and code as intermediate SAMs, reaching
  weighted F1 0.86–0.87.
- **TraceRank** (2026) combines retrieval, semantic-structural, dependency,
  and hypergraph evidence into a **Validated Trace Responsibility Graph
  (VTRG)**: LinkRecall@30 from 80.6% cold-start to 92.8% with partial
  validation.
- North et al.: gradients between generated code tokens and requirement
  sentences expose overlooked clauses and drive prompt reformulation.

**PDD takes:** Functional Intents *are* the transition space; Specificity
weights teleological closeness; the CI trace gate and the coverage check come
from TransArC/VTRG and North et al.
→ [pdd-trace-gate](../skills/pdd-trace-gate/SKILL.md),
[pdd-contract-coverage](../skills/pdd-contract-coverage/SKILL.md)

## 2.3 Software debloating and program reduction

Driven by attack-surface reduction (for example the US Navy's TPCP program).

- **Type I bloat:** unneeded shared-library and transitive dependency code.
  **Type II bloat:** unneeded features and dead paths. Debloaters work
  source-to-source, binary-to-binary, on shared libraries, or at runtime.
- Input-based debloating: given p and inputs I, produce p′ with p(i) = p′(i)
  for all i ∈ I, trading reduction against **c-generality** (correctness) and
  **r-generality** (robustness) on unseen inputs.
- Tools: Chisel (MDP + delta debugging), Debop, Trimmer (constant
  propagation), Razor (binary rewriting), Cov/CovA (coverage pruning),
  Negativa (shared libraries), Cozart (kernel config), DeView (record-and-replay
  for PWAs: blocks 91.8% of unneeded web APIs, neutralizing 76.3% of exploits).
- Flaw: minimizers can delete null checks and bounds validators. **LEADER**
  (2025/26) makes a coverage debloater and a static analyzer advisors to an
  LLM decision-maker that preserves security checks.

**PDD takes:** the Law of Minimal Sufficiency, the multi-advisor arbiter, and
surface reduction for APIs and UIs.
→ [pdd-debloat](../skills/pdd-debloat/SKILL.md)

## 2.4 Semantic clone detection and multi-modal similarity

- Clone types: **Type-1** exact, **Type-2** renamed, **Type-3** near-miss,
  **Type-4** syntactically different but semantically identical. AI mostly
  produces Type-4.
- Code: ASTs, CFGs, PDGs with graph centrality (TreeCen) or gated BiLSTMs.
- UI: Screen2Vec embeds screens from text, component types, and layout;
  DesignCoder, ProtoVLM, FrameKit measure TreeBLEU, DOM tree edit distance,
  and Container Match (IoU).
- APIs: APIAide and OpenAPI clustering embed operation descriptions and
  schemas to find functional equivalence across services.

**PDD takes:** stratum-specific structural and semantic similarity, fused with
teleology. → [pdd-closeness-mapping](../skills/pdd-closeness-mapping/SKILL.md)

## 2.5 Constitutional Spec-Driven Development and the incompleteness proof

- Adapting Constitutional AI to engineering: a versioned **Software
  Constitution** of principles mapped to CWEs with RFC 2119 levels constrains a
  cascade **spec.md → plan.md → tasks.md**, with a file-and-line Compliance
  Traceability Matrix. Reported: −73% vulnerabilities, 56% faster time to first
  secure build, 4.3× compliance documentation coverage.
- **Vassilev (NIST, 2026, IEEE S&P)**, building on Gödel and Chaitin, models a
  guardrail as a finite checker over an unbounded input domain. **Theorem 2:**
  some behavioral constraint will be enforced incorrectly on some adversarial
  or out-of-distribution input. **Theorem 3:** finite context windows tighten
  this further.
- Implication: static prompt guardrails and markdown specs alone are
  mathematically incomplete. You need an external, deterministic
  purpose-to-artifact graph plus continuous structural verification and
  runtime action enforcement.

**PDD takes:** the constitution and the cascade, and adds the graph, CI
verification, and runtime guardrails that the proof says are needed.
→ [pdd-constitution](../skills/pdd-constitution/SKILL.md),
[pdd-spec-cascade](../skills/pdd-spec-cascade/SKILL.md),
[pdd-runtime-guardrails](../skills/pdd-runtime-guardrails/SKILL.md)

## Summary table

| Paradigm | Representative work | Mechanism | Strength | Failure mode in the agentic era |
|----------|--------------------|-----------|----------|---------------------------------|
| GORE | KAOS, i\*, MDGore | Goal refinement, obstacles, operationalization | Formal WHY/HOW, minimal reduction, design-time exceptions | Static, early-stage; links lost once AI coding starts |
| TLR | T-SimCSE, TransArC, ARDoCo, LiSSA, TraceRank | Contrastive embeddings, intermediate SAMs, VTRG | Bridges problem and solution (92.8% recall, 0.87 F1) | Retrospective; text-to-class only; ignores DOM, state, workers, imports |
| Debloating | Trimmer, Chisel, Razor, DeView, Negativa, LEADER | Coverage, constant propagation, binary rewriting, LLM advisors | Up to 91.8% unused web APIs removed; 44–74% overhead cuts | Post-hoc; no purpose awareness; may delete security checks unless advised |
| Clone & UI similarity | TreeCen, BiLSTM, Screen2Vec, DesignCoder, APIAide | AST/PDG centrality, embeddings, TreeBLEU, TED, cosine | Finds Type-4 clones, redundant UI and REST ops | No intent grounding; cannot tell intentional separation from accidental duplication |
| Constitutional SDD | Constitutional AI; spec/plan/tasks cascade | RFC 2119 constitutions with CWE mappings | −73% vulnerabilities; 56% faster secure build | Incomplete under finite context (Vassilev) without graph enforcement |

Next: [3. Anatomy of full-stack entropy](03-full-stack-entropy.md)
