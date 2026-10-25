# 5. Multi-modal closeness mapping and automated merging

To stop redundancy, PDD measures how "close" any two artifacts in the same
stratum are (two screens, two OpenAPI services, two workers, two methods) and
merges true duplicates into reusable abstractions. Pure bottom-up clone
detection fails both ways: coincidentally similar code may serve different
purposes, and Type-4 clones look different while implementing the same rule.

## 5.1 The unified closeness metric

**Φ(a_i, a_j) = α·Sim_struct(a_i, a_j) + β·Sim_sem(a_i, a_j) + γ·Sim_teleo(a_i, a_j)**,
α, β, γ ≥ 0, α + β + γ = 1, for a_i, a_j in the same stratum 𝒜_τ.

Let 𝒯(a) be the contract, intent, and purpose ancestors of a in the validated
trace graph, and Spec(u) = |Desc(u)|⁻¹ the TLR specificity of node u (a node
governing many artifacts discriminates little). Teleological closeness is the
specificity-weighted Jaccard similarity:

**Sim_teleo(a_i, a_j) = Σ_{u ∈ 𝒯(a_i) ∩ 𝒯(a_j)} Spec(u) / Σ_{v ∈ 𝒯(a_i) ∪ 𝒯(a_j)} Spec(v)**

Two consequences:

1. **Invisible Type-4 redundancy surfaces.** Two payment validators written
   with different syntax and libraries have low Sim_struct, but both implement
   the same contract and intent, so Sim_teleo → 1.0 and the pair is flagged.
2. **False merges are suppressed.** An internal audit-log formatter and a
   customer GDPR export may share an AST (Sim_struct ≈ 0.95), but they trace
   to disjoint purposes under conflicting invariants, so low Sim_teleo keeps Φ
   below the merge threshold and preserves domain isolation.

`python tools/pdd.py closeness A B --struct s --sem m` computes Sim_teleo from
the graph and combines it with the structural and semantic scores you supply.

## 5.2 Screens, design blocks, and UI elements

Semantic / visual (Sim_sem-UI):
- pixel MSE, **SSIM** for spatial layout, **CLIP score**
  cos(CLIP(img_i), CLIP(img_j));
- **Screen2Vec** embedding of the view hierarchy (component, text, layout
  encoders; no manual labels).

Structural (Sim_struct-UI), over the containment DOM tree:
- **TreeBLEU**(t, t_r) = |S(t) ∩ S(t_r)| / |S(t_r)|, where S is the set of
  height-1 subtrees;
- **Tree Edit Distance** TED(t₁, t₂) = min over edit paths of Σ c(e_m)
  (insert, delete, substitute);
- **Container Match**: mean bounding-box IoU of container nodes against
  canonical groupings.

Merge when Φ ≥ τ_UI, with **FrameKit-style adaptation**: treat the two DOM
trees as keyframes for context parameters (`userRole`, `viewportSize`,
`workflowStage`), take the minimal edit sequence from TED, find parallel
elements with the hierarchy embedding, hoist the shared subtree into one
canonical component, and turn the deltas into typed conditional props or
keyframe rules.

## 5.3 API endpoints and microservices

Bi-level pipeline (APIAide + whole-service OpenAPI vectorization):

- **Operation level.** For each OpenAPI operation, extract summary,
  description, operationId, path tokens, and request/response schemas;
  mean-pool transformer embeddings for the operation a and the governing
  intent p (d ∈ {512, 768, 1024}); Sim_API(p, a) = cos θ = p·a / (‖p‖‖a‖).
  Reported matches: "Get user purchase history" 0.89, "Retrieve product
  catalog" 0.94, "Filter products by category" 0.82.
- **Service level.** Extract domain phrases across each whole spec, embed them
  with the document vector, cluster services by responsibility overlap.

When two endpoints exceed Φ ≥ τ_API and share domain entities in the graph:
unify the routes, union the response fields behind optional projection
parameters, and deprecate the redundant route behind an API-gateway rewrite.

## 5.4 Classes, methods, and imports

- **Structure:** parse into ASTs and PDGs; TreeCen centrality vectors and
  gated BiLSTM sequence matching.
- **Semantics:** CodeBERT, StarEncoder, contrastive T-SimCSE embeddings.
- **Cost control:** DietCode input simplification (word dropout, frequency
  filtering, attention-based statement selection) cuts embedding compute about
  40% without accuracy loss.
- **Imports:** a cross-repository symbol and bytecode dependency graph
  (Negativa function detection, Calibro link-time outlining). If two packages
  serve the same intent (two JSON-schema validators, two date libraries),
  Sim_teleo = 1.0 triggers consolidation: rewrite call sites of the package
  with more bloat or more CVE gadgets to the canonical one, and drop it from
  the manifest.

## 5.5 State, background workers, and workflows

Lexical similarity matters little here; behaviour does. Model stores and
workflows as **labeled transition systems** and check equivalence with
SMT-based weakest-precondition analysis (Crystal and Casinghino), which proves
equivalent post-states for all valid inputs or isolates the divergence. When
two workers subscribe to overlapping events or mutate the same aggregate under
equivalent contracts, merge them into one consumer group with unified
partition-offset management, dead-letter isolation, and fixed-footprint
circuit breaking.

## 5.6 Summary

| Stratum | Structural metric | Semantic metric | Teleological grounding | Consolidation |
|---------|-------------------|-----------------|------------------------|---------------|
| Screens & design blocks | TreeBLEU, TED, Container Match | Screen2Vec, CLIP, SSIM | Shared contract / intent | FrameKit keyframes → one canonical component with typed props |
| Screen elements | Subtree isomorphism, CSS/prop schema overlap | Widget embeddings + label text | Shared parent screen or design-system contract | Hoist into parameterized design-system primitives |
| App & UI state | Transition-graph isomorphism, binding-path overlap | Identifier / slice embeddings (T-SimCSE) | Shared domain entity invariant | One normalized state machine with O(N) render bindings |
| APIs & microservices | JSON Schema tree match, verb alignment | APIAide pooled embeddings, whole-service vectors | Shared contract ReqPre/ReqPost | Unify routes with projection; deprecate behind gateway |
| Workers & workflows | CFG + SMT weakest-precondition equivalence | Trace and event-schema embeddings | Shared contract and obstacle resolution | One partitioned consumer group with shared DLQ and 480 B breakers |
| Classes & methods | TreeCen, BiLSTM | DietCode-filtered CodeBERT / StarEncoder / T-SimCSE | Ancestor overlap weighted by specificity | Extract injected interface; replace Type-4 clones with canonical calls |
| Imports | Call-graph reachability, Calibro outlining | Package docs and API-surface embeddings | Same Tier-3 intent | Rewrite to lowest-bloat, lowest-CVE package; purge the rest |

Procedure for agents: [pdd-closeness-mapping](../skills/pdd-closeness-mapping/SKILL.md).

Next: [6. Lifecycle mechanisms](06-lifecycle-mechanisms.md)
