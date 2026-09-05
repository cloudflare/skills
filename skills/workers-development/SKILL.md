---
name: workers-development
description: Find tools for running, inspecting, and debugging Cloudflare Workers locally or in production, and testing deployed changes with previews. Use for Wrangler or Cloudflare Vite development, binding data inspection, and runtime investigation.
---

# Workers Development and Debugging

Use the project's installed tooling, scripts, and configuration as the starting point. Choose the capabilities relevant to the task; installed help, API schemas, and current docs describe their supported operations.

| Need | Tools and discovery |
| --- | --- |
| Run locally | Use the existing Wrangler or Cloudflare Vite dev script. Inspect package scripts, `wrangler --help`, and [local development docs](https://developers.cloudflare.com/workers/local-development/) for available modes. |
| Inspect local binding data | [Local Explorer](https://developers.cloudflare.com/workers/local-development/local-explorer/) provides a UI and API for KV, R2, D1, SQLite Durable Objects, and Workflows. Fetch the OpenAPI schema from the startup hint; it describes data inspection, editing, and Workflow operations. Open the UI with `e` in Wrangler or `/cdn-cgi/local/explorer` on the actual dev origin. |
| Debug local execution | Explorer automatically captures invocation traces and logs, including binding operations. Discover telemetry queries through its API schema; existing traces can reveal failing operations without adding instrumentation. |
| Investigate production | The [Workers Observability MCP server](https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/workers-observability) exposes `observability_keys`, `observability_values`, and `query_worker_observability` for field discovery, logs, metrics, and invocations. If connected, inspect tool schemas and query the relevant Worker and time window. Connection details are in its README. For live logs, see [`wrangler tail`](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/). |
| Inspect production traces | Consult [Workers Traces](https://developers.cloudflare.com/workers/observability/traces/) for trace access, enablement, and sampling. Discover whether connected tools expose spans; log and invocation queries alone do not establish that capability. |
| Test deployed changes | Use the `wrangler` skill's preview guidance to discover supported deployment commands and resource configuration. |

A locally executing Worker can use remote bindings. Explorer's local data browser does not show those remote resources. Likewise, a preview URL does not establish data isolation: inspect its binding targets before testing writes.
