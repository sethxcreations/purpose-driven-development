# Worked example: checkout

A small checkout flow modeled end to end.

| File | Shows |
|------|-------|
| `purpose-graph.yaml` | Purposes (one active, one retired), an AND/OR intent tree, contracts with DomPre/DomPost/ReqPre/ReqPost, two obstacles each resolved once |
| `specs/` | The sealed spec cascade: `spec.md`, `plan.md`, `tasks.md` with a compliance matrix |
| `src/payments/authorize.py` | A contract implementation: RBAC, parameterized SQL, idempotency, no local retries |
| `src/payments/resilience.py` | The single binding to the circuit-breaker harness (resolution contract) |
| `src/api/orders.py` | One endpoint, extended rather than cloned |
| `src/workers/order_events.py` | A worker bound to the partition-resilient consumer harness |
| `src/ui/` | One screen with a `variant` prop instead of a copied file; one normalized store |
| `reward-hack.diff` | What `pdd guard` catches |

```bash
python tools/pdd.py check --graph examples/checkout/purpose-graph.yaml --scan examples/checkout/src --require-tags --specs examples/checkout/specs
python tools/pdd.py lens  --graph examples/checkout/purpose-graph.yaml --scan examples/checkout/src src/payments/authorize.py
python tools/pdd.py guard examples/checkout/reward-hack.diff
```

Try breaking it: add a file under `src/` without a tag, set `P-CHECKOUT` to
`retired`, or add a second artifact implementing `OC-RES-PSP-FAILURE`, and run
`check` again.

The source files are illustrative; they import modules (`shared.validation`,
`@acme/design-system`) that are not part of this repository.
