# Executor Patterns

## DynamicWorkerExecutor (Production)

The default production executor. Creates isolated V8 Workers for each execution.

```typescript
import { DynamicWorkerExecutor } from "@cloudflare/codemode";

const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  timeout: 30000,
  globalOutbound: null,  // Network blocked
});
```

### Wrangler Configuration

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }],
  "compatibility_flags": ["nodejs_compat"]
}
```

### Network Control

```typescript
// Fully isolated (default) — fetch() and connect() throw
new DynamicWorkerExecutor({ loader, globalOutbound: null });

// Route outbound through a Fetcher (controlled access)
new DynamicWorkerExecutor({ loader, globalOutbound: env.MY_OUTBOUND });

// Inherit parent Worker's access (use with caution)
new DynamicWorkerExecutor({ loader, globalOutbound: undefined });
```

### Security Properties

- Each execution runs in a separate V8 isolate
- No shared state between executions
- Console output captured (not leaked to host)
- Timeout enforced via `Promise.race`
- Tool calls dispatched via Workers RPC (not network requests)

---

## Custom Executor: Node.js VM (Development)

For local development without Cloudflare Workers. Uses Node.js `vm` module.

```typescript
import vm from "node:vm";
import type { Executor, ExecuteResult } from "@cloudflare/codemode";

class NodeVMExecutor implements Executor {
  async execute(
    code: string,
    fns: Record<string, (...args: unknown[]) => Promise<unknown>>
  ): Promise<ExecuteResult> {
    const logs: string[] = [];

    // Create codemode proxy
    const codemode = new Proxy({}, {
      get(_, prop: string) {
        return async (...args: unknown[]) => {
          const fn = fns[prop];
          if (!fn) throw new Error(`Tool not found: ${prop}`);
          return fn(args[0]);
        };
      },
    });

    // Create sandbox context
    const context = vm.createContext({
      codemode,
      console: {
        log: (...args: unknown[]) => logs.push(args.map(String).join(" ")),
        warn: (...args: unknown[]) => logs.push(`[warn] ${args.map(String).join(" ")}`),
        error: (...args: unknown[]) => logs.push(`[error] ${args.map(String).join(" ")}`),
      },
      fetch,
      setTimeout,
      URL,
      Response,
      Request,
      Headers,
    });

    try {
      const script = new vm.Script(`(${code})()`);
      const result = await script.runInContext(context, { timeout: 30000 });
      return { result, logs };
    } catch (error) {
      return { result: null, error: String(error), logs };
    }
  }
}
```

### Usage

```typescript
const executor = new NodeVMExecutor();
const codemode = createCodeTool({ tools, executor });
```

**Limitations:**
- Less secure than V8 isolates (Node VM can be escaped)
- No WorkerLoader binding needed
- Suitable for local development only

---

## Custom Executor: HTTP Bridge (Remote Execution)

For running code on a separate server (useful for language-specific runtimes).

```typescript
import type { Executor, ExecuteResult } from "@cloudflare/codemode";

class HTTPExecutor implements Executor {
  constructor(private serverUrl: string, private callbackUrl: string) {}

  async execute(
    code: string,
    fns: Record<string, (...args: unknown[]) => Promise<unknown>>
  ): Promise<ExecuteResult> {
    const execId = crypto.randomUUID();

    // Register tool callbacks
    registerCallbacks(execId, fns);

    try {
      const response = await fetch(`${this.serverUrl}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code,
          callbackUrl: `${this.callbackUrl}/${execId}`,
          tools: Object.keys(fns),
        }),
      });

      return await response.json() as ExecuteResult;
    } finally {
      unregisterCallbacks(execId);
    }
  }
}
```

The remote server creates tool proxies that POST back to the callback URL for each `codemode.*` call. See the [codemode example](https://github.com/cloudflare/agents/tree/main/examples/codemode) for a complete Node.js HTTP bridge implementation.

---

## Executor Selection Guide

| Executor | Environment | Security | Network | Use Case |
|----------|------------|----------|---------|----------|
| `DynamicWorkerExecutor` | Cloudflare Workers | V8 isolate | Configurable | Production |
| Node VM | Node.js | `vm` module | Unrestricted | Local development |
| HTTP Bridge | Any | Depends on server | Depends on server | Multi-language, remote execution |

Always use `DynamicWorkerExecutor` in production. The `Executor` interface is intentionally minimal to support diverse sandbox implementations.
