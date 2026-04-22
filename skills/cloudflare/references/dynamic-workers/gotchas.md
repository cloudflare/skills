# Gotchas & Best Practices

Retrieve current pricing, plan availability, and platform limits from the official docs before citing specific numbers. Those details change more often than the behavioral guidance in this file.

## Common Errors

### Dynamic Worker returns an error or empty response

**Cause**: `mainModule` doesn't match a key in `modules`, or the module doesn't have a default export with `fetch()`.
**Solution**: Ensure `mainModule` is an exact key in the `modules` object and the code exports a `fetch` handler.

```typescript
// ❌ BAD: mainModule doesn't match
env.LOADER.load({
  mainModule: "index.js",
  modules: { "worker.js": code } // Key mismatch
});

// ✅ GOOD: mainModule matches modules key
env.LOADER.load({
  mainModule: "worker.js",
  modules: { "worker.js": code }
});
```

### `fetch()` or `connect()` throws an exception in Dynamic Worker

**Cause**: `globalOutbound` is set to `null`, which blocks all outbound network access. Any `fetch()` or `connect()` call will throw.
**Solution**: If the Dynamic Worker needs network access, either omit `globalOutbound` (inherits parent's access) or provide a gateway `ServiceStub`.

### Callback returning different code for the same ID

**Cause**: Using `get(id, callback)` where the callback returns different content across invocations for the same ID.
**Solution**: The callback must always return identical content for a given ID. Use content-hashed IDs if code varies:

```typescript
// ❌ BAD: Same ID, potentially different code
env.LOADER.get("my-worker", async () => {
  const code = await fetchLatestCode(); // May change!
  return { modules: { "index.js": code }, /* ... */ };
});

// ✅ GOOD: ID derived from content hash
const hash = await hashCode(code);
env.LOADER.get(`worker-${hash}`, async () => {
  return { modules: { "index.js": code }, /* ... */ };
});
```

### Standard bindings (KV, R2, D1) not working in Dynamic Worker

**Cause**: Passing standard Workers bindings directly via `env` is [not currently supported](https://developers.cloudflare.com/dynamic-workers/usage/bindings/). Dynamic Workers use capability-based security via Workers RPC.
**Solution**: Create a wrapper RPC interface using `WorkerEntrypoint` classes and pass as stubs (see [api.md](./api.md)). This also lets you narrow scope, filter requests, etc.

### Props not serializable

**Cause**: Passing functions or non-clonable objects via `ctx.props`.
**Solution**: `ctx.props` values must be structured-clonable (strings, numbers, plain objects, arrays). No functions, classes, or circular references.

### Python code runs slowly

**Cause**: Python isolates have significantly slower startup than JavaScript.
**Solution**: Use JavaScript or TypeScript (via bundler) for AI-generated code. Reserve Python for cases where it's strictly necessary.

### Tail Worker logs not appearing

**Cause**: Tail Workers run asynchronously after the response is sent. If you return immediately, logs may not have arrived yet.
**Solution**: Use the Durable Object log session pattern (see [patterns.md](./patterns.md)) to wait for logs before responding, or accept that logs arrive asynchronously.

### RPC methods executing in different isolates

**Cause**: There is [no guarantee](https://developers.cloudflare.com/dynamic-workers/api-reference/) that two requests go to the same isolate, even with the same `WorkerStub` or the same ID via `get()`. Only stubs returned from the same RPC method call share a session.
**Solution**: Do not rely on in-memory state persisting across requests. Pass state explicitly (via RPC arguments, Durable Objects, or KV). `get()` with a stable ID improves the *likelihood* of hitting a warm isolate but does not guarantee it.

## Best Practices

### Use `load()` for one-shot, `get()` for repeated

```typescript
// One-shot AI code execution — use load()
const worker = env.LOADER.load({ /* ... */ });

// App receiving multiple requests — use get() with stable ID
const worker = env.LOADER.get("app-v1", async () => { /* ... */ });
```

### Content-hash your worker IDs

Derive IDs from the code content so identical code reuses the same warm isolate:

```typescript
async function workerId(files: Record<string, string>): Promise<string> {
  const sorted = Object.entries(files).sort();
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(JSON.stringify(sorted))
  );
  return "worker-" + Array.from(new Uint8Array(digest), (b) =>
    b.toString(16).padStart(2, "0")
  ).join("").slice(0, 16);
}
```

### Block network by default

Use `globalOutbound: null` unless the Dynamic Worker genuinely needs network access. When it does, use a gateway to filter and inject credentials rather than passing raw tokens.

### Set explicit runtime limits

Use `limits` to bound CPU time and subrequests for untrusted or AI-generated code. Choose values that fit the task rather than inheriting the parent Worker's full budget.

```typescript
const worker = env.LOADER.load({
  compatibilityDate: "$today",
  mainModule: "worker.js",
  modules: { "worker.js": code },
  globalOutbound: null,
  limits: { cpuMs: 50, subRequests: 20 }
});
```

### Cold-start warmup

You can trigger isolate initialization before the real request by calling a method that forces the isolate to load. This pattern is used in [Cloudflare's playground example](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground) but is not a documented API:

```typescript
const entrypoint = worker.getEntrypoint();
try {
  await entrypoint.__warmup__?.();
} catch {
  // Intentional — the method doesn't exist, but the isolate is now warm
}
```

## Retrieve Current Pricing and Limits

- Use the [Pricing docs](https://developers.cloudflare.com/dynamic-workers/pricing/) for current plan availability, billing dimensions, and whether any pricing component is active yet.
- Use the [Custom Limits docs](https://developers.cloudflare.com/dynamic-workers/usage/limits/) for current limit controls and ceilings.
- Use the [Workers platform limits docs](https://developers.cloudflare.com/workers/platform/limits/) when you need current runtime ceilings.
- Prefer describing cost behavior qualitatively in the skill: `load()` creates fresh Workers, while `get()` can reuse a stable ID and usually fits repeated traffic better.

## Starter Templates

- [Dynamic Workers Starter](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers) — Minimal `load()` example
- [Dynamic Workers Playground](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground) — Full IDE with bundling, caching, and real-time logs
- [Codemode](https://github.com/cloudflare/agents/tree/main/examples/codemode) — AI agent code execution with tools
- [Codemode MCP](https://github.com/cloudflare/agents/tree/main/examples/codemode-mcp) — Wrap MCP server into single code tool
- [Codemode MCP OpenAPI](https://github.com/cloudflare/agents/tree/main/examples/codemode-mcp-openapi) — OpenAPI spec → MCP code tool
- [Worker Bundler Playground](https://github.com/cloudflare/agents/tree/main/examples/worker-bundler-playground) — AI-generated full-stack apps

## Resources

- [Official Docs](https://developers.cloudflare.com/dynamic-workers/)
- [Getting Started](https://developers.cloudflare.com/dynamic-workers/getting-started/)
- [Bindings (Cap'n Web)](https://developers.cloudflare.com/dynamic-workers/usage/bindings/)
- [Custom Limits](https://developers.cloudflare.com/dynamic-workers/usage/limits/)
- [Egress Control](https://developers.cloudflare.com/dynamic-workers/usage/egress-control/)
- [Observability](https://developers.cloudflare.com/dynamic-workers/usage/observability/)
- [Pricing](https://developers.cloudflare.com/dynamic-workers/pricing/)
- [API Reference](https://developers.cloudflare.com/dynamic-workers/api-reference/)
- [Blog Post](https://blog.cloudflare.com/dynamic-workers/)
- [LLM Reference](https://developers.cloudflare.com/dynamic-workers/llms-full.txt)
