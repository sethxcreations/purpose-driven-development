---
name: pdd-runtime-guardrails
description: Design and implement the six-layer runtime guardrail architecture (input, retrieval, planning, inference, action, output/continuous) for AI agents and tool-using services, with per-contract tool allowlists and schema-checked arguments before any tool, API, database, or MCP call executes. Use when building, deploying, or reviewing an AI agent, an LLM feature, or an MCP integration.
---

# Six-layer runtime guardrails

Vassilev's 2026 incompleteness result: a guardrail is a finite checker over an
unbounded input space, so some constraint will always be enforced wrongly on
some input (Theorem 2), and a finite context window makes it worse (Theorem 3).
Build-time rules and prompt constitutions are therefore never enough. PDD adds
runtime enforcement tied to the purpose graph, in depth, at every layer.

## The six layers

| # | Layer | Enforces | Bound to the graph by |
|---|-------|----------|-----------------------|
| 1 | **Input** | Authenticate the caller; detect prompt injection and jailbreak payloads; size and schema limits | Contract `req_pre`; SEC invariants |
| 2 | **Retrieval** | RBAC and least privilege on what RAG may fetch for this caller; mark retrieved text as data, never instructions | Contract `agent` and entities |
| 3 | **Planning** | Audit the agent's goal decomposition; reject sub-goals that map to no active contract | Purpose graph: every sub-goal must trace to an intent |
| 4 | **Inference** | Check intermediate reasoning steps and claims against contract preconditions | `req_pre`, `dom_pre` |
| 5 | **Action** | Between the model's tool call and execution: tool is on the active contract's allowlist; arguments validate against the tool schema and constitution; high-impact actions need confirmation | `contracts[].tools`; AI-001 |
| 6 | **Output and continuous** | Scan responses for sensitive data; stream decision traces (OpenTelemetry) and alert on drift | `req_post`; OPS-005 |

Layer 5 is the one that prevents damage. Build it first.

## Procedure

1. **Model the agent's contracts.** Each thing the agent may do is an
   Operational Contract with `tools: [...]` listing exactly the tools (APIs,
   database operations, MCP server tools) it may call. No contract, no tool.
2. **Implement the action guardrail** as middleware wrapping every tool
   dispatcher:
   ```python
   def guarded_call(active_contract, tool, args, principal):
       if tool.name not in graph.contracts[active_contract]["tools"]:
           deny("tool not allowlisted for " + active_contract)
       validate(args, tool.schema)                      # strict JSON Schema
       enforce_constitution(tool, args)                 # e.g. no raw SQL, no external email
       if tool.impact == "high" and not confirmed(principal, tool, args):
           deny("needs confirmation")
       trace.emit("tool_call", contract=active_contract, tool=tool.name, decision="allow")
       return tool.run(args)
   ```
   Deny by default. Log every decision, allowed or denied.
3. **Input and retrieval:** authenticate before the model sees anything;
   filter retrieval by the caller's permissions, not the agent's; wrap
   retrieved content so the model sees it as quoted data.
4. **Planning and inference:** have the planner output sub-goals with the
   contract each serves; reject plans containing sub-goals with none.
5. **Output:** redact secrets and personal data; check the answer satisfies
   `req_post` where it is checkable.
6. **Continuous:** export decision traces; alert on spikes in denials, new
   tool-argument shapes, or output distribution shifts. Feed incidents back
   as new obstacles and invariants.
7. **Test with adversarial cases**: injected instructions in retrieved
   documents and tool outputs, out-of-allowlist tool requests, oversized and
   malformed arguments, and goal-hijack prompts.

## Constitutional infrastructure templates

Agents also must not reinvent operational logic at runtime. Bind them to the
harnesses (`pdd-resilience-harnesses`) and give them pre-verified templates
for any action with blast radius (deploys, migrations, payments, messaging).
