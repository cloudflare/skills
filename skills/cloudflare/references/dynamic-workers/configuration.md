# Configuration

## Worker Loader Binding

The `worker_loaders` binding gives your Worker access to the Dynamic Worker Loader API.

**wrangler.jsonc**:
```jsonc
{
  "name": "my-loader",
  "main": "src/index.ts",
  "compatibility_date": "2026-01-28",
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
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["LogSession"] }]
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

For structured real-time logs, use Tail Workers with a Durable Object log session (see [patterns.md](./patterns.md)).

## Supported Languages

| Language | Module Type | Notes |
|----------|-------------|-------|
| JavaScript (ES modules) | `{js: string}` or `.js` string | Recommended. Fastest startup. |
| JavaScript (CommonJS) | `{cjs: string}` | Use for `require()`-style modules |
| Python | `{py: string}` or `.py` string | Significantly slower startup than JS |
| TypeScript | Requires bundling | Use `@cloudflare/worker-bundler` to compile before loading |

### TypeScript and npm Dependencies

TypeScript cannot be passed directly to the loader. Use `@cloudflare/worker-bundler` to transpile and resolve dependencies at runtime:

```typescript
import { createWorker } from "@cloudflare/worker-bundler";

const { mainModule, modules } = await createWorker({
  files: {
    "src/index.ts": typescriptCode,
    "package.json": JSON.stringify({
      dependencies: { hono: "^4.0.0" }
    })
  },
  bundle: true,
  minify: false
});

const worker = env.LOADER.load({
  mainModule,
  modules: modules as Record<string, string>,
  compatibilityDate: "2026-01-28"
});
```

`createWorker()` returns:
- `mainModule`: Entry point filename
- `modules`: Bundled module map
- `wranglerConfig`: Parsed config from the files (if a `wrangler.jsonc` was included)
- `warnings`: Build warnings

## Compatibility Date and Flags

```typescript
env.LOADER.load({
  compatibilityDate: "2026-01-28",       // Required
  compatibilityFlags: ["nodejs_compat"],  // Optional
  allowExperimental: true,                // Optional — parent must have "experimental" flag
  // ...
});
```

The `compatibilityDate` on the Dynamic Worker is independent of the loader Worker's date. Set it to match the code you're executing.

## CLI Commands

```bash
wrangler dev              # Local development
wrangler deploy           # Deploy loader Worker
wrangler tail             # Stream real-time logs
```

Dynamic Workers are created at runtime — there are no separate deploy or management commands for them.
