---
name: dynamic-workers
description: "Build and review Cloudflare Dynamic Workers and Worker Loader integrations. Load when a task involves runtime-loaded Workers, AI-generated or untrusted code execution, Code Mode, worker_loaders bindings, dynamic workflows, custom sandbox bindings, egress control, Tail Worker observability, or Durable Object facets. Retrieve current Cloudflare docs before exact APIs, limits, pricing, or beta status."
---

# Cloudflare Dynamic Workers

Dynamic Workers let a Worker load isolated Worker code at runtime. Use them for lightweight generated-code execution and per-user or per-tenant dynamic logic; use Sandbox SDK or Containers when the workload needs a filesystem, processes, package installation, or longer-lived runtime isolation.

## Retrieval Sources

Prefer current sources before exact API shapes, config fields, limits, or pricing:

| Topic | URL |
| --- | --- |
| Overview | https://developers.cloudflare.com/dynamic-workers/ |
| Getting started | https://developers.cloudflare.com/dynamic-workers/getting-started/ |
| API reference | https://developers.cloudflare.com/dynamic-workers/api-reference/ |
| Custom bindings | https://developers.cloudflare.com/dynamic-workers/usage/bindings/ |
| Egress control | https://developers.cloudflare.com/dynamic-workers/usage/egress-control/ |
| Observability | https://developers.cloudflare.com/dynamic-workers/usage/observability/ |
| Durable Object facets | https://developers.cloudflare.com/dynamic-workers/usage/durable-object-facets/ |
| Dynamic Workflows | https://developers.cloudflare.com/dynamic-workers/usage/dynamic-workflows/ |

## Workflow

1. Decide whether Dynamic Workers are the right primitive:
   - One-off AI-generated JavaScript tool execution: Dynamic Workers fit well.
   - Persistent Linux processes, filesystem-heavy tools, package installs, or shell execution: prefer Sandbox SDK or Containers.
   - Customer-uploaded Worker scripts at platform scale: compare Workers for Platforms.
2. Inspect `wrangler.*`, generated types, compatibility date/flags, package versions, and existing service bindings.
3. Add a Worker Loader binding and run `npx wrangler types`.
4. Build a `WorkerCode` object with explicit `compatibilityDate`, `mainModule`, and `modules`.
5. Choose `load()` for fresh one-off code or `get(id, callback)` for cacheable code versions.
6. Lock down egress and bindings before running untrusted code.
7. Add Tail Worker or application logs for generated-code output and errors.
8. Validate with local tests where possible, then deployed smoke tests for loader behavior.

## Binding Pattern

```jsonc
{
  "worker_loaders": [
    { "binding": "LOADER" }
  ]
}
```

Use generated `Env` types. Do not invent Worker Loader or `WorkerCode` interfaces by hand.

## Loading Strategy

- Use `env.LOADER.load(code)` when every execution is fresh, such as one-off AI-generated tool calls.
- Use `env.LOADER.get(id, callback)` when code can be cached by a stable identity.
- Make `get()` IDs deterministic and versioned. Use a version number or a hash of code plus config. If code, compatibility flags, bindings, or limits change, use a new ID.
- Do not rely on the same ID always returning the same isolate. Dynamic Workers may start fresh even for the same ID.
- For one-off AI-generated code, prefer JavaScript. Dynamic Workers support Python, but current docs warn that Python startup is much slower.

## Egress And Capability Design

Raw Dynamic Workers are not automatically safe. Design their capabilities deliberately:

- If `globalOutbound` is omitted, the dynamic Worker inherits the parent network access, which usually means public Internet access.
- Set `globalOutbound: null` to block `fetch()` and `connect()` completely.
- Prefer the secure pattern: block global outbound, then provide only specific capabilities through `env` bindings.
- Use service bindings or `ctx.exports` to expose narrow RPC APIs to the dynamic Worker.
- Use a gateway `WorkerEntrypoint` as `globalOutbound` when outbound HTTP/TCP must be allowed but inspected, restricted, credential-injected, or audited.
- Never expose raw secrets to generated code. Inject credentials in a gateway or host-side binding.

## Durable Object Facets

Use facets when dynamically loaded code needs isolated persistent state attached to a supervising Durable Object.

- Treat each facet as its own storage and execution boundary.
- Let the parent Durable Object supervise lifecycle, naming, deletion, and recovery.
- Retrieve current facet APIs before implementing; this area changes quickly.

## Observability

- Add Tail Workers when generated code needs structured log capture, audit trails, or error forwarding.
- Include dynamic worker ID, code version/hash, tenant/user, and request ID in logs.
- Track usage in current dashboard or GraphQL Analytics surfaces before making pricing or quota claims.

## Gotchas

- Dynamic Workers execute code, but they are not a full OS sandbox. Use Sandbox SDK or Containers for shell/process/filesystem workloads.
- `globalOutbound: null` is the safest default for untrusted or AI-generated code. If you allow outbound access, explain exactly what is allowed and why.
- `WorkerCode.env` must contain structured-cloneable values or service bindings.
- Avoid non-deterministic code callbacks for the same `get()` ID.
- Generated code should have input validation, timeouts, and explicit output size limits.
- Dynamic Workflows combine two fast-moving products. Load `workflows` too and retrieve both docs before implementing.
