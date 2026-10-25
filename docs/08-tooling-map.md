# 8. Tooling map: whitepaper mechanisms to what this repository provides

The whitepaper describes PDD with research systems (TraceRank, LEADER, DeView,
FrameKit, …), several of which have no off-the-shelf distribution. This
repository gives a working, dependency-light implementation of the parts that
can be checked deterministically, skills that let an agent perform the rest
with judgement, and pointers to production tools you can plug in.

| Whitepaper mechanism | In this repository | Plug-in options for higher fidelity |
|----------------------|--------------------|-------------------------------------|
| Software Constitution (RFC 2119 + CWE) | `templates/constitution.yaml`, schema, `pattern.forbid` checks in `pdd check` | Semgrep, CodeQL, ESLint/Ruff custom rules generated from invariants |
| Spec cascade spec → plan → tasks + compliance matrix | `templates/spec.md`, `plan.md`, `tasks.md`; `pdd-spec-cascade` | Any spec-driven toolkit that emits the same three files |
| Checksum-validated specs | `pdd seal` / `pdd check --specs` | Signed commits, CODEOWNERS on `specs/` |
| PAPG (tiers, edges) | `purpose-graph.yaml`, `schemas/purpose-graph.schema.json`, in-code `pdd:` tags | Store in a graph database for large estates |
| Law 1 zero-orphan | `pdd check` rules `zero-orphan`, `constitution-scope` | — |
| Law 2 minimal sufficiency | `pdd-debloat`, `pdd-contract-coverage` (procedures) | Mutation testing (mutmut, Stryker, PIT) to test removability |
| Law 3 obstacle centralization | `pdd check` rule `obstacle-centralized`; OPS-002 pattern | — |
| Sim_teleo with specificity | `pdd closeness`, `pdd lens` (exact implementation of the formula) | — |
| Sim_struct / Sim_sem | Agent estimation in `pdd-closeness-mapping` | jscpd, PMD CPD, SonarQube; tree-sitter AST diff; code embeddings (CodeBERT-class models, any embeddings API); Playwright screenshots + SSIM/CLIP for screens; OpenAPI diff tools |
| Intent-to-Artifact RAG gate (0.85 / 0.65) | `pdd-reuse-gate` | Embedding index over the repo + graph; agent pre-tool hooks that block file creation |
| Gradient-guided prompt reformulation | `pdd-contract-coverage` (explicit clause attribution) | Model-internal attribution where available |
| TransArC + VTRG trace gate | `pdd check` + `pdd-trace-gate` review procedure + `templates/pdd-ci.yml` | LLM-based trace recovery over architecture docs |
| Reward-hacking detection | `pdd guard` | Mutation testing on changed tests; test-change CODEOWNERS |
| LEADER multi-advisor debloating | `pdd-debloat` (advisors + arbiter procedure) | coverage.py, c8/istanbul, llvm-cov, JaCoCo; knip, ts-prune, vulture, depcheck; Semgrep/CodeQL as the security advisor |
| DeView API-surface reduction | `pdd-debloat` surface advisor | Gateway logs, Playwright journey recordings |
| DesignCoder DOM refinement, FrameKit merge | `pdd-closeness-mapping` UI moves | Storybook + visual regression for equivalence |
| SMT weakest-precondition equivalence | Equivalence-by-suite in `pdd-closeness-mapping` | Model checkers / SMT (Z3) for critical state machines |
| Teleological lens (ARDoCo, TraceViz) | `pdd lens`; `pdd-teleological-lens` | Editor extension calling `pdd lens` |
| Six-layer runtime guardrails | `pdd-runtime-guardrails` incl. action-guardrail middleware sketch | Policy engines (OPA), MCP gateways, OpenTelemetry |
| Ring-buffer circuit breaker (480 B, 20 floor) | `harnesses/python/circuit_breaker.py` + tests | Port to your language with the same tests |
| Partition-resilient consumer | `harnesses/python/partition_consumer.py` + tests | Broker-specific DLQ features; transactional outbox |
| Governance KPIs | `pdd kpi` (coverage), `pdd-governance-kpis` (all four) | Git analytics, SAST history, dependency scanners |

## What `pdd` deliberately does not do

- It does not embed code or screens. Semantic similarity needs a model; bring
  your own and pass the score to `pdd closeness`.
- It does not execute tests. Minimal sufficiency and equivalence are proven by
  your test runner, following the skills.
- It does not prove a tag is truthful. Reviewers (human or agent) do, with the
  trace-gate procedure.

Back to [README](../README.md)
