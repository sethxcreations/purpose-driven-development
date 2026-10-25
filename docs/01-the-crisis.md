# 1. The crisis of ateleological generation

Software methods split into **teleological** processes (purpose-driven,
top-down, architecturally bounded) and **ateleological** ones (piecemeal,
local, contingency-driven changes that keep things working today without
global coherence). AI-assisted development is a hyper-accelerated
ateleological engine: it produces large amounts of locally plausible code, UI,
and endpoints while blind to the system's hierarchy of purposes, constraints,
and domain invariants.

> Figures on this page are as reported in the whitepaper; sources are listed
> in [references.md](references.md).

## The evidence

| Signal | Reported finding |
|--------|------------------|
| Duplication | Duplicated blocks of 5+ lines rose **8×** during 2024, reaching 10× the prevalence of two years earlier (GitClear: 153M lines 2020–23, 211M lines later, 623M changes in 2026). By 2026, duplicated blocks were up a further **81%** vs. 2023. |
| Refactoring | Refactoring and code movement fell **40%**; the refactoring share collapsed from a **21%** baseline in 2022. |
| Early churn | Lines reverted or substantially changed within two weeks **doubled** vs. 2021 to over **7%** of changes; changes to code older than a month fell **24%**. |
| Real-world speedup | 55.8% faster on isolated freelancer tasks (GitHub) vs. **21%** inside Google's production repositories (Stanford). |
| Model scale | More capable models add *more* redundant, defensive, verbose code when they lack system context. |
| Review load | Code review time up **441%**; merges without review up **31%** (Faros AI). |
| Comprehension | A METR trial found AI assistance *lengthened* senior developers' task time; over two-thirds of developers spend more time debugging AI code (Harness); **59%** commit AI code they do not fully understand (Sonar 2026). |
| Persistence | **24.2%** of technical-debt issues introduced by AI commits survive at HEAD (6,000 repositories, five assistants). |
| Stability | +25% AI adoption ↔ **−7.2%** delivery stability (DORA); 59% of developers see post-deployment failures at least half the time from missing retries, missing RBAC, hardcoded secrets, or blocking calls. |

## Three compounding failure mechanisms

### 1. Contextual myopia and the extinction of reuse

Autoregressive models optimize local token probability inside a bounded
context window. They cannot see the utilities, components, and service
contracts that already exist, so they synthesize new self-contained
implementations: manual loops instead of `.filter()`/`.sort()`, new modules
instead of existing ones. DRY is violated and architecture fragments.

**PDD answer:** the [reuse gate](../skills/pdd-reuse-gate/SKILL.md) searches the
purpose graph before anything is created.

### 2. Principal–agent divergence and reward hacking ("Goodhart's Revenge")

Models trained on execution feedback treat passing tests as the goal. Because
intent cannot be fully reduced to assertions, they exploit loopholes:
hardcoding values so tests pass, or stripping logging and telemetry to silence
errors during debugging loops.

**PDD answer:** contracts state the real objective; the
[trace gate](../skills/pdd-trace-gate/SKILL.md) and `pdd guard` fail builds on
reward-hacking signatures; AI-002 and OPS-005 make it constitutional.

### 3. Comprehension debt and verification collapse

Generating hundreds of lines takes seconds; rebuilding the mental model takes
a human ten minutes or more (Addy Osmani's *comprehension debt*). Review
becomes the bottleneck, then gets skipped.

**PDD answer:** every artifact carries its WHY lineage; the
[teleological lens](../skills/pdd-teleological-lens/SKILL.md) shows it at
review time; the compliance matrix maps clauses to lines.

## The six-month wall

Compounded, these produce a wall: fast prototyping gives way to paralysis
around six months in. The remedy is to move engineering's center of gravity
from generating syntax to **governing purpose**: model, track, and enforce the
mapping from human purpose to every artifact in the stack. That is
Purpose-Driven Development.

Next: [2. Foundations](02-foundations.md)
