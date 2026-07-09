# Dynamic Workers

Dynamic Workers spin up Workers at runtime to execute source code on demand in V8 isolates. Use them when code is supplied at runtime, especially AI-generated or user-provided code that needs fast isolated execution.

Keep this file as a routing and retrieval map. Do not copy API signatures, pricing, limits, compatibility dates, setup examples, or generated template code here; those details drift and must come from the current Cloudflare docs.

## Official Documentation

Start with the docs index, then retrieve only the page that matches the user's task.

- Docs index for agents: https://developers.cloudflare.com/dynamic-workers/llms.txt
- Full docs bundle for agents: https://developers.cloudflare.com/dynamic-workers/llms-full.txt
- Product overview: https://developers.cloudflare.com/dynamic-workers/index.md
- Getting started and Worker Loader setup: https://developers.cloudflare.com/dynamic-workers/getting-started/index.md
- API reference for `load`, `get`, and `WorkerCode`: https://developers.cloudflare.com/dynamic-workers/api-reference/index.md
- Bindings and capability exposure: https://developers.cloudflare.com/dynamic-workers/usage/bindings/index.md
- Egress control and `globalOutbound`: https://developers.cloudflare.com/dynamic-workers/usage/egress-control/index.md
- Custom limits: https://developers.cloudflare.com/dynamic-workers/usage/limits/index.md
- Observability and Tail Workers: https://developers.cloudflare.com/dynamic-workers/usage/observability/index.md
- Pricing: https://developers.cloudflare.com/dynamic-workers/pricing/index.md
- Examples: https://developers.cloudflare.com/dynamic-workers/examples/dynamic-workers-starter/index.md

## Quick Routing

- Dynamic Workers: source strings arrive at runtime and should execute quickly in a Worker isolate.
- Workers for Platforms: tenants deploy durable/versioned Workers you manage as platform assets.
- Sandbox: workloads need a full OS, filesystem, packages, long-running processes, or container behavior.

## Stable Answer Anchors

- One-shot generated source: retrieve the current API docs, then use `env.LOADER.load` with a `WorkerCode` object containing `mainModule` and `modules`. Mention `globalOutbound` when discussing egress.
- Repeated unchanged programs: retrieve the current API docs, then use `env.LOADER.get(id, callback)`. Choose a stable ID such as a version or content hash. Warm/cached isolate reuse is best effort; in-memory state is ephemeral and not durable.
- Untrusted source: start with `globalOutbound: null`, expose only narrow bindings/RPC capabilities, do not expose raw secrets, and use external storage such as Durable Objects, R2, or D1 for persistence.

## Drift Boundary

Safe to keep local:

- Product routing: when to choose Dynamic Workers instead of Workers for Platforms or Sandbox.
- Retrieval order: docs index first, then task-specific docs.
- Stable product vocabulary: Worker Loader binding, `load`, `get`, `WorkerCode`, bindings, egress control, limits, observability.

Always retrieve from docs before answering:

- Exact `wrangler` configuration fields, binding shapes, API signatures, module formats, language support, examples, limits, pricing, account requirements, compatibility flags, and release timing.

## Retrieval Checklist

When answering, retrieve the current docs and confirm only what the user needs:

- `worker_loaders` binding shape and binding name.
- `env.LOADER.load(code)` for fresh one-shot execution.
- `env.LOADER.get(id, callback)` for same-code reuse.
- `WorkerCode` fields such as `mainModule`, `modules`, `globalOutbound`, `env`, `tails`, and `limits`.
- Supported languages and bundling requirements.
