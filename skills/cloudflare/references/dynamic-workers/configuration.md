# Configuration

## Worker Loader Binding

The `worker_loaders` binding gives your Worker access to the Dynamic Worker Loader API.

**wrangler.jsonc**:
```jsonc
{
  "name": "my-loader",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-22", // Use current date for new projects
  "compatibility_flags": ["nodejs_compat"],
  "worker_loaders": [{ "binding": "LOADER" }]
}
```

**wrangler.toml**:
```toml
[[worker_loaders]]
binding = "LOADER"
```

Access via `env.LOADER` in your Worker code.

## Combining with Other Bindings

Dynamic Workers are typically used alongside other Cloudflare bindings in the **loader** Worker. The Dynamic Worker itself does not receive these bindings directly — you wrap them in RPC entrypoints (see [api.md](./api.md)).

### With Durable Objects (for logging)

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }],
  "durable_objects": {
    "bindings": [{ "class_name": "LogSession", "name": "LogSession" }]
  },
  "migrations": [{ "tag": "v1", "new_classes": ["LogSession"] }]
}
```

### With AI Binding (for code generation)

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }],
  "ai": { "binding": "AI" }
}
```

### With AI + Durable Objects + Assets (full-stack playground)

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }],
  "ai": { "binding": "AI" },
  "durable_objects": {
    "bindings": [{ "class_name": "WorkerPlayground", "name": "WorkerPlayground" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["WorkerPlayground"] }],
  "assets": {
    "directory": "public",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*"]
  }
}
```

## Observability

Enable Workers Logs to see output from both the loader and Dynamic Workers.

**wrangler.jsonc**:
```jsonc
{
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  }
}
```

**wrangler.toml**:
```toml
[observability]
enabled = true
head_sampling_rate = 1
```

For Tail Worker setup and the `tails` property, see [api.md — Tail Workers](./api.md#tail-workers-observability). For the real-time log streaming pattern using Durable Objects, see [patterns.md — Real-Time Log Streaming](./patterns.md#real-time-log-streaming).

## Custom Limits

Set explicit limits when running untrusted or AI-generated code. This keeps each invocation bounded even if the generated code loops, fans out, or behaves unexpectedly.

```typescript
const worker = env.LOADER.load({
  compatibilityDate: "2026-04-22", // Use a current compatibility date
  mainModule: "worker.js",
  modules: { "worker.js": code },
  globalOutbound: null,
  limits: { cpuMs: 50, subRequests: 20 }
});

const entrypoint = worker.getEntrypoint(null, {
  limits: { cpuMs: 10, subRequests: 5 }
});
```

Retrieve current maximum values and behavior from the [Custom Limits docs](https://developers.cloudflare.com/dynamic-workers/usage/limits/) before citing specific ceilings.

## Supported Languages

| Language | Module Type | Notes |
|----------|-------------|-------|
| JavaScript (ES modules) | `{js: string}` or `.js` string | Recommended. Fastest startup. |
| JavaScript (CommonJS) | `{cjs: string}` | Use for `require()`-style modules |
| Python | `{py: string}` or `.py` string | Significantly slower startup than JS |
| TypeScript | Requires bundling | Use `@cloudflare/worker-bundler` to compile before loading |

### Non-Code Module Types

You can also include non-code modules in the `modules` object (see [api.md — WorkerCode](./api.md#workercode-object)):

| Type | Syntax | Use |
|------|--------|-----|
| `{text: string}` | Importable string value | Config files, templates |
| `{data: ArrayBuffer}` | Importable binary data | Wasm modules, images |
| `{json: object}` | Importable JSON-serializable object | Structured config, manifests |

### TypeScript and npm Dependencies

TypeScript cannot be passed directly to the loader. Use `@cloudflare/worker-bundler` to transpile and resolve dependencies at runtime:

```typescript
import { createWorker } from "@cloudflare/worker-bundler";

const { mainModule, modules } = await createWorker({
  files: {
    "src/index.ts": typescriptCode,
    "package.json": JSON.stringify({
      dependencies: { hono: "^4" }
    })
  },
  bundle: true,
  minify: false
});

const worker = env.LOADER.load({
  mainModule,
  modules: modules as Record<string, string>,
  compatibilityDate: "2026-04-22" // Use a current compatibility date
});
```

`createWorker()` returns (based on [official examples](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground)):
- `mainModule`: Entry point filename
- `modules`: Bundled module map
- `wranglerConfig`: Parsed config from the files (if a `wrangler.jsonc` was included)
- `warnings`: Build warnings

See the [@cloudflare/worker-bundler npm package](https://www.npmjs.com/package/@cloudflare/worker-bundler) for the latest API surface.

## Compatibility Date and Flags

```typescript
env.LOADER.load({
  compatibilityDate: "2026-04-22",      // Required. Use current date for new projects.
  compatibilityFlags: ["nodejs_compat"],  // Optional
  allowExperimental: true,                // Optional — parent must have "experimental" flag
  // ...
});
```

## CLI Commands

```bash
wrangler dev              # Local development (uses local runtime)
wrangler deploy           # Deploy loader Worker
wrangler tail             # Stream real-time logs
```

Dynamic Workers are created at runtime — there are no separate deploy or management commands for them.

**Local development**: `wrangler dev` runs the loader Worker locally. Dynamic Workers execute in the local runtime during development. Behavior may differ from production — test with `wrangler deploy` to a staging Worker before relying on production-only features. Check the [official docs](https://developers.cloudflare.com/dynamic-workers/) for current local dev support status.
