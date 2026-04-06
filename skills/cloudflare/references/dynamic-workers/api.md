# API Reference

## Loading Dynamic Workers

### `env.LOADER.load(code: WorkerCode): WorkerStub`

Creates a fresh Dynamic Worker. No caching — each call creates a new isolate.

```typescript
const worker = env.LOADER.load({
  compatibilityDate: "2026-01-28",
  mainModule: "worker.js",
  modules: { "worker.js": code },
  globalOutbound: null
});

const response = await worker.getEntrypoint().fetch(request);
```

### `env.LOADER.get(id: string, callback: () => Promise<WorkerCode>): WorkerStub`

Loads or retrieves a cached Dynamic Worker by ID. The callback executes only if the Worker isn't already warm. Returns synchronously; requests queue if the Worker is still loading.

```typescript
const worker = env.LOADER.get("hello-v1", async () => {
  const code = await env.MY_CODE_STORAGE.get("hello-v1");
  return {
    compatibilityDate: "2026-01-28",
    mainModule: "index.js",
    modules: { "index.js": code },
    globalOutbound: null
  };
});
```

**Critical**: The callback must always return the same content for the same ID. Different code for the same ID breaks caching guarantees.

### `WorkerStub.getEntrypoint(): object`

Access the Dynamic Worker's `export default`. Returns an object you can call `fetch()` or RPC methods on.

### `WorkerStub.getEntrypoint(name: string): object`

Access a named entrypoint (a named `WorkerEntrypoint` export from the Dynamic Worker).

## WorkerCode Object

### Required Properties

**`compatibilityDate`** (string) — Sets the Worker runtime version (e.g. `"2026-01-28"`).

**`mainModule`** (string) — Name of the entry module. Must exist as a key in `modules`.

**`modules`** (Record<string, string | Module>) — Dictionary mapping filenames to code. String values require `.js` or `.py` extensions. Object values specify the module type:

| Type | Syntax | Use |
|------|--------|-----|
| `{js: string}` | ES module (`import`/`export`) | Default for `.js` strings |
| `{cjs: string}` | CommonJS (`require()`) | Legacy modules |
| `{py: string}` | Python | Slower startup than JS |
| `{text: string}` | Importable string value | Config, templates |
| `{data: ArrayBuffer}` | Binary data | Wasm, images |
| `{json: object}` | JSON-serializable object | Structured config |

### Optional Properties

**`compatibilityFlags`** (string[]) — Compatibility flags augmenting the date.

**`allowExperimental`** (boolean) — Permit experimental flags. Parent Worker must have the `"experimental"` flag set.

**`globalOutbound`** (ServiceStub | null) — Controls network egress:
- **Omitted**: Inherits parent Worker's network access
- **`null`**: Blocks all `fetch()` and `connect()` (throws on attempt)
- **ServiceStub**: Routes all network requests through a custom gateway

**`env`** (object) — Environment passed to the Dynamic Worker. Supports:
- Structured-clonable types (strings, numbers, objects, arrays)
- Service Bindings (RPC stubs from `ctx.exports`)
- Loopback bindings (the loader's own entrypoints)

**`tails`** (ServiceStub[]) — Tail Workers that receive logs and metadata after execution.

## Custom Bindings via RPC (Cap'n Web)

Passing standard Workers bindings (KV, R2, D1, etc.) directly into a Dynamic Worker is [not currently supported](https://developers.cloudflare.com/dynamic-workers/usage/bindings/). Instead, create wrapper RPC interfaces using `WorkerEntrypoint` classes and pass them as stubs.

This uses [Cap'n Web](https://developers.cloudflare.com/dynamic-workers/usage/bindings/) (Workers RPC) — a capability-based security model. Objects passed over RPC are stubs: if you haven't received a stub, you can't call the object. There's no global identifier to guess. This is why Dynamic Workers are secure by default — the sandbox can only access what you explicitly grant it, and you can narrow scope, filter requests, or inject credentials at the boundary.

### Define in Loader Worker

```typescript
import { WorkerEntrypoint } from "cloudflare:workers";

export class ChatRoom extends WorkerEntrypoint<Cloudflare.Env, ChatRoomProps> {
  async post(text: string): Promise<void> {
    const { apiKey, botName, roomName } = this.ctx.props;
    text = `[${botName}]: ${text}`;
    await postToChat(apiKey, roomName, text);
  }
}

type ChatRoomProps = {
  apiKey: string;
  roomName: string;
  botName: string;
};
```

### Pass to Dynamic Worker

```typescript
const chatRoom = ctx.exports.ChatRoom({
  props: { apiKey, botName: "Robo", roomName: "#bot-chat" }
});

const worker = env.LOADER.load({
  env: { CHAT_ROOM: chatRoom },
  compatibilityDate: "2026-01-28",
  mainModule: "index.js",
  modules: { "index.js": codeFromAgent },
  globalOutbound: null
});

return worker.getEntrypoint("Agent").run();
```

The Dynamic Worker accesses `this.env.CHAT_ROOM.post(text)` without seeing secrets.

## Network Access Control (globalOutbound)

### Block All Egress

```typescript
globalOutbound: null
// Any fetch() or connect() in the Dynamic Worker throws
```

### Intercept Requests via Gateway

```typescript
export class HttpGateway extends WorkerEntrypoint {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    // Inspect, modify, block, or forward
    return fetch(request);
  }
}

// In loader:
globalOutbound: ctx.exports.HttpGateway()
```

### Inject Credentials

```typescript
export class HttpGateway extends WorkerEntrypoint {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const headers = new Headers(request.headers);

    if (url.hostname === "api.example.com") {
      headers.set("Authorization", `Bearer ${this.env.API_TOKEN}`);
      headers.set("X-Tenant-Id", this.ctx.props.tenantId);
    }

    return fetch(request, { headers });
  }
}

// Pass with props:
globalOutbound: ctx.exports.HttpGateway({ props: { tenantId } })
```

## Helper Libraries

### `@cloudflare/worker-bundler`

Bundles TypeScript and npm dependencies before passing to the loader. Handles transpilation, dependency resolution, and module output.

```typescript
import { createWorker } from "@cloudflare/worker-bundler";

const worker = env.LOADER.get("my-worker", async () => {
  const { mainModule, modules, wranglerConfig, warnings } = await createWorker({
    files: {
      "src/index.ts": `
        import { Hono } from 'hono';
        const app = new Hono();
        app.get('/', (c) => c.text('Hello from Hono!'));
        export default app;
      `,
      "package.json": JSON.stringify({
        dependencies: { hono: "^4.0.0" }
      })
    },
    bundle: true,
    minify: false
  });

  return {
    mainModule,
    modules: modules as Record<string, string>,
    compatibilityDate: wranglerConfig?.compatibilityDate ?? "2026-01-01",
    compatibilityFlags: wranglerConfig?.compatibilityFlags ?? []
  };
});
```

### `@cloudflare/codemode`

Replace individual tool calls with a single `code()` tool, so LLMs write and execute TypeScript that orchestrates multiple API calls in one pass. Provides `DynamicWorkerExecutor` and `createCodeTool()`.

Key exports:
- `@cloudflare/codemode` — `DynamicWorkerExecutor` class
- `@cloudflare/codemode/ai` — `createCodeTool()` function
- `@cloudflare/codemode/mcp` — `codeMcpServer()` and `openApiMcpServer()` wrappers

The `DynamicWorkerExecutor` implements the generic [`Executor` interface](https://developers.cloudflare.com/agents/api-reference/codemode/) — you can implement your own `Executor` to run code in a different sandbox (e.g., containers, external services) while reusing `createCodeTool()` and the MCP wrappers.

See the [Code Mode documentation](https://developers.cloudflare.com/agents/api-reference/codemode/) for full API reference.

### `@cloudflare/shell`

Give your agent a virtual filesystem inside a Dynamic Worker with persistent storage backed by SQLite and R2.

See [npm package](https://www.npmjs.com/package/@cloudflare/shell) for current API surface.

## Tail Workers (Observability)

Attach Tail Workers via the `tails` property to capture `console.log()`, exceptions, and request metadata.

### Define Tail Worker

```typescript
import { WorkerEntrypoint } from "cloudflare:workers";

export class DynamicWorkerTail extends WorkerEntrypoint {
  async tail(events: TraceItem[]) {
    for (const event of events) {
      for (const log of event.logs) {
        console.log({
          source: "dynamic-worker-tail",
          workerId: this.ctx.props.workerId,
          level: log.level,
          message: log.message
        });
      }
    }
  }
}
```

### Attach to Dynamic Worker

```typescript
const worker = env.LOADER.get(workerId, () => ({
  mainModule: "index.js",
  modules: { "index.js": code },
  compatibilityDate: "2026-01-28",
  tails: [
    ctx.exports.DynamicWorkerTail({ props: { workerId } })
  ]
}));
```

Tail Workers run asynchronously after the response is sent — they cannot affect the request-response cycle.
