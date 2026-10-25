---
name: pdd-full-stack-audit
description: Audit an existing codebase across all ten artifact strata (design blocks, screens, screen elements, state, APIs, workers, workflows, classes, methods, imports) for bloat, redundancy, and rigidity, and produce a prioritized PDD adoption plan. Use when onboarding PDD to a legacy or AI-heavy codebase, or for a periodic architecture health check.
---

# Full-stack entropy audit

AI-era entropy shows up in every layer at once. Audit all ten strata, record
findings in one table, and turn them into graph work and cleanup PRs.

## What to look for

| Stratum | Bloat / redundancy signature | Rigidity consequence |
|---------|------------------------------|----------------------|
| **Design blocks / modules** | Parallel feature modules re-implementing validation and layout; bounded contexts ignored | Cross-cutting changes need N edits |
| **Screens** | `*V2`, `*Copy` screens; per-role or per-viewport copies; high visual similarity, diverging DOM | Every UI change multiplied |
| **Screen elements** | Wrapper divs that group nothing; inline styles over tokens; one-off buttons and inputs lacking accessibility and telemetry | Broken responsiveness, inaccessible UI |
| **App / UI state** | Boolean flags mirroring other state; the same server data cached in two stores; effects that set state during render | Re-render loops, impossible states (most high-impact web defects are state/DOM bugs) |
| **APIs** | An endpoint per screen; near-identical payloads across routes; routes without RBAC or input validation | Larger attack surface, schema drift |
| **Background workers** | Duplicate consumers for one event; no idempotency, backoff, dead-letter, or timeouts | One poison event stalls a partition; lag explodes |
| **Workflows** | Synchronous remote calls in request paths; saga/retry logic re-implemented per service; unbounded in-memory windows | Latency amplification, OOM in retry storms, cost spikes |
| **Classes** | Concrete classes duplicating rules instead of a shared interface; deep inheritance | Cannot mock or change together |
| **Methods** | Type-3/Type-4 clones; hand-written loops for `.filter`/`.sort`; logging or checks removed in fix cycles | Co-change defects; AI debt persists |
| **Imports** | Two libraries for the same job; a whole library for one helper | Bigger images, license and CVE exposure |

## Procedure

1. **Measure the baseline.**
   - Duplication: a clone detector (jscpd, PMD CPD, SonarQube) for Type 1–3;
     sample-read for Type 4.
   - Churn: share of lines changed again within 2 weeks
     (`git log --since` with numstat), and moved vs. duplicated blocks.
   - Dependencies: count, duplicates by purpose, image size, known CVEs.
   - API surface: routes defined vs. routes called in the last 30 days.
   - Coverage and dead code per module.
2. **Walk each stratum** with the table above. For each finding record:
   stratum, artifacts, signature, evidence, severity (blast radius × likelihood),
   and the PDD remedy skill.
3. **Reverse-model purposes** for the hottest areas (`pdd-purpose-modeling`,
   bottom-up mode) so findings can be judged against purpose rather than taste.
4. **Prioritize.** Order: security exposure (unauthenticated or unvalidated
   routes, secrets) → operational fragility (consumers, sync calls, unbounded
   memory) → state bugs → duplication → dependency bloat → visual
   inconsistency.
5. **Plan adoption** in three waves:
   1. constitution + CI trace gate in warn mode + reuse gate for all new work;
   2. graph for the top two purposes, harness adoption, first consolidation PRs;
   3. `--require-tags` per directory, scheduled consolidation, KPIs.

## Output

A report (markdown) with: baseline metrics, a findings table by stratum, the
top ten actions with owner skill, and the adoption plan. Store it as
`docs/pdd-audit-<date>.md` in the audited repository.
