---
name: pdd-governance-kpis
description: Measure and report the four Teleological Governance KPIs - Teleological Coverage, Refactoring-to-Clone Ratio, Attack Surface Reduction, and AI Debt Survival Rate - in place of volume metrics like commits or lines of code. Use for engineering health reports, PDD adoption tracking, or when leadership asks how AI tooling affects quality.
---

# Teleological governance KPIs

Volume metrics (commits, lines added, PR count) reward exactly the bloat PDD
removes. Replace them with four measures of whether the codebase stays a
faithful, minimal projection of purpose.

## The four KPIs

### 1. Teleological Coverage

Share of artifacts with a valid path to an active purpose, plus how complete
the trace links are.

```bash
python tools/pdd.py kpi --scan src
```
Reports `teleological_coverage`, `orphan_artifacts`,
`contract_implementation_rate`, `obstacle_resolution_rate`, and artifact
counts per stratum. For recall-style measures (LinkRecall@k, CompleteRate@k),
sample artifacts, have a reviewer list their true contracts, and compare with
the graph. Target: coverage → 1.0 in governed directories.

### 2. Refactoring-to-Clone Ratio

Moved or consolidated lines divided by newly duplicated lines over a period.
The historical healthy refactoring share was about 21% of changed lines before
AI assistants; under unguided AI use, duplicated blocks rose roughly eightfold
and moves fell about 40%.

- Duplicates: run a clone detector on each release and diff the clone set.
- Moves: `git log -M -C --numstat` and `git diff --color-moved` counts, or a
  code-analytics product that reports moved code.
- Report the ratio and its trend. Target: refactoring above the 21% baseline
  and rising after consolidation PRs land.

### 3. Attack Surface Reduction

Percentage of unused API operations, browser APIs, dependencies, and binary
code removed, from `pdd-debloat` runs. Report routes defined vs. routes called,
dependency count, image size, and CVE count before and after.

### 4. AI Debt Survival Rate

Of the defects or code-smell issues introduced by AI-authored commits, the
share still present at HEAD. Industry baseline: about 24.2%.

- Identify AI-authored commits (co-author trailers, bot accounts, or PR labels).
- Run static analysis at each such commit and at HEAD; count issues introduced
  by the commit that persist.
- Target: well below 24.2%, trending down.

## Supporting signals

Early churn (lines rewritten within two weeks; above 7% signals rework),
review time per PR, share of PRs merged without review, and reward-hack
findings from `pdd guard`.

## Report format

One page: the four KPIs with current value, previous value, target, and a
one-line cause for each movement; top five orphan or duplicate clusters; the
consolidation and debloat PRs planned next. Do not rank individuals by any of
these numbers.
