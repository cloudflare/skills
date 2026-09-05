---
description: Guidance for writing, reviewing, or configuring Cloudflare Workers and applications deployed to Workers.
alwaysApply: false
---

# Cloudflare Workers

Your knowledge of Cloudflare Workers APIs, types, and configuration may be outdated. **Prefer retrieval over pre-training.** Use the project's installed versions, generated types, and compatibility settings as the baseline. Retrieve relevant Cloudflare documentation to verify API, configuration, runtime behavior, and limit claims.

## Workers Defaults

- **Keep compatibility dates current.** Use today's date for new Workers. Encourage periodic updates for existing Workers, reviewing compatibility changes and running relevant tests.
- **Enable logs and traces.** When creating or preparing a Worker for production, set `observability.enabled` and `observability.traces.enabled` to `true`. The top-level setting alone does not enable traces. Use structured JSON logging and configure sampling for the workload. During reviews, flag missing logs or traces. See [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) and [Traces](https://developers.cloudflare.com/workers/observability/traces/).
- **Keep binding types in sync.** Run `wrangler types` after changing bindings in the project's Wrangler configuration, whether JSONC, JSON, or TOML.

## Shared Guidance

- Use [workers-best-practices](../skills/workers-best-practices/SKILL.md) for runtime patterns, anti-patterns, configuration, and platform API checks. Read the references relevant to the task.
- Use [wrangler](../skills/wrangler/SKILL.md) for CLI commands and deployment configuration.
- Find documentation for products used by the Worker in the [Cloudflare docs directory](https://developers.cloudflare.com/directory/). Verify limits and quotas against the affected product's documentation.
