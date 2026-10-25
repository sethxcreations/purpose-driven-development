---
name: pdd-reuse-gate
description: Pre-synthesis closeness gate (Intent-to-Artifact RAG). Before creating any new file, function, class, component, screen, state slice, endpoint, worker, workflow, or dependency, search for the closest existing artifact and decide reuse (Φ ≥ 0.85), extend (0.65–0.85), or create (< 0.65). Use every time you are about to add something new.
---

# Reuse gate: search before you synthesize

AI assistants default to writing new, self-contained code because they cannot
see what already exists. This gate makes you look first. It is the single
highest-leverage PDD habit.

## Thresholds

Score the closest existing artifact with the closeness metric
Φ = α·Sim_struct + β·Sim_sem + γ·Sim_teleo (see `pdd-closeness-mapping`).

| Φ | Decision | What you do |
|---|----------|-------------|
| **≥ 0.85** | **Reuse** | Do not create anything. Import or call the existing artifact. |
| **0.65 – 0.85** | **Extend** | Parameterize the existing artifact (a new argument, prop, query parameter, keyframe, strategy, or interface implementation). Do not copy it. |
| **< 0.65** | **Create** | Create a new artifact, tagged to its contract. |

When you cannot compute numbers, estimate each similarity on a 0–1 scale and
show your reasoning; the decision bands still apply.

## Procedure

1. **State the need** as the contract clause you are implementing:
   "OC-PAY-AUTH ReqPost 1: authorization is idempotent per cart id."
2. **Search all strata the need could live in**, not just the one you were
   about to write in:
   - `purpose-graph.yaml`: artifacts implementing the same contract or
     contracts under the same intent (Sim_teleo is highest here);
   - code search by verb and entity (`authorize`, `payment`, `idempot`);
   - for UI: design-system primitives and existing screens with the same
     entity; for APIs: the OpenAPI spec of every service touching the entity;
     for workers: consumers of the same event; for dependencies: the manifest
     and the standard library;
   - harnesses for anything resembling retry, timeout, breaker, consumer,
     validation, or authorization.
3. **Score the top candidates.** For each: what does it do, which contract and
   intent does it serve, how similar is its structure, how similar is its
   meaning? Teleology dominates: same contract means reuse even if the code
   looks different; different purposes under conflicting invariants means
   keep separate even if the code looks identical.
4. **Decide and record** in the task or PR:
   `Reuse gate: extend src/ui/CheckoutScreen.tsx (Φ≈0.78: same contract, adds agent-assisted variant)`.
5. **Act on the decision.**
   - Reuse: inject the existing signature into your context and call it.
   - Extend: change the existing artifact minimally and keep its existing
     callers and tests passing; add a test for the new parameter.
   - Create: tag the new artifact with `pdd: implements OC-… stratum=…`.

## Stratum-specific extension moves

| Stratum | Instead of copying, … |
|---------|-----------------------|
| screen / block | add typed props or keyframes for role, viewport, or workflow stage |
| elem | use or extend the design-system primitive; never inline-style a copy |
| state | derive with a selector; add a state to the existing machine |
| api | add a query parameter or field projection to the existing operation |
| worker | subscribe the existing consumer group's handler to the extra event |
| workflow | add a step or branch to the existing orchestration |
| class | implement the shared interface; inject it |
| method | add a parameter or strategy; call the built-in (`.filter`, `.sort`) |
| import | use the dependency already serving that intent, or the standard library |

## Red flags that you skipped the gate

File names ending in `V2`, `Copy`, `New`, `2`; a second date formatter,
validator, HTTP client, or retry helper; an endpoint that differs from another
only in returned fields; a boolean flag that mirrors existing state.
