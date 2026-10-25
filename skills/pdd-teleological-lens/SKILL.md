---
name: pdd-teleological-lens
description: Explain why a piece of code exists by showing its upward WHY lineage (artifact → contract → intent → purpose), its governing constitutional invariants and obstacles, and its nearest neighbours, to cut comprehension debt in review and maintenance. Use when reviewing unfamiliar or AI-generated code, before modifying code you did not write, or when someone asks "why is this here?".
---

# Teleological lens

Generating code takes seconds; understanding it takes a person ten minutes or
more. Reviews have ballooned and many developers now merge AI code they do
not understand. The lens answers the reviewer's first question, "why does
this exist and what must it never do?", before they read a line.

## Procedure

1. **Resolve the artifact**: by id, path, or symbol.
   ```bash
   python tools/pdd.py lens src/payments/authorize.py --scan src
   ```
2. **Present the lineage**, top-down for humans:
   ```
   PURPOSE  P-CHECKOUT  Shoppers can pay quickly and safely …
   INTENT   I-PAY → I-PAY-CARD  The system can authorize a card payment
   CONTRACT OC-PAY-AUTH  ReqPre: caller holds payments:authorize …
                         ReqPost: idempotent per cart id; event emitted
   MUST     SEC-002 parameterized SQL · SEC-003 RBAC · OPS-001 timeout+fallback
   OBSTACLE X-PSP-TIMEOUT → resolved by OC-RES-PSP-FAILURE (psp_breaker)
   NEIGHBOURS  0.62 A-API-AUTHORIZE (api) …
   ```
3. **Map the code to the contract**: for each ReqPre/ReqPost clause, point to
   the lines that enforce it. This is the reviewer's reading guide.
4. **Flag mismatches**: code with no clause (possible bloat), clauses with no
   code (omission), invariants the code appears to violate, neighbours with
   high closeness (possible duplication).
5. **If there is no lineage**, say so plainly: the artifact is an orphan.
   Offer two paths: model the missing purpose with the human, or mark it for
   `pdd-debloat`.

## In review

Put the lens output at the top of the review comment for each significant
artifact. Reviewers then check the code against the contract instead of
reconstructing the intent themselves. For an IDE, the same output fits a hover
card; a language-server extension can call `pdd lens` on the file
under the cursor.

## In maintenance

Before changing code, run the lens. If your change would alter a ReqPost
clause, it is a contract change: update `plan.md` and the graph first.
