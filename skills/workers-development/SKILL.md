---
name: workers-development
description: Find tools for running, inspecting, and debugging Cloudflare Workers locally or in production, and testing deployed changes with previews. Use for Wrangler or Cloudflare Vite development, binding data inspection, and runtime investigation.
---

# Workers Development and Debugging

Use the project's installed tooling, scripts, and configuration as the starting point. Choose the capabilities relevant to the task; installed help, API schemas, and current docs describe their supported operations.

| Need | Tools and discovery |
| --- | --- |
| Run locally | Use the existing Wrangler or Cloudflare Vite dev script. Inspect package scripts, `wrangler --help`, and [local development docs](https://developers.cloudflare.com/workers/local-development/) for available modes. |
| Inspect local binding data | [Local Explorer](https://developers.cloudflare.com/workers/local-development/local-explorer/) provides a UI and API for KV, R2, D1, SQLite Durable Objects, and Workflows. Use the startup hint's routes and examples; fetch and extract the relevant operations from its OpenAPI schema when needed. Open the UI with `e` in Wrangler or `/cdn-cgi/local/explorer` on the actual dev origin. |
| Debug local execution | Explorer automatically captures invocation traces and logs, including binding operations. Discover telemetry queries through startup hints or its API schema; existing traces can reveal failing operations without adding instrumentation. |
| Query production telemetry | If the Cloudflare MCP server is connected (bundled with this plugin), use `search` to discover Workers Observability telemetry keys, values, and query operations, then `execute` to call them. The query API supports logs, metrics, invocations, and trace summaries. Inspect its current schema and scope queries to the target account, Worker, and time window. See [Observability](https://developers.cloudflare.com/workers/observability/). |
| Other production tools | If connected, the optional [Workers Observability MCP server](https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/workers-observability) provides `observability_keys`, `observability_values`, and `query_worker_observability`. For live logs use [`wrangler tail`](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/). [Workers Traces](https://developers.cloudflare.com/workers/observability/traces/) covers trace inspection, enablement, and sampling; check discovered tool schemas for the trace detail they expose. |
| Test deployed changes | Use the [Wrangler skill's preview guidance](../wrangler/SKILL.md#preview-deployments) to discover supported deployment commands and resource configuration. |

If the Explorer hint is absent, try `/cdn-cgi/local/explorer/api` on the actual dev origin. If Explorer or telemetry operations are unavailable, check the installed version against the docs and use existing logs or tests as appropriate.

A locally executing Worker can use remote bindings. Explorer's local data browser does not show those remote resources. Likewise, a preview URL does not establish data isolation: inspect its binding targets before testing writes.
