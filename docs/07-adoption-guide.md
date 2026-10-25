# 7. Adoption guide

PDD works for any software or product team, with or without AI agents, in any
language. Start small: one purpose, one feature, one CI check.

## Day 1: one feature, end to end

1. **Copy the kit** into your repository:
   ```bash
   cp templates/constitution.yaml   <repo>/constitution.yaml
   cp templates/purpose-graph.yaml  <repo>/purpose-graph.yaml
   cp tools/pdd.py                  <repo>/tools/pdd.py
   cp -r harnesses                  <repo>/harnesses        # if you use Python; otherwise port them
   cp templates/pdd-ci.yml          <repo>/.github/workflows/pdd.yml
   cp templates/pull_request_template.md <repo>/.github/pull_request_template.md
   pip install pyyaml
   ```
2. **Trim the constitution** to what your team actually enforces today
   (`pdd-constitution`). Keep the MUSTs few and real.
3. **Model the purpose** of one feature you are about to build
   (`pdd-purpose-modeling`), then its contracts and obstacles
   (`pdd-operational-contracts`). Write `specs/<feature>/spec.md`, `plan.md`,
   `tasks.md` and seal them (`pdd-spec-cascade`).
4. **Build it** with the reuse gate and tags; run `pdd check` and `pdd guard`.
5. **Turn on CI** in warn-only mode for legacy directories and enforce mode for
   the new feature's directory.

## Installing the skills for agents

- **Claude Code:** add this repository as a plugin marketplace and install the
  `purpose-driven-development` plugin, or copy `skills/*` into
  `.claude/skills/` in your project (or `~/.claude/skills/` for all projects).
- **Other agents (Cursor, Copilot, Codex, Devin, Gemini, …):** reference
  `AGENTS.md` from the repository root of your project and copy the skills
  directory; every `SKILL.md` is plain markdown with a short frontmatter and
  works as a rules or instructions file.
- **Humans:** the skills double as checklists. Product managers use
  `pdd-purpose-modeling`; architects `pdd-constitution` and
  `pdd-operational-contracts`; reviewers `pdd-trace-gate` and
  `pdd-teleological-lens`.

## Maturity levels

| Level | Practices | Exit criterion |
|-------|-----------|----------------|
| **0 — Ateleological** | Requirements in tickets; AI writes code from prompts | — |
| **1 — Constituted** | `constitution.yaml`; PR template; `pdd guard` in CI | Reward-hack signatures blocked |
| **2 — Purposeful** | Spec cascade for new features; reuse gate habitual; new code tagged | All new artifacts trace to purposes |
| **3 — Governed** | `pdd check --require-tags` enforced per directory; harnesses mandatory; debloat on releases | Teleological coverage ≥ 0.9 in governed code |
| **4 — Self-cleaning** | Scheduled consolidation; runtime guardrails for all agents; KPIs reviewed monthly | Refactoring-to-clone ratio above baseline; AI debt survival falling |

## Roles

| Role | Owns |
|------|------|
| Product | Strategic purposes, success measures, retiring purposes |
| Architecture | Constitution, intent trees, resolution contracts, harnesses |
| Engineering (human or agent) | Contracts' implementation, tags, reuse decisions |
| Review | Trace gate, lens-based review, waivers |
| Platform / SRE | Harnesses, runtime guardrails, telemetry |
| Leadership | Governance KPIs instead of volume metrics |

## Using PDD outside code

The same graph works for product work without code: purposes and intents in
discovery, contracts as acceptance criteria, obstacles as risks, and
"artifacts" as designs, documents, campaigns, or experiments. The zero-orphan
law then asks of every deliverable: which purpose does this serve, and is that
purpose still active?

## Common pitfalls

- **Modeling everything up front.** Model what you are about to change.
  Coverage grows with the work.
- **Purposes without measures.** They can never be retired, so their artifacts
  never become removable.
- **Tagging without meaning.** A tag pointing at a vague contract satisfies the
  checker and nothing else. Review the trace, not just its presence.
- **Too many MUSTs.** Teams then waive them. Prefer SHOULD until a rule has
  proven itself.
- **Treating the graph as documentation.** It is a build input. If CI does not
  read it, it will rot like every requirements document before it.

Next: [8. Tooling map](08-tooling-map.md)
