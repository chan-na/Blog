---
title: "Designing MCP Tools That LLM Agents Actually Use Well"
date: 2026-05-30T10:00:00+09:00
draft: false
slug: "mcp-tool-design-principles"
translationKey: "mcp-tool-design-principles"
categories: ["Engineering"]
tags: ["mcp", "llm", "agent", "tool-design"]
summary: "Principles for designing MCP tools an LLM can clearly select, safely execute, verify the results of, and recover from on failure."
---

The most common mistake in MCP tool design is falling into one of two extremes:
exposing your backend API verbatim, or collapsing everything into a single `do_anything` tool.

This post is about the good spot in between — **a unit of work an LLM can clearly select, safely execute, verify with little context, and recover from on failure.** The reasoning leans on Anthropic, the official MCP spec, and OpenAI's function calling docs; sources are collected at the bottom.

---

## 1. Avoid both extremes

**Bad design A — expose the backend API verbatim**

```text
create_node, set_color, set_font, move_node, resize_node, set_padding,
set_gap, delete_node, export_svg, upload_asset, publish_page, ...
```

The LLM has to reason about which tool to call, in what order, on every request. The tool definitions and intermediate results eat context too.

**Bad design B — a single `do_anything`**

```json
{ "tool": "do_anything", "instruction": "Make the page better" }
```

Too abstract for validation, permission separation, destructive-action detection, or regression testing.

**Good design — a unit of work in the middle**

```text
rich read tools
+ a few high-expressiveness write tools
+ separate validate / preview / diff tools
+ server-side guardrails for destructive operations
+ checkpoint / rollback
+ descriptions and schemas verified by eval
```

Anthropic recommends the same: "more tools is not always better — start from a small set of high-impact tools that fit the task." For example, one tool that builds a Login Card can call `create_frame`, `create_text`, `set_padding`, and `set_fill` internally — the agent makes a single call. The key is that one tool can bundle several API calls internally.

---

## 2. Design around units of work, not API calls

> "The backend has 80 functions, so let's make 80 tools."

Natural for a developer, a burden for an agent. Ask instead:

> "What are the units of action an LLM naturally needs to distinguish when handling a user request?"

A design-tool user typically says "make me a login screen" or "turn this section into a pricing card." Internally that may need dozens of operations — create frame, insert text, set padding, change fill — but from the agent's view it's one intent: "change the design." Here a unit-of-work tool like `batch_design` is more natural than exposing every low-level API.

That said, batch isn't the answer for every domain.

| Domain | Recommended shape | Why |
|---|---|---|
| Design / doc / IDE editors | high-expressiveness batch write + rich read/preview | transaction, rollback, diff matter |
| Search / lookup | narrow tools like `search`, `get_by_id` | tasks are independent, little need for transactions |
| Messaging / external sends | split `draft_message` / `send_message` | the preview/confirmation boundary matters |
| Large toolsets | direct tools + `search_tools` | so you don't put every definition in context always |

Numbers for tool count (e.g. 8–15 for an editor-style server) are useful starting points, not absolute rules. Keep it to **the smallest set whose selection boundaries are obvious even to a human**, and retune with eval.

---

## 3. Not everything should be a Tool — Tool vs Resource vs Prompt

MCP gives you two more primitives besides tools. Before deciding what to expose as a tool, ask whether it should be a tool at all.

- **Tool** — something the model *calls to act* or compute. Has side effects, or its result depends on arguments. `create_design`, `search_document`, `batch_design`.
- **Resource** — context data the model/client *reads*. Relatively stable; referenced rather than called. `design_tokens`, `style_guide`, `project_settings`.
- **Prompt** — a reusable workflow template the user explicitly picks (slash commands, etc.).

The rule is simple: **if it acts or computes, it's a tool; if it's reference data you just read, it's a resource.** Wrapping rarely-changing data like a style guide or design tokens in a `get_style_guide` tool forces the agent to reason about whether to call it every time, and the result eats context. As a resource, the client can attach it to the model when needed.

---

## 4. Separate Read / Write / Validate / Export

This is one of the most important principles in MCP design.

| Class | Example tools | Auto-run | Watch out for |
|---|---|---|---|
| Read | `get_state`, `search_nodes`, `get_screenshot` | high | response size limits, pagination |
| Write | `batch_design`, `set_variables` | low–mid | dry-run, diff, idempotency |
| Validate / Preview | `validate_design`, `preview_diff` | high | structure the suggested fixes |
| Safety / Recovery | `create_checkpoint`, `restore_checkpoint` | mid | explicit checkpoint ID |
| Export / External | `export_nodes`, `publish`, `send_message` | low | confirmation, flag side effects |

Separating them means:

- read-only tools let the agent inspect state freely.
- confirmation, dry-run, and audit logs concentrate on write tools only.
- destructive actions are easy to police via schema and server policy.
- validation/preview stand alone, enabling a self-correction loop.

---

## 5. Make Write batch-based without becoming `do_anything`

A write tool is often better as a batch than as a pile of split-up low-level APIs. But **the operations inside the batch must be structured.**

```json
{
  "mode": "dry_run",
  "idempotency_key": "req_2026_05_28_login_card_01",
  "operations": [
    {
      "op_id": "op_1",
      "op": "insert",
      "risk": "safe",
      "parent_id": "node_7f3a",
      "node": { "type": "frame", "name": "Login Card" }
    },
    {
      "op_id": "op_2",
      "op": "delete",
      "risk": "destructive",
      "target_id": "node_8ab2"
    }
  ]
}
```

What a good batch write tool needs:

- `op` is an enum (`insert`, `update`, `move`, `replace`, `delete` ...).
- each operation has an `op_id`, and later operations can reference earlier results.
- targets use the stable `id`/`ref` the server returned.
- `mode` separates `dry_run` from `apply`.
- `idempotency_key` prevents duplicate application during retries.
- partial failures are reported per operation.
- each operation declares its `risk` (`safe` / `caution` / `destructive` / `external_side_effect`), and the server forces dry-run/confirmation on risky ones.

The important part is **not leaving safety to annotations**. The official MCP spec says annotations should be treated as untrusted unless they come from a trusted server. Permissions and confirmation must be enforced in server policy.

---

## 6. Dry-run / Preview / Diff are first-class features

Give write tools a dry-run/preview by default. A natural flow falls out:

```text
get_state → snapshot_layout → create_checkpoint
→ batch_design(dry_run) → preview_diff
→ (user confirmation if needed)
→ batch_design(apply) → get_screenshot → validate
→ fix issues with batch_design
```

A dry-run response should let the agent decide what to do next.

```json
{
  "status": "ok",
  "mode": "dry_run",
  "summary": "3 nodes will be inserted, 1 node will be replaced.",
  "risk_summary": { "safe": 3, "caution": 1, "destructive": 0 },
  "requires_confirmation": false,
  "diff_ref": "diff_41c9",
  "actions_available": [
    { "tool": "preview_diff", "arguments": { "diff_ref": "diff_41c9" } },
    { "tool": "batch_design", "arguments": { "mode": "apply", "diff_ref": "diff_41c9" } }
  ]
}
```

Destructive/external actions like `delete`, `publish`, `send`, `overwrite` get an extra boundary: forced dry-run + auto checkpoint + confirmation + idempotency.

---

## 7. Names, schema, and response decide the agent's behavior

**Names and descriptions are the selection boundary.** The LLM picks a tool from its name and description. Synonym tools invite confusion.

```text
Bad:  get_nodes, fetch_nodes, read_nodes, load_nodes
Good: canvas_get_state, canvas_search_nodes, canvas_batch_design
```

Make the read/write/export/validate nature obvious from the name, and namespace when aggregating servers (`figma_search_nodes`). A description should carry: (1) one sentence on what it does, (2) when to use it, (3) **when not to use it**, (4) dry-run rules for risky actions, (5) an input example.

**Keep the input schema strict and flat** to start. Lean on `enum`, default to `additionalProperties: false`, and avoid ambiguous names (`user_id` over `user`). When the schema is loose, an LLM tends to invent fields that aren't defined, so `additionalProperties: false` cuts off hallucinated fields early. Deep nested objects hurt reliability — when in doubt, go flatter.

**Responses should be high-signal, low-noise.** Control tokens with pagination, field selection, and a `view`/`response_format` enum.

```text
concise   : only what's needed for the final judgment
standard  : includes IDs, labels, paths needed for the next tool call
detailed  : full structure for debug/audit
```

**Use a dual model for identifiers: stable ID + human label.** Force write targets to use a server-returned `id`/`ref` so the agent can't hallucinate IDs, and also give `name`/`path` so a human can read it.

```json
{
  "id": "node_7f3a9c",
  "name": "Primary Login Button",
  "path": "Page/Home/Login Card/Primary Login Button",
  "reference_hint": "Use id for write targets. Use path/name for reasoning."
}
```

---

## 8. Errors should teach a recoverable next action

An agent can do nothing with `{ "error": "Invalid request" }`. A good error tells it what to do next.

```json
{
  "status": "error",
  "error_code": "INVALID_TARGET",
  "message": "Target node 'node_123' does not exist in the current document.",
  "field_path": "operations[2].target.id",
  "recoverable": true,
  "suggestion": {
    "next_tool": "canvas_get_state",
    "reason": "Retrieve current node IDs, then retry with a valid target id."
  },
  "partial_success": {
    "succeeded": ["op_0", "op_1"],
    "failed": [{ "op_id": "op_2", "reason": "INVALID_TARGET" }]
  }
}
```

Enum error codes, the offending field path, an explicit `recoverable` flag, a suggested retry tool, and per-operation partial success for batches — this is what enables efficient retries.

In the same spirit, expose state through **explicit handles**, not hidden state. Instead of `undo_last_action`, which assumes the agent remembers its call history, put checkpoint IDs, cursors, diff refs, and document versions in the response.

---

## 9. Use progressive disclosure for large toolsets

Putting every tool definition in context always raises cost, latency, and confusion. Expose only the core tools plus `search_tools`, and let the agent search for tools that fit the task and load only the schemas it needs, dynamically.

```text
search_tools(query, capability?, risk?, detail_level)
get_tool_schema(tool_name)
```

When there's heavy data manipulation, repeated loops, or multi-step orchestration, don't stream every intermediate result to the model — filter it in a sandboxed code-execution environment and return only the small result. Filtering a 10,000-row spreadsheet, aggregating data from several SaaS apps, or work where PII must not enter the model context are good candidates. Sandboxing, resource limits, and audit are prerequisites.

---

## 10. Evaluation is part of the design

What matters isn't how good the design *looks* but whether it works in real agent calls. Once you have a tool prototype, run eval on 30–100 real-world tasks and read the raw transcripts yourself.

The eval set shouldn't be only happy paths — include multi-step, ambiguous ("just make this prettier"), destructive ("delete the pricing section"), error recovery (stale ID, invalid schema), large response, and external side effects. Track task success rate, tool selection accuracy, recovery rate, **destructive containment** (no unintended destructive actions), token efficiency, schema error rate, and so on.

These aren't measured by vibe — label each scenario and score against it. Tool selection accuracy is the fraction of scenarios where the first (or key) call matches the expected tool; destructive containment is the count of destructive/external scenarios where a destructive action ran without confirmation or dry-run. Both score automatically, so they drop straight into regression.

Common failure patterns in transcripts, and their fixes:

| Failure pattern | Fix |
|---|---|
| Bouncing between similar tools | namespace, "Do NOT use", examples |
| Repeating the same read tool | add IDs, `actions_available`, summary to the response |
| Trying to delete without dry-run | force dry-run on the server |
| Using hallucinated IDs | provide `id`+`path`, allow only IDs in writes |
| Failing to read long responses | add fields/view/limit/cursor |
| Missing arguments | flatten the schema, required, examples |

A state-changing agent can take different valid paths from the same start, so rather than over-fixing a "correct trajectory," evaluate the **end state and safety invariants**. Treat a change to a tool description like a code change — run a regression test on it.

---

## In one line

> An MCP tool is neither "better the more you have" nor "better the fewer you have."
> The point is to build **a unit of work an agent can clearly select, safely execute, verify with little context, and recover from on failure.**

---

## Sources

- [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [MCP official — Tools spec](https://modelcontextprotocol.io/specification/draft/server/tools)
- [OpenAI — Function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI — o3/o4-mini Function Calling Guide](https://developers.openai.com/cookbook/examples/o-series/o3o4-mini_prompting_guide)
