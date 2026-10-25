---
name: pdd-trace-gate
description: Verify a pull request or branch against the purpose graph - every added or changed artifact must IMPLEMENT a contract that traces to an active purpose, no reward-hacking signatures (skipped tests, hardcoded returns, removed logging or security checks), sealed specs untouched - and set this up as a CI gate. Use when reviewing a PR, before merge, or when wiring PDD into CI.
---

# Trace gate: verify every change traces to purpose

The reactive counterpart of the reuse gate. The whitepaper pairs an
architecture-level trace recovery (TransArC: extract components from docs and
code, link through them) with a validated trace responsibility graph
(TraceRank VTRG). In practice: explicit tags and graph entries give the
validated links; you, the reviewing agent, recover and judge the rest.

## Review procedure (agent or human)

1. **List changed artifacts** across all ten strata: new or changed files,
   classes, methods, components, state slices, routes, consumers, workflows,
   and manifest dependencies. `git diff --stat origin/main...HEAD` plus the
   manifest diff.
2. **Run the checker** on the branch:
   ```bash
   python tools/pdd.py check --scan src --require-tags --specs specs/<feature>
   ```
   Errors fail the review: orphans, unknown references, missing in-scope MUST
   invariants, scattered obstacle resolutions, tampered sealed specs.
3. **Recover links the tags cannot express.** For each changed artifact, read
   it and name the contract clause it serves. Check the tag is truthful: an
   artifact tagged `OC-PAY-AUTH` that sends marketing email is mis-traced.
   Use the architecture as the intermediate layer: artifact → component or
   service → contract. A link you cannot justify is an orphan, whatever the
   tag says.
4. **Check for reward hacking:**
   ```bash
   git diff origin/main...HEAD | python tools/pdd.py guard -
   ```
   Then read the test diff yourself. Fail on: skipped or deleted tests,
   loosened assertions, expected values copied from the implementation's
   output, constant returns in production code that match test fixtures,
   removed logging/tracing/metrics, removed authorization or validation, new
   blanket `except`/`catch`, new type-checker or linter suppressions.
5. **Check minimal sufficiency at review level.** Does every added artifact
   cover a clause no other artifact covers? Are there bespoke retries or
   defensive checks for obstacles that already have a resolution? (See
   `pdd-debloat`.)
6. **Check reuse.** Was the reuse gate recorded? Does any new artifact
   duplicate an existing one (`pdd-closeness-mapping`)?
7. **Report** as a short table: artifact, contract, verdict (ok / orphan /
   mis-traced / duplicate / reward-hack), and the required fix.

## CI setup

Copy `templates/pdd-ci.yml` to `.github/workflows/pdd.yml` (or translate it to
your CI). It runs `pdd check` on every PR and `pdd guard` on the PR diff, and
fails on errors. Start with `--require-tags` off on a legacy codebase and turn
it on per directory as the graph fills in (`--scan src/payments`).

Add `templates/pull_request_template.md` as `.github/pull_request_template.md`
so authors state the contract, the reuse decision, and artifacts added and
removed.

## Waivers

A SHOULD violation may be waived with `pdd: allow <INVARIANT-ID>` on the line
and a reason in the PR. MUST violations are never waived in code; changing a
MUST is a constitution amendment (`pdd-constitution`).
