# Dynamic Workers

Spin up isolated Workers at runtime to execute code on-demand in secure V8 isolates. Unlike pre-deployed Workers, Dynamic Workers are created from code strings at request time — no build step, no deploy.

**Use cases**: AI agent code execution ("code mode"), generated applications, custom automations, user-uploaded code, rapid prototyping.

## Dynamic Workers vs Other Runtimes

| | Dynamic Workers | Workers for Platforms | Sandbox |
|---|---|---|---|
| **Runtime** | V8 isolate | V8 isolate | Container (Durable Object) |
| **When created** | At runtime from code strings | Pre-deployed via API | On first request to DO ID |
| **Startup** | Milliseconds | Already deployed | 2-3s cold start |
| **Languages** | JS, Python | JS, TS, Python, Rust, Wasm | Any (Dockerfile) |
| **State** | Ephemeral per invocation | Persistent (deployed script) | Ephemeral disk (lost on sleep); use R2 mounts for persistence |
| **Best for** | One-shot code execution, AI agents | Multi-tenant SaaS platforms | Long-running processes, full OS |

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
  "compatibility_date": "2026-01-28",
  "compatibility_flags": ["nodejs_compat"],
  "worker_loaders": [{ "binding": "LOADER" }]
}
```

**src/index.ts**:
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const worker = env.LOADER.load({
      compatibilityDate: "2026-01-28",
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
      globalOutbound: null // Block all network access
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
- [gotchas.md](./gotchas.md) — Limits, pricing, common errors, best practices

## See Also
- [workers-for-platforms](../workers-for-platforms/) — Pre-deployed multi-tenant Workers
- [sandbox](../sandbox/) — Container-based isolated execution
- [workers](../workers/) — Standard Workers fundamentals
- [tail-workers](../tail-workers/) — Log consumption (used for Dynamic Worker observability)
