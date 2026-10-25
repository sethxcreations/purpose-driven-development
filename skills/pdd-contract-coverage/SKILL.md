---
name: pdd-contract-coverage
description: Before committing, check generated code clause by clause against its Operational Contract (ReqPre, ReqPost, ReqTrig, obstacles, invariants) to catch omitted requirements such as RBAC checks, retry bounds, idempotency, or telemetry, then fix and re-check. Use after implementing a task and before opening a PR.
---

# Contract coverage self-check

The whitepaper's Gradient-Guided Prompt Reformulation (North et al.) measures
which requirement clauses had no influence on the generated code and
re-prompts until every clause is covered. Without model gradients, an agent
gets most of the benefit by doing the attribution explicitly: map every clause
to the exact code and test that satisfy it, and treat any unmapped clause as
an omission.

## Procedure

1. **Collect the clauses.** From the contract in `plan.md` /
   `purpose-graph.yaml`: each `req_pre`, `req_post`, and `req_trig` item; each
   obstacle that obstructs the contract and its resolution contract; each
   invariant in `constrained_by` plus global invariants.
2. **Attribute each clause** in a table:

   | Clause | Code (file:line) | Test | Status |
   |--------|------------------|------|--------|
   | ReqPre: caller holds `payments:authorize` | `authorize.py:24` | `test_authorize_forbidden` | covered |
   | ReqPost: idempotent per cart id | `authorize.py:31` | `test_authorize_idempotent` | covered |
   | X-PSP-TIMEOUT → OC-RES-PSP-FAILURE | `authorize.py:36` calls `psp_breaker` | `test_authorize_psp_timeout` | covered |
   | SEC-002 parameterized SQL | `authorize.py:26,31,41` | static check | covered |
   | OPS-005 telemetry kept | — | — | **missing: no event on decline** |

   A clause is covered only if you can point to the line that enforces it and
   the test that would fail without it. "Handled implicitly" is not covered.
3. **Fix every missing clause**, then redo the table. Commonly omitted:
   authorization checks, input validation at the boundary, idempotency keys,
   timeouts on remote calls, telemetry on failure paths, emitting the event
   in ReqPost, accessibility names on new controls.
4. **Check the reverse direction.** List code you wrote that maps to no
   clause. Each such line is either a missing clause (add it to the contract
   with the human's agreement) or bloat (delete it). Defensive checks for an
   obstacle that a resolution contract already handles are bloat.
5. **Run the gates.**
   ```bash
   python tools/pdd.py check --scan src --require-tags
   git diff origin/main | python tools/pdd.py guard -
   ```
6. Paste the table into the PR's compliance matrix (`tasks.md`).

## Do not

- Satisfy a clause by changing the test instead of the code.
- Mark a clause covered because a comment mentions it.
- Expand scope to "cover" clauses from other contracts.
