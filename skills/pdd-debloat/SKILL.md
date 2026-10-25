---
name: pdd-debloat
description: Remove teleological bloat safely - orphan artifacts, code serving retired purposes, unreached paths, unused API endpoints and dependencies, redundant DOM wrappers - using a multi-advisor process (coverage, static security analysis, constitution) that never deletes security checks or obstacle handlers. Use on release branches, after retiring a purpose, or when cleaning up AI-generated code.
---

# Multi-advisor debloating

Two kinds of bloat: **Type I**, unneeded dependency and shared-library code,
and **Type II**, unneeded application features and dead paths. PDD removes
both, but naive debloaters also delete null checks, bounds checks, and error
handlers that tests never exercise. The LEADER pattern fixes this: several
advisors propose, one arbiter bound by the constitution decides.

## Advisors

| Advisor | Finds | Tools |
|---------|-------|-------|
| **Teleology** | orphans, artifacts serving only retired purposes, unimplemented contracts | `pdd check`, `pdd kpi` |
| **Coverage** | code never executed by the verification suites or production traffic | coverage.py, istanbul/c8, llvm-cov, gcov, JaCoCo; production profiling |
| **Static** | unreachable code, unused exports, unused imports and packages | ts-prune/knip, vulture, deadcode, depcheck, cargo-udeps, `go mod why` |
| **Surface** | API routes and browser APIs no user journey calls | gateway access logs, end-to-end journey recordings (DeView-style record and replay) |
| **UI structure** | wrapper elements that group nothing, unused components and styles | DOM tree inspection, design-system usage reports |
| **Security** | checks that look dead but defend an obstacle or invariant | SAST (Semgrep, CodeQL), the constitution, the obstacle list |

## Procedure

1. **Gather candidates** from each advisor into one list: artifact, stratum,
   advisor(s), evidence.
2. **Arbitrate each candidate** (you are the arbiter). Keep it if any of these hold:
   - it is on an obstacle's resolution path or is a security boundary check
     (authorization, validation, bounds, null, escaping, rate limit), even if
     coverage says it never ran;
   - it is required by a MUST invariant;
   - it serves an active purpose through a path the coverage run did not
     exercise (seasonal jobs, disaster recovery, rare locales);
   - removing it changes behaviour on inputs outside the test suite in a way
     you cannot rule out (generality risk).
   Otherwise mark it for removal.
3. **Test minimal sufficiency.** For each contract with candidates, remove the
   candidate and run the contract's full verification suite (functional,
   robustness, security). If everything still passes and the arbiter found no
   keep reason, the artifact violates Minimal Sufficiency: delete it. If
   something fails, the coverage advisor was wrong: keep it and add the
   missing tag.
4. **Remove in small PRs** grouped by contract or stratum, each listing the
   evidence per artifact and the suites run. Update `purpose-graph.yaml`.
5. **For dependencies**, remove the manifest entry and lockfile entries, rebuild,
   and record image size and CVE count before and after.
6. **For APIs**, deprecate first (gateway rewrite or 410 with telemetry), watch
   traffic for one release cycle, then delete.

## After retiring a purpose

```bash
python tools/pdd.py check --scan src --require-tags   # lists artifacts serving only retired purposes
```
Every artifact reported is a removal candidate; arbitrate as above.

## Never remove

Logging, tracing, or metrics (OPS-005); authorization or validation; obstacle
handlers; tests. Never "debloat" a test suite to make coverage look complete.
