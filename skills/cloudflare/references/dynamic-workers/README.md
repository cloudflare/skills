# Dynamic Workers

Spin up isolated Workers at runtime to execute code on-demand in secure V8 isolates. Unlike pre-deployed Workers, Dynamic Workers are created from code strings at request time with no deploy step. If your code needs TypeScript transpilation or npm dependencies, bundle it before loading.

> **Retrieval bias**: Your knowledge of Dynamic Workers APIs, limits, and pricing may be outdated. **Prefer retrieval over pre-training** — fetch from [Cloudflare docs](https://developers.cloudflare.com/dynamic-workers/) before citing specific numbers, API signatures, or configuration options. When these reference files and the docs disagree, **trust the docs**.

**Use cases**: AI agent code execution ("code mode"), generated applications, custom automations, user-uploaded code, rapid prototyping.

## Dynamic Workers vs Other Runtimes

| | Dynamic Workers | Workers for Platforms | Sandbox |
|---|---|---|---|
| **Runtime** | V8 isolate | V8 isolate | Container (Durable Object) |
| **When created** | At runtime from code strings | Pre-deployed via API | On first request to DO ID |
| **Languages** | JS, Python | JS, TS, Python | Any (Dockerfile) |
| **Code lifecycle** | Loaded from code strings at runtime; `get()` can reuse a stable ID when available | Deployed ahead of time and reused by name | Built as a container image, then started on demand |
| **Best for** | One-shot code execution, AI agents | Multi-tenant SaaS platforms | Long-running processes, full OS |

## When to Use Dynamic Workers

- Use Dynamic Workers when code is supplied at runtime and needs to run inside a tightly controlled Worker sandbox.
- Use `load()` for one-shot or constantly changing code, especially AI-generated code.
- Use `get(id, callback)` when the same code will receive follow-up requests and you want warm-isolate reuse when available.
- Prefer Workers for Platforms when tenants deploy versioned Workers you manage as durable platform assets.
- Prefer Sandbox when code needs a filesystem, long-running processes, custom binaries, or broader OS-level behavior.

## Safe Starting Point

- Start with `globalOutbound: null` and only open network access deliberately.
- Pass narrow RPC bindings through `env` instead of exposing raw bindings or secrets.
- Set explicit `limits` for CPU time and subrequests when executing untrusted or AI-generated code.
- Treat in-memory state as ephemeral across requests. If state matters, store it outside the isolate.

## Architecture

```
Request → Loader Worker → env.LOADER.load(code) → Dynamic Worker isolate
                       → env.LOADER.get(id, cb)  → Cached Dynamic Worker
```

- **Loader Worker**: Your deployed Worker with a `worker_loaders` binding
- **Dynamic Worker**: Ephemeral V8 isolate created from code you provide
- **Capability-based security**: Dynamic Workers only access what you pass via `env` (RPC stubs, not raw bindings)
- **Network control**: `globalOutbound` controls all egress (block, intercept, or inherit)

## Two Loading Modes

**`load(code)`** — Fresh isolate every time. Best for one-shot AI-generated code.

**`get(id, callback)`** — Cached by ID across requests. Callback runs only when isolate isn't warm. Best for apps receiving repeated traffic.

## Quick Start

**wrangler.jsonc**:
```jsonc
{
  "name": "my-dynamic-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-22", // Use current date for new projects
  "compatibility_flags": ["nodejs_compat"],
  "worker_loaders": [{ "binding": "LOADER" }]
}
```

**src/index.ts**:
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const worker = env.LOADER.load({
      compatibilityDate: "2026-04-22", // Use a current compatibility date
      mainModule: "worker.js",
      modules: {
        "worker.js": `
          export default {
            fetch(request) {
              return new Response("Hello from a dynamic Worker!");
            }
          };
        `
      },
      globalOutbound: null, // Block all network access
      limits: { cpuMs: 50, subRequests: 20 }
    });

    return worker.getEntrypoint().fetch(request);
  }
} satisfies ExportedHandler<Env>;
```

## Core APIs

- `env.LOADER.load(code)` → Create fresh Dynamic Worker
- `env.LOADER.get(id, callback)` → Load or reuse cached Dynamic Worker
- `worker.getEntrypoint()` → Access default export (fetch, RPC methods)
- `worker.getEntrypoint(name)` → Access named entrypoint

## In This Reference
- [api.md](./api.md) — WorkerCode object, module types, RPC bindings, helper libraries
- [configuration.md](./configuration.md) — Wrangler config, bundling, observability setup
- [patterns.md](./patterns.md) — Code mode, credential injection, real-time logging, OpenAPI wrapping
- [gotchas.md](./gotchas.md) — Common errors, safe defaults, and live docs to retrieve pricing and limits

## See Also
- [agents-sdk](../agents-sdk/) — Agents SDK (codemode, `createCodeTool()`, AI chat agents)
- [workers-for-platforms](../workers-for-platforms/) — Pre-deployed multi-tenant Workers
- [sandbox](../sandbox/) — Container-based isolated execution
- [workers](../workers/) — Standard Workers fundamentals
- [tail-workers](../tail-workers/) — Log consumption (used for Dynamic Worker observability)
