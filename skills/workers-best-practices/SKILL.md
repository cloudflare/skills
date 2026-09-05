---
name: workers-best-practices
description: Write or review Cloudflare Workers runtime code for production reliability. Use wrangler for CLI commands and deployment configuration.
---

Use the project's installed versions, generated types, and Wrangler compatibility settings as the baseline for existing code. Retrieve current Cloudflare sources when the affected API, configuration, runtime behavior, or limit needs verification.

## Retrieval Sources

Consult only the sources needed for the task. A newer published type package does not supersede the project's configured target; distinguish a defect in that target from a possible upgrade.

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Workers best practices | Fetch `https://developers.cloudflare.com/workers/best-practices/workers-best-practices/` | Canonical rules, patterns, anti-patterns |
| Workers types | See `references/review.md` | API signatures, handler types, binding types |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` | Config fields, binding shapes, allowed values |
| Cloudflare docs | Search tool or `https://developers.cloudflare.com/workers/` | API reference, compatibility dates/flags |

## Reference Documentation

- [references/rules.md](references/rules.md) — consult relevant patterns when authoring or assessing affected Workers behavior
- [references/review.md](references/review.md) — Workers-specific type, binding, config, and serialization checks; consult the sections relevant to the task

## Enable Observability

Enable [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) and [Traces](https://developers.cloudflare.com/workers/observability/traces/) when creating or preparing a Worker for production. Set `observability.enabled` and `observability.traces.enabled` to `true`; the top-level setting alone does not enable traces. Use structured JSON logging and configure sampling for the workload. During reviews, flag missing logs or traces. See the [configuration example](references/rules.md#enable-workers-logs-and-traces).

## Workers Pitfalls

| Risk | Guidance |
|------|----------|
| Buffering large or unbounded bodies | Stream request and response bodies; see [streaming patterns](references/rules.md#stream-request-and-response-bodies). |
| Work outliving its request | Await or return required work; attach post-response work to `ctx.waitUntil()`. Keep the `ctx` receiver when calling it. |
| Request state shared across invocations | Keep request-scoped state out of module-level mutable variables. |
| Binding and handler type mismatches | Use generated `Env` types and check affected signatures and binding access against the project's target; see [type checks](references/review.md#type-validation). |
| Payloads crossing API boundaries | Check the specific API's encoding and supported values; see [serialization checks](references/review.md#serialization-boundaries). |

For configuration, service bindings, database connections, and security patterns, consult the relevant sections of [references/rules.md](references/rules.md).

## Validation

Use the project's existing checks for affected Workers behavior: type-check binding or handler contract changes, and run relevant runtime tests for behavior changes. Preserve required repository checks; a narrow edit does not require a full Workers audit.

## Scope

This skill covers Workers-specific best practices and code review. For related topics:

- **Durable Objects**: load the `durable-objects` skill
- **Workflows**: see [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)
- **Wrangler CLI commands**: load the `wrangler` skill
