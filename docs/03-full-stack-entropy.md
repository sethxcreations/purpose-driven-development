# 3. Anatomy of full-stack bloat, redundancy, and rigidity

Without a purpose graph, entropy appears in every layer at once:

- **Bloat:** entities that serve no verified purpose.
- **Redundancy:** several different entities fulfilling the same intent.
- **Rigidity:** brittle coupling that resists change.

PDD tracks ten artifact strata. The `stratum` field in `purpose-graph.yaml`
uses these keys.

| Key | Stratum |
|-----|---------|
| `block` | Software and design blocks (modules, bounded contexts, composite patterns) |
| `screen` | Screens / GUI views |
| `elem` | Screen elements (DOM nodes, widgets) |
| `state` | Application and UI state |
| `api` | API operations and microservice boundaries |
| `worker` | Background workers |
| `workflow` | Asynchronous workflows and orchestration |
| `class` | Classes and domain entities |
| `method` | Methods and functions |
| `import` | Package and module imports |

## Software and design blocks

Lacking global context (reported by 65% of enterprise engineers), models
generate flat, generic implementations that ignore module boundaries and the
design system. Instead of extending a domain block or composite layout, they
create parallel standalone blocks with duplicated validation and hardwired
dependencies.

## Screens and screen elements

Multimodal models turning mockups or prompts into views produce deep,
ungrouped DOM hierarchies. Without explicit hierarchy grouping (DesignCoder
ablation), TreeBLEU drops from 0.66 to 0.38, Container Match from 0.73 to
0.41, and tree edit distance worsens from 27.32 to 36.57. Instead of
parameterizing a screen for a new role or viewport, assistants clone it
(`CheckoutScreenV2.tsx`, `AdminUserModalCopy.tsx`). At element level: redundant
wrappers, inline CSS bypassing tokens, duplicate widgets missing accessibility
and telemetry.

## Frontend and application state

Up to 80% of high-impact web defects come from DOM manipulation errors driven
by exploding UI state transitions (Ocariza et al.). Modern frameworks keep
rendering linear by enforcing one-way binding from state to UI. Asked to fix a
glitch, an assistant adds a boolean flag, a duplicated server-cache slice, or
an effect that mutates state during render. In virtual-DOM frameworks (React,
Blazor) and fine-grained reactive ones (Vue, Svelte) alike, the result is
cascading re-renders, races, and impossible state combinations.

## APIs and microservice boundaries

A service's responsibility is only visible across its whole OpenAPI spec.
Seeing one request/response pair at a time, an assistant adds a new endpoint
for a slightly different payload instead of composing operations or adding a
query parameter. Proliferated endpoints widen the attack surface (in PWAs over
90% of reachable APIs are unneeded) and often skip RBAC and input sanitization.

## Background workers and asynchronous workflows

The most destructive rigidity. Assistants put expensive synchronous calls in
the hot path and generate workers without idempotency keys, backoff,
telemetry, or dead-letter routing. Two classic failures:

1. **Partition-stalling poison events.** A malformed event on one Kafka
   partition sends a naive handler into a swallowed infinite retry, or it
   blocks with no timeout. A partition belongs to one consumer, so CPU idles
   while lag climbs past 400,000 messages, freezing every aggregate hashed to
   that partition. Missing: dead-letter isolation and offset-commit recovery.
2. **Unbounded circuit-breaker memory.** Asked to track rolling failure rates,
   models write a deque of timestamps over 60 seconds: amortized O(1), but
   memory grows with traffic. A retry storm piles up hundreds of thousands of
   entries and the node crashes. The purpose-driven design: a fixed ring of 60
   one-second buckets, two 4-byte integers each, **480 bytes per destination**
   (~20–25 MB for 40,000 destinations), with a **20-attempt minimum sample
   floor** before opening. See [harnesses/python/circuit_breaker.py](../harnesses/python/circuit_breaker.py).

## Classes, methods, and imports

Assistants prefer adding to restructuring, driving the 8× duplication surge
and 40% drop in moved code. Classes: concrete utility classes duplicate
business rules instead of injecting a shared ("can-do") interface. Methods:
Type-4 clones, verbose loops, and logging or security checks stripped during
break-fix cycles. Imports: heavy libraries pulled in for one helper, inflating
images and adding license liabilities and exploitable gadgets.

## Summary table

| Stratum | AI bloat mechanism | Redundancy signature | Rigidity consequence |
|---------|--------------------|----------------------|----------------------|
| Software & design blocks | Context-free synthesis ignoring bounded contexts and tokens | Parallel modules with duplicated validation and layout | High coupling; cross-cutting updates cannot propagate |
| Screens | Cloning whole views for minor state or persona variations | High visual similarity (CLIP/SSIM) with diverging DOM | Maintenance surface multiplied across N files |
| Screen elements | Ungrouped elements and inline style overrides | Low Container Match, inflated tree edit distance | Broken responsive layouts, degraded accessibility, bloated DOM |
| App & UI state | Ad-hoc flags and imperative DOM mutation | Mirrored or derived state across components and stores | Exponential transition bugs; cascading re-renders |
| APIs | Endpoint-per-screen without whole-service context | High semantic similarity across summaries, params, schemas | Larger attack surface, missing RBAC, schema drift |
| Background workers | Stateful consumers without dead-letter or memory bounds | Duplicate consumers; unbounded timestamp deques | Partition head-of-line blocking; OOM in retry storms |
| Async workflows | Synchronous blocking calls; flat orchestration without fallbacks | Saga/retry logic re-implemented per service | Latency amplification, silent failures, cost explosions |
| Classes | Bypassing dependency injection for monolithic concrete classes | Overlapping domain models violating SRP and DRY | Cannot mock or test in isolation; fragile inheritance |
| Methods | Re-implementing built-ins; reward-hacking tests | Type-3 and Type-4 clones | Co-change defects; 24.2% of AI debt persists at HEAD |
| Imports | Whole libraries for trivial utilities | Several packages for one intent (Type I bloat) | Binary size, dependency hell, license risk, ROP gadgets |

Audit any codebase against this table with
[pdd-full-stack-audit](../skills/pdd-full-stack-audit/SKILL.md).

Next: [4. The PDD paradigm](04-paradigm.md)
