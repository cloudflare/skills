# Common Patterns

## Basic Code Execution

The simplest pattern: accept code, execute it, return the result.

```typescript
const DEFAULT_CODE = `export default {
  fetch() {
    return new Response("Hello from a dynamic Worker!");
  },
};`;

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "POST") {
      const { code } = await request.json<{ code?: string }>();

      try {
        const worker = env.LOADER.load({
          compatibilityDate: "2026-01-28",
          mainModule: "worker.js",
          modules: { "worker.js": code?.trim() || DEFAULT_CODE },
          globalOutbound: null
        });

        const result = await worker.getEntrypoint().fetch(new Request("https://worker/"));
        const text = await result.text();
        return Response.json({ ok: true, status: result.status, output: text });
      } catch (err) {
        return Response.json(
          { ok: false, error: err instanceof Error ? err.message : String(err) },
          { status: 400 }
        );
      }
    }

    return new Response("Not found", { status: 404 });
  }
} satisfies ExportedHandler<Env>;
```

## AI Agent Code Mode

Instead of calling tools one at a time, the LLM writes code that calls multiple tools programmatically. This reduces token usage by up to 80%.

Uses the Agents SDK `AIChatAgent` with `DynamicWorkerExecutor` to combine tools into a single `codemode` tool:

```typescript
import { AIChatAgent } from "@cloudflare/agents/ai-chat-agent";
import { DynamicWorkerExecutor } from "@cloudflare/agents/dynamic-worker-executor";
import { codemode } from "@cloudflare/agents/codemode";

export class MyAgent extends AIChatAgent<Env> {
  async onChatMessage(onFinish) {
    const tools = getMyTools(this.sql);

    const result = streamText({
      model: createWorkersAI({ binding: this.env.AI }),
      system: "You are a helpful assistant.",
      messages: this.messages,
      tools: codemode({
        tools,
        executor: new DynamicWorkerExecutor(this.env.LOADER)
      }),
      maxSteps: 10
    });

    return result.toTextStreamResponse();
  }
}
```

The agent generates a single TypeScript function that chains multiple tool calls, rather than making sequential individual tool calls.

## Wrapping MCP Servers (codeMcpServer)

Collapse any MCP server's tool list into a single `code` tool with `codeMcpServer`:

```typescript
import { createMcpHandler } from "@cloudflare/agents/mcp";
import { codeMcpServer } from "@cloudflare/agents/codemode";
import { DynamicWorkerExecutor } from "@cloudflare/agents/dynamic-worker-executor";

function createUpstreamServer() {
  // Standard MCP server with multiple tools
  const server = new McpServer({ name: "my-tools", version: "1.0" });
  server.tool("add", { a: z.number(), b: z.number() }, ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }]
  }));
  // ... more tools
  return server;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);

    if (url.pathname === "/mcp") {
      // Raw: exposes all individual tools
      return createMcpHandler(createUpstreamServer)(request, env, ctx);
    }

    if (url.pathname === "/codemode") {
      // Wrapped: single "code" tool that can call all upstream tools
      return createMcpHandler(() =>
        codeMcpServer(createUpstreamServer(), new DynamicWorkerExecutor(env.LOADER))
      )(request, env, ctx);
    }

    return new Response("Not found", { status: 404 });
  }
};
```

## OpenAPI Spec → MCP Code Tool

Turn any REST API into a pair of MCP tools (`search` + `execute`) using `openApiMcpServer`:

```typescript
import { openApiMcpServer } from "@cloudflare/agents/codemode";
import { DynamicWorkerExecutor } from "@cloudflare/agents/dynamic-worker-executor";

let cachedSpec: string | null = null;

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const token = request.headers.get("Authorization")?.replace("Bearer ", "");
    if (!token) return new Response("Bearer token required", { status: 401 });

    if (!cachedSpec) {
      const res = await fetch("https://raw.githubusercontent.com/.../openapi.json");
      cachedSpec = await res.text();
    }

    return createMcpHandler(() =>
      openApiMcpServer({
        spec: cachedSpec,
        executor: new DynamicWorkerExecutor(env.LOADER),
        baseUrl: "https://api.example.com/v4",
        headers: { Authorization: `Bearer ${token}` }
      })
    )(request, env, ctx);
  }
};
```

This pattern keeps credentials on the host side while the sandbox executes API calls without direct token access.

## Bundled Playground with Warm Caching

Use content-hashed IDs with `get()` for efficient caching, and `@cloudflare/worker-bundler` for TypeScript/npm support:

```typescript
import { createWorker } from "@cloudflare/worker-bundler";

async function createWorkerId(files: Record<string, string>): Promise<string> {
  const payload = JSON.stringify(Object.entries(files).sort());
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(payload));
  const hash = Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 16);
  return `worker-${hash}`;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const { files } = await request.json<{ files: Record<string, string> }>();
    const workerId = await createWorkerId(files);

    const worker = env.LOADER.get(workerId, async () => {
      const { mainModule, modules, wranglerConfig } = await createWorker({
        files, bundle: true, minify: false
      });

      return {
        mainModule,
        modules: modules as Record<string, string>,
        compatibilityDate: wranglerConfig?.compatibilityDate ?? "2026-01-01",
        globalOutbound: null,
        tails: [
          (ctx as any).exports.DynamicWorkerTail({ props: { workerId } })
        ]
      };
    });

    return worker.getEntrypoint().fetch(request);
  }
};
```

Same code + same hash = same ID = warm cache hit. Different code = different hash = new isolate.

## Real-Time Log Streaming

Use a Durable Object to collect Tail Worker logs and return them synchronously with the response:

```typescript
import { WorkerEntrypoint } from "cloudflare:workers";
import { DurableObject, RpcTarget } from "cloudflare:workers";

// 1. Log waiter collects events
export class LogWaiter extends RpcTarget {
  private logs: unknown[] = [];
  private resolve?: (logs: unknown[]) => void;

  push(entries: unknown[]) {
    this.logs.push(...entries);
    this.resolve?.(this.logs);
  }

  async getLogs(timeoutMs: number): Promise<unknown[]> {
    if (this.logs.length > 0) return this.logs;
    return new Promise((resolve) => {
      this.resolve = resolve;
      setTimeout(() => resolve(this.logs), timeoutMs);
    });
  }
}

// 2. Durable Object holds the waiter
export class LogSession extends DurableObject {
  private waiter = new LogWaiter();

  async waitForLogs() { return this.waiter; }
  async pushLogs(entries: unknown[]) { this.waiter.push(entries); }
}

// 3. Tail Worker forwards logs to the DO
export class DynamicWorkerTail extends WorkerEntrypoint {
  async tail(events: TraceItem[]) {
    const entries = events.flatMap((e) =>
      e.logs.map((log) => ({
        workerId: this.ctx.props.workerId,
        level: log.level,
        message: log.message
      }))
    );

    const session = this.env.LogSession.getByName(this.ctx.props.workerId);
    await session.pushLogs(entries);
  }
}
```

**Usage in loader**:

```typescript
const logSession = ctx.exports.LogSession.getByName(workerId);
const logWaiter = await logSession.waitForLogs();

const response = await worker.getEntrypoint().fetch(request);

const logs = await logWaiter.getLogs(1000); // Wait up to 1s for logs
return Response.json({ response: await response.text(), logs });
```

## Capability-Based Security

Pass only the capabilities the Dynamic Worker needs. Hide secrets, restrict access:

```typescript
// Loader defines narrow interfaces
export class DatabaseReader extends WorkerEntrypoint {
  async query(sql: string): Promise<unknown[]> {
    // Validate SQL is read-only
    if (!/^\s*SELECT/i.test(sql)) throw new Error("Read-only access");
    return this.env.DB.prepare(sql).all().results;
  }
}

export class HttpGateway extends WorkerEntrypoint {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    // Only allow specific hosts
    const allowed = ["api.example.com", "data.example.com"];
    if (!allowed.includes(url.hostname)) {
      return new Response("Blocked", { status: 403 });
    }
    return fetch(request);
  }
}

// Dynamic Worker receives constrained capabilities
const worker = env.LOADER.load({
  env: {
    DB: ctx.exports.DatabaseReader(),
    // No direct KV, R2, or D1 access
  },
  globalOutbound: ctx.exports.HttpGateway(), // Filtered egress
  // ...
});
```
