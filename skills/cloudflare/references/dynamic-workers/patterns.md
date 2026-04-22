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
          compatibilityDate: "$today",
          mainModule: "worker.js",
          modules: { "worker.js": code?.trim() || DEFAULT_CODE },
          globalOutbound: null,
          limits: { cpuMs: 50, subRequests: 20 }
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

Instead of calling tools one at a time, the LLM writes code that calls multiple tools programmatically.

Uses `@cloudflare/codemode` with `DynamicWorkerExecutor` to combine tools into a single `codemode` tool:

```typescript
import { Agent } from "agents";
import { createCodeTool } from "@cloudflare/codemode/ai";
import { DynamicWorkerExecutor } from "@cloudflare/codemode";
import { streamText, convertToModelMessages, stepCountIs } from "ai";

export class MyAgent extends Agent<Env> {
  async onChatMessage() {
    const executor = new DynamicWorkerExecutor({
      loader: this.env.LOADER
    });

    const codemode = createCodeTool({
      tools: getMyTools(this.sql),
      executor
    });

    const result = streamText({
      model,
      system: "You are a helpful assistant.",
      messages: await convertToModelMessages(this.state.messages),
      tools: { codemode },
      stopWhen: stepCountIs(10)
    });

    // Stream response back to client...
  }
}
```

The agent generates a single TypeScript function that chains multiple tool calls, rather than making sequential individual tool calls.

## Wrapping MCP Servers (codeMcpServer)

Collapse any MCP server's tool list into a single `code` tool with `codeMcpServer`:

```typescript
import { codeMcpServer } from "@cloudflare/codemode/mcp";
import { DynamicWorkerExecutor } from "@cloudflare/codemode";

const executor = new DynamicWorkerExecutor({ loader: env.LOADER });

// Wrap an existing MCP server — all its tools become
// typed methods the LLM can call from generated code
const server = await codeMcpServer({ server: upstreamMcp, executor });
```

## OpenAPI Spec → MCP Code Tool

Turn any REST API into a pair of MCP tools (`search` + `execute`) using `openApiMcpServer`. The host-side `request` handler keeps authentication out of the sandbox:

```typescript
import { openApiMcpServer } from "@cloudflare/codemode/mcp";
import { DynamicWorkerExecutor } from "@cloudflare/codemode";

const executor = new DynamicWorkerExecutor({ loader: env.LOADER });

const server = openApiMcpServer({
  spec: openApiSpec,
  executor,
  request: async ({ method, path, query, body }) => {
    // Runs on the host — add auth headers here
    const res = await fetch(`https://api.example.com${path}`, {
      method,
      headers: { Authorization: `Bearer ${token}` },
      body: body ? JSON.stringify(body) : undefined,
    });
    return res.json();
  },
});
```

This keeps authentication and request policy on the host side while the sandbox executes the generated orchestration code.

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
        compatibilityDate: wranglerConfig?.compatibilityDate ?? "$today",
        globalOutbound: null,
        limits: { cpuMs: 50, subRequests: 20 },
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
