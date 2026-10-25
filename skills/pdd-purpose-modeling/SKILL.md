---
name: pdd-purpose-modeling
description: Elicit Strategic Purposes and refine them into Functional Intents with AND/OR/XOR goal trees using KAOS-style WHY/HOW questioning. Use when starting a product, feature, or epic, when a request has no stated reason, or when existing code has no clear purpose.
---

# Model purposes and intents (Tiers 2–3)

A **Strategic Purpose** answers the terminal WHY: whose value, of what kind,
measured how. A **Functional Intent** is a technology-agnostic capability that
serves a purpose. Intents sit in the transition space between the problem
(stakeholder language) and the solution (code), which is what makes them
traceable from both directions.

## Procedure

1. **Capture the purpose.**
   - Statement: "<Stakeholder> can <outcome>, so that <business value>."
   - Stakeholders, including the ones who pay the cost (support, finance,
     operations, compliance).
   - Success measure: an observable number or event. If nobody can name one,
     say so to the human; a purpose with no measure cannot be retired later.
   - Status: `active`. Purposes are retired, not deleted, so the checker can
     find the artifacts that served them.
2. **Refine downward by asking HOW?** For each purpose, ask "how could the
   system make this true?" Each answer is a child intent. Mark the refinement:
   - `AND`: all children are needed.
   - `OR`: any child suffices (alternatives that can coexist, such as card or
     wallet payment).
   - `XOR`: exactly one must be chosen (mutually exclusive designs). Record
     which one was chosen and why.
3. **Stop at assignable leaves.** A leaf intent is one capability one agent can
   own: a service, a worker, a UI surface, an external system, or a person.
   If a leaf needs two agents to cooperate, refine again.
4. **Check upward by asking WHY?** For every leaf, ask why it is needed and
   confirm the answer is its parent. If the answer is a different purpose,
   move it. If there is no answer, it is speculative scope; drop it or ask.
5. **Check minimal reduction.** For each AND node, confirm the children are
   sufficient for the parent and that removing any one makes them
   insufficient. Extra children are future bloat.
6. **Name domain entities** each intent reads or changes. Shared entities are
   how closeness mapping later finds overlap across services.
7. **Look for existing intents first.** Search `purpose-graph.yaml` for
   intents with the same entities and verbs before adding new ones. Two intents
   that mean the same thing guarantee duplicate code later.
8. **Write it down** in `purpose-graph.yaml` (`purposes:`, `intents:`) and in
   the Purpose and Functional intents sections of `spec.md`.

## Retiring purposes

When a purpose ends (a campaign, a sunset product, a removed integration),
set `status: retired`. Run `pdd check`: every artifact that served only that
purpose is now reported as teleological bloat. Hand the list to `pdd-debloat`.

## Reverse modeling an existing codebase

When code exists without a graph, work bottom-up: list the system's user
journeys, APIs, workers, and scheduled jobs; ask WHY of each until you reach a
business outcome; group them into purposes; then fill in intents top-down.
Mark anything you cannot justify as a debloat candidate rather than inventing
a purpose for it.

## Output

- Updated `purposes:` and `intents:` in `purpose-graph.yaml`.
- An ASCII refinement tree in `spec.md`.
- A list of open questions for the human (missing measures, unclear XOR choices).
