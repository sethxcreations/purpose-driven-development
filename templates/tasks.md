# Tasks: <feature name>

> Atomic work items derived from `plan.md`. One task, one contract, one reviewable change.
> An agent executing a task must pass the reuse gate first and tag every artifact it creates.

## T-001 — <imperative title>

- **Implements:** OC-…
- **Constrained by:** SEC-…, OPS-…
- **Reuse gate result:** reuse `<artifact>` / extend `<artifact>` / new (closest Φ = …)
- **Allowed to create:** <files or symbols, with strata>
- **Allowed to modify:** <files>
- **Must not touch:** <files, tests, telemetry>
- **Done when:**
  - [ ] every ReqPost clause of OC-… is covered by a named test
  - [ ] every new artifact carries `pdd: implements OC-…` or is declared in `purpose-graph.yaml`
  - [ ] `python tools/pdd.py check --scan src` passes
  - [ ] `git diff | python tools/pdd.py guard -` reports no errors
  - [ ] contract clause self-check done (`pdd-contract-coverage` skill)

## T-002 — …

## Compliance traceability matrix

Fill as tasks land. Reviewers check this instead of re-deriving intent from code.

| Invariant / clause | Contract | Artifact | File:line | Test |
|--------------------|----------|----------|-----------|------|
| SEC-002 | OC-… | A-… | `src/…:42` | `test_…` |
| OC-… ReqPost 1 | OC-… | A-… | `src/…:57` | `test_…` |
