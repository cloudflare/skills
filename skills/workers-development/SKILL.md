---
name: workers-development
description: Run, inspect, and debug Cloudflare Workers during local development with cf dev, wrangler dev, or the Cloudflare Vite plugin, using Local Explorer to read and seed binding data and query local traces and logs. Also routes production debugging to Workers observability. Use for debugging requests whether or not the project uses Wrangler.
---

# Workers development and debugging

Use the project's existing tooling, scripts, and configuration. Installed help, the Local Explorer API schema, and current docs describe the supported operations; read them rather than guessing endpoints or flags.

| Need | Tools and discovery |
| --- | --- |
| Run locally | Use the project's existing dev command: `cf dev` in a `cf` project, otherwise the Wrangler or Cloudflare Vite dev script. See [local development](https://developers.cloudflare.com/workers/local-development/index.md). |
| Inspect or seed local binding data | [Local Explorer](https://developers.cloudflare.com/workers/local-development/local-explorer/index.md) is a UI and API for local KV, R2, D1, SQLite-backed Durable Objects, and Workflows, and can trigger Cron handlers. Open `/cdn-cgi/local/explorer` on the dev server's origin. |
| Debug local requests | Local Explorer captures traces and logs from every local invocation, including binding operations, without code changes. Check traces before adding logging. |
| Debug a deployed Worker | Choose logs, traces, or metrics with [Workers observability](https://developers.cloudflare.com/workers/observability/index.md), or the `cloudflare` skill's observability reference when installed. If the Cloudflare MCP server is connected (bundled with this plugin), use `search` to find the [Workers Observability API](https://developers.cloudflare.com/api/resources/workers/subresources/observability/index.md) operations, then `execute` to call them, scoped to the target account, Worker, and time window. |

## Use the Local Explorer API

When the dev server detects an AI agent, including under `cf dev`, it prints a hint with the API URL and relevant endpoints. Fetch the OpenAPI specification from `/cdn-cgi/local/explorer/api` on the dev server's origin, then extract only the operations the task needs. If no hint appears, request that URL directly. If the API or an operation is missing, compare the installed Wrangler or Vite plugin version against the requirements in the Local Explorer docs.

Bindings are simulated locally by default, but a binding set to `remote: true` reaches the real deployed resource while the Worker runs locally. Traces also capture those remote calls. Identify which bindings are remote before seeding or writing data.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
