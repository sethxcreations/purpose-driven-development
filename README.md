# Purpose-Driven Development

**A teleological architecture for keeping AI-built software minimal, traceable, and resilient.**

AI agents made writing code nearly free, yet delivery stability and
maintainability are falling: duplicated code up 8×, refactoring down 40%,
review time up 441%, and about a quarter of AI-introduced debt never leaves
the codebase. The cause is structural. Models generate locally plausible code
while blind to *why* the system exists.

**Purpose-Driven Development (PDD)** makes purpose the primary artifact of
software engineering. Every screen, state slice, endpoint, worker, class,
method, and dependency must trace through an explicit graph to a live business
purpose, under a versioned software constitution. Anything that does not is
bloat and is removed. Anything that duplicates an existing purpose is reused
or merged. Every failure mode is handled once, canonically.

This repository packages PDD as:

- **15 agent skills** (`skills/*/SKILL.md`) that any coding agent or human can follow;
- **templates** for the constitution, the purpose graph, and the spec cascade;
- **`pdd`**, a small checker that enforces the teleological laws in CI;
- **constitutional harnesses**: a 480-byte ring-buffer circuit breaker and a
  partition-resilient consumer, with tests;
- **docs** covering every section of the whitepaper, and a worked example.

## The model

```
Tier 1  Constitutional Invariants   MUST / SHOULD / MAY (RFC 2119), mapped to CWEs     constitution.yaml
   │ CONSTRAINS
Tier 2  Strategic Purposes          the terminal WHY                                   ┐
   │ AND / OR / XOR refines                                                            │
Tier 3  Functional Intents          technology-agnostic capabilities                   │ purpose-graph.yaml
   │ OPERATIONALIZES                                                                   │ spec.md · plan.md · tasks.md
Tier 4  Operational Contracts       DomPre/Post, ReqPre/Post/Trig   + Obstacles ──► Resolution contracts
   ▲ IMPLEMENTS                                                                        │
Tier 5  Artifacts in 10 strata      block · screen · elem · state · api · worker ·     ┘ code tagged
                                    workflow · class · method · import                   `pdd: implements OC-…`
```

**Three laws**

1. **Teleological Completeness** — every artifact traces upward to an active purpose. Zero orphans.
2. **Minimal Sufficiency** — every artifact implementing a contract is necessary; removable ones are bloat.
3. **Obstacle-Grounded Centralization** — each failure mode is mitigated once, by one canonical mechanism.

**Closeness** — Φ = α·structural + β·semantic + γ·teleological similarity.
Before creating anything: Φ ≥ 0.85 reuse, 0.65–0.85 extend, otherwise create.

## Quick start

```bash
pip install pyyaml

# Check the worked example against the three laws
python tools/pdd.py check --graph examples/checkout/purpose-graph.yaml \
    --scan examples/checkout/src --require-tags --specs examples/checkout/specs

# Why does this code exist?
python tools/pdd.py lens --graph examples/checkout/purpose-graph.yaml \
    --scan examples/checkout/src src/payments/authorize.py

# Catch reward hacking in a diff (removed auth check, skipped test, constant return)
python tools/pdd.py guard examples/checkout/reward-hack.diff

# Governance KPIs
python tools/pdd.py kpi --graph examples/checkout/purpose-graph.yaml --scan examples/checkout/src
```

Adopting it in your project: [docs/07-adoption-guide.md](docs/07-adoption-guide.md).

### Install the skills

- **Claude Code:** `/plugin marketplace add <owner>/purpose-driven-development`, then
  `/plugin install purpose-driven-development`. Or copy `skills/*` into your project's `.claude/skills/`.
- **Any other agent:** copy `skills/` and point the agent at [AGENTS.md](AGENTS.md).

## Skills

| Skill | Use it when |
|-------|-------------|
| [using-pdd](skills/using-pdd/SKILL.md) | Starting any task; routes to the right skill |
| [pdd-constitution](skills/pdd-constitution/SKILL.md) | Writing or amending `constitution.yaml` |
| [pdd-purpose-modeling](skills/pdd-purpose-modeling/SKILL.md) | Eliciting purposes and AND/OR/XOR intent trees (WHY/HOW) |
| [pdd-operational-contracts](skills/pdd-operational-contracts/SKILL.md) | Contracts, obstacle analysis, resolution contracts |
| [pdd-spec-cascade](skills/pdd-spec-cascade/SKILL.md) | Requirement → spec.md → plan.md → tasks.md, sealed |
| [pdd-reuse-gate](skills/pdd-reuse-gate/SKILL.md) | **Before creating anything new** |
| [pdd-contract-coverage](skills/pdd-contract-coverage/SKILL.md) | Before commit: every clause covered, nothing extra |
| [pdd-trace-gate](skills/pdd-trace-gate/SKILL.md) | Reviewing PRs; CI setup; reward-hacking checks |
| [pdd-closeness-mapping](skills/pdd-closeness-mapping/SKILL.md) | Finding and merging duplicates in any stratum |
| [pdd-debloat](skills/pdd-debloat/SKILL.md) | Removing dead code, endpoints, dependencies safely |
| [pdd-full-stack-audit](skills/pdd-full-stack-audit/SKILL.md) | Assessing an existing codebase across ten strata |
| [pdd-resilience-harnesses](skills/pdd-resilience-harnesses/SKILL.md) | Retries, breakers, consumers: bind, don't write |
| [pdd-runtime-guardrails](skills/pdd-runtime-guardrails/SKILL.md) | Six-layer guardrails for agents and MCP tools |
| [pdd-teleological-lens](skills/pdd-teleological-lens/SKILL.md) | Explaining why code exists; lens-based review |
| [pdd-governance-kpis](skills/pdd-governance-kpis/SKILL.md) | Replacing volume metrics with the four PDD KPIs |

## Whitepaper coverage

| Whitepaper section | Docs | Skills, tools, templates |
|--------------------|------|--------------------------|
| Executive abstract: the crisis, three failure mechanisms, six-month wall | [01](docs/01-the-crisis.md) | `using-pdd` |
| Genealogy: GORE (KAOS, i\*) | [02 §2.1](docs/02-foundations.md#21-goal-oriented-requirements-engineering-kaos-i) | `pdd-purpose-modeling`, `pdd-operational-contracts` |
| Genealogy: Traceability link recovery, transition space | [02 §2.2](docs/02-foundations.md#22-traceability-link-recovery-tlr-and-the-transition-space) | `pdd-trace-gate`, `pdd-contract-coverage`, `pdd check` |
| Genealogy: Software debloating | [02 §2.3](docs/02-foundations.md#23-software-debloating-and-program-reduction) | `pdd-debloat` |
| Genealogy: Semantic clone and UI similarity | [02 §2.4](docs/02-foundations.md#24-semantic-clone-detection-and-multi-modal-similarity) | `pdd-closeness-mapping` |
| Genealogy: Constitutional SDD, Vassilev incompleteness | [02 §2.5](docs/02-foundations.md#25-constitutional-spec-driven-development-and-the-incompleteness-proof) | `pdd-constitution`, `pdd-spec-cascade`, `pdd-runtime-guardrails` |
| Anatomy of full-stack bloat across ten strata | [03](docs/03-full-stack-entropy.md) | `pdd-full-stack-audit` |
| Five-tier taxonomy, formal PAPG, three laws | [04](docs/04-paradigm.md) | templates, schemas, `pdd check` |
| Closeness Φ, Sim_teleo, per-stratum merging | [05](docs/05-closeness-and-merging.md) | `pdd-closeness-mapping`, `pdd closeness`, `pdd lens` |
| Proactive: cascade, Intent-RAG gate, prompt reformulation | [06 §6.1](docs/06-lifecycle-mechanisms.md#61-proactive-pre-generation-synthesis-control) | `pdd-spec-cascade`, `pdd-reuse-gate`, `pdd-contract-coverage`, `pdd seal` |
| Reactive: TLR gate, multi-advisor debloating, consolidation | [06 §6.2](docs/06-lifecycle-mechanisms.md#62-reactive-cicd-verification-and-debloating) | `pdd-trace-gate`, `pdd-debloat`, `pdd guard`, `templates/pdd-ci.yml` |
| Practical: lenses, six-layer guardrails, harnesses, KPIs | [06 §6.3](docs/06-lifecycle-mechanisms.md#63-practical-ide-ergonomics-runtime-guardrails-telemetry) | `pdd-teleological-lens`, `pdd-runtime-guardrails`, `pdd-resilience-harnesses`, `pdd-governance-kpis`, `harnesses/` |
| Conclusions | below | — |

What maps to research tooling and what this repo implements directly:
[docs/08-tooling-map.md](docs/08-tooling-map.md).

## Repository layout

```
skills/            15 SKILL.md agent skills
docs/              whitepaper, section by section; adoption guide; tooling map; glossary; references
templates/         constitution.yaml, purpose-graph.yaml, spec/plan/tasks.md, PR template, CI workflow
schemas/           JSON Schemas for the constitution and the purpose graph
tools/pdd.py       checker: check · lens · closeness · kpi · guard · seal
harnesses/python/  ring-buffer circuit breaker (480 B/destination) and partition-resilient consumer
examples/checkout/ worked example: graph, tagged source, sealed spec cascade, reward-hack diff
purpose-graph.yaml this repository's own purpose graph (PDD applied to PDD)
```

## Conclusion

Speeding up syntax without formalizing intent does not speed up delivery; it
speeds up entropy. Static rules and finite context windows cannot close the
gap on their own. PDD makes the mapping from constitution to purpose to intent
to contract to artifact explicit, typed, and checked, so code becomes a
governed, self-cleaning projection of human intent rather than an opaque
liability, and teams keep the speed of AI agents without paying for it in
bloat, duplication, and fragility.

## License

MIT. See [LICENSE](LICENSE). Figures quoted in the docs are as reported in the
whitepaper; sources are in [docs/references.md](docs/references.md).
