# Cloudflare Wrangler

Use Wrangler for Worker development, deployment, and resource management. Retrieve current docs before writing commands or configuration; use the Cloudflare MCP `docs` tool if available, or fetch the linked page directly.

Inspect the project's package scripts, installed Wrangler version, and active config first. Use project-local command help and `wrangler/config-schema.json` to check features against that version; do not silently upgrade to match the latest docs. If retrieval fails, state the gap and use local evidence rather than inventing syntax.

| Task | Read |
| --- | --- |
| Install or update Wrangler | [Installation guide](https://developers.cloudflare.com/workers/wrangler/install-and-update/) |
| Find command flags or manage resources | [Command reference](https://developers.cloudflare.com/workers/wrangler/commands/), then the relevant command page and project-local command help |
| Edit bindings, routes, or environments | [Configuration](./configuration.md) |
| Choose a testing or programmatic API | [API and testing](./api.md) |
| Create, develop, or deploy a Worker | [Workflows](./patterns.md) |
| Diagnose failures or check limits | [Troubleshooting](./gotchas.md) |

Establish the target account, Worker, environment, and resource before mutations. For data operations and development bindings, distinguish local state from remote resources.
