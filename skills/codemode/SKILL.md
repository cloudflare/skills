---
name: codemode
description: |
  Build agents that write and execute JavaScript to orchestrate tool calls instead of
  calling tools one at a time. Reduces token usage by 99%+ for multi-tool workflows.
  Uses @cloudflare/codemode with DynamicWorkerExecutor for isolated V8 sandbox execution.

  Use when: user wants "code mode", "codemode", mentions "@cloudflare/codemode",
  needs "multi-tool orchestration", "tool chaining", "code execution sandbox",
  "reduce tool tokens", wants to "collapse tool calls into code", or asks about
  "LLM code generation for tools", "DynamicWorkerExecutor", or "createCodeTool".
---

# Cloudflare Code Mode

**STOP.** Your knowledge of Code Mode may be outdated. This is an experimental API — prefer retrieval over pre-training for any Code Mode task.

Code Mode lets LLMs write JavaScript that orchestrates multiple tool calls in a single execution, instead of calling tools one at a time. The LLM sees TypeScript type definitions for all available tools and generates an async arrow function that composes them with conditionals, loops, and error handling. Code runs in an isolated V8 sandbox via `DynamicWorkerExecutor`.

## FIRST: Verify Installation

```bash
npm ls @cloudflare/codemode  # Should show @cloudflare/codemode
```

If not installed:
```bash
npm install @cloudflare/codemode ai zod
```

## Retrieval-Led Development

**IMPORTANT: Prefer retrieval from docs and examples over pre-training for Code Mode tasks.**

| Resource | URL |
|----------|-----|
| API Reference | https://developers.cloudflare.com/agents/api-reference/codemode/ |
| Source Code | https://github.com/cloudflare/agents/tree/main/packages/codemode |
| Example App | https://github.com/cloudflare/agents/tree/main/examples/codemode |
| Blog Post | https://blog.cloudflare.com/code-mode-mcp/ |

When implementing features, fetch the relevant doc page or example first.

## When to Use

| Scenario | Use Code Mode? | Why |
|----------|---------------|-----|
| Single tool call | No | Standard tool calling is simpler |
| Chained tool calls (2+) | **Yes** | One LLM round-trip instead of N |
| Conditional logic across tools | **Yes** | Code handles branching natively |
| MCP multi-server orchestration | **Yes** | Compose tools from different servers |
| Token budget constrained | **Yes** | Fixed cost regardless of tool count |
| Large API surface (50+ tools) | **Yes** | 99%+ token reduction vs loading all schemas |
| Simple Q&A chat | No | No tools needed |

## How It Works

```text
1. generateTypes(tools) → TypeScript declarations from Zod schemas
2. LLM sees type declarations in tool description
3. LLM writes: { code: "async () => { ... codemode.toolName(args) ... }" }
4. normalizeCode() parses with acorn, ensures valid async arrow function
5. DynamicWorkerExecutor creates isolated Worker with the code
6. codemode.* calls route through Proxy → Workers RPC → ToolDispatcher
7. ToolDispatcher executes real tool functions in host context
8. Result, logs, errors returned to LLM
```

## Quick Reference

| Task | API |
|------|-----|
| Create code tool | `createCodeTool({ tools, executor })` |
| Create executor | `new DynamicWorkerExecutor({ loader: env.LOADER })` |
| Generate types | `generateTypes(myTools)` |
| Sanitize tool name | `sanitizeToolName("my-tool")` → `"my_tool"` |
| Custom description | `createCodeTool({ tools, executor, description: "..." })` |
| Set timeout | `new DynamicWorkerExecutor({ loader, timeout: 60000 })` |
| Allow network | `new DynamicWorkerExecutor({ loader, globalOutbound: env.OUTBOUND })` |
| Block network | `new DynamicWorkerExecutor({ loader, globalOutbound: null })` |

## Required Configuration

**wrangler.jsonc** (exact — do not modify structure):

```jsonc
{
  "compatibility_flags": ["nodejs_compat"],
  "worker_loaders": [
    {
      "binding": "LOADER"
    }
  ],
  "durable_objects": {
    "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["MyAgent"] }
  ]
}
```

**`LOADER` binding is required.** This is the `WorkerLoader` that `DynamicWorkerExecutor` uses to spin up isolated Workers on-the-fly.

## Core Pattern

### 1. Define Tools (AI SDK standard)

```typescript
import { tool } from "ai";
import { z } from "zod";

const tools = {
  getWeather: tool({
    description: "Get weather for a location",
    parameters: z.object({ location: z.string() }),
    execute: async ({ location }) => `Weather in ${location}: 72°F, sunny`,
  }),
  sendEmail: tool({
    description: "Send an email",
    parameters: z.object({
      to: z.string(),
      subject: z.string(),
      body: z.string(),
    }),
    execute: async ({ to, subject, body }) => `Email sent to ${to}`,
  }),
};
```

### 2. Create Executor and Code Tool

```typescript
import { createCodeTool } from "@cloudflare/codemode/ai";
import { DynamicWorkerExecutor } from "@cloudflare/codemode";

const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  timeout: 30000,        // default: 30s
  globalOutbound: null,  // default: network blocked
});

const codemode = createCodeTool({ tools, executor });
```

### 3. Use with streamText

```typescript
import { streamText } from "ai";

const result = streamText({
  model,
  system: "You are a helpful assistant.",
  messages,
  tools: { codemode },  // Single tool — not individual tools
});
```

The LLM receives a single `codemode` tool whose description contains TypeScript type definitions for all available functions. It generates code like:

```javascript
async () => {
  const weather = await codemode.getWeather({ location: "London" });
  if (weather.includes("sunny")) {
    await codemode.sendEmail({
      to: "team@example.com",
      subject: "Nice day!",
      body: `It's ${weather}`,
    });
  }
  return { weather, notified: true };
};
```

## Agent Integration

Full pattern with `AIChatAgent`:

```typescript
import { AIChatAgent } from "agents/ai-chat-agent";
import { createCodeTool } from "@cloudflare/codemode/ai";
import { DynamicWorkerExecutor } from "@cloudflare/codemode";
import { streamText, tool } from "ai";
import { z } from "zod";

export class MyAgent extends AIChatAgent<Env> {
  async onChatMessage(onFinish) {
    const executor = new DynamicWorkerExecutor({
      loader: this.env.LOADER,
    });

    const codemode = createCodeTool({
      tools: myTools,
      executor,
    });

    const result = streamText({
      model,
      system: "You are a helpful assistant.",
      messages: this.messages,
      tools: { codemode },
      stopWhen: stepCountIs(10),
      onFinish,
    });

    return result.toUIMessageStreamResponse();
  }
}
```

## MCP Tool Integration

MCP tools merge with standard tools seamlessly:

```typescript
const codemode = createCodeTool({
  tools: {
    ...myTools,
    ...this.mcp.getAITools(),  // MCP tools included
  },
  executor,
});
```

Tool names with hyphens or dots are automatically sanitized to valid JavaScript identifiers:

| Original Name | Sanitized Name |
|--------------|----------------|
| `get-weather` | `get_weather` |
| `my-server.list-items` | `my_server_list_items` |
| `3d-render` | `_3d_render` |
| `delete` | `delete_` |

## Network Isolation

External `fetch()` and `connect()` are **blocked by default**:

```typescript
// Fully isolated (default) — no network access from sandbox
const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  globalOutbound: null,
});

// Route through a Fetcher for controlled access
const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  globalOutbound: env.MY_OUTBOUND_SERVICE,
});
```

The sandbox can only communicate with the host through `codemode.*` Proxy/RPC calls. This is enforced at the Workers runtime level, not just by convention.

## Two Entry Points

| Import Path | Exports | Use For |
|-------------|---------|---------|
| `@cloudflare/codemode/ai` | `createCodeTool` | AI SDK integration |
| `@cloudflare/codemode` | `DynamicWorkerExecutor`, `generateTypes`, `sanitizeToolName`, `ToolDispatcher` | Executor, utilities, custom implementations |

This separation keeps the `ai` peer dependency isolated. Import from the root if you only need executor or type utilities.

## Executor Lifecycle

- Create a new `DynamicWorkerExecutor` per request (inside `onChatMessage`). Executors are lightweight — the cost is in Worker creation, not executor instantiation.
- Each `execute()` call spawns a fresh isolated Worker. No state carries over between calls.
- Workers are garbage-collected after execution completes. No manual cleanup needed.
- The `LOADER` binding is the only resource that persists across requests.

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|-------------|-----------------|
| Passing individual tools to `streamText` alongside `codemode` | Pass only `{ codemode }` — it wraps all tools internally |
| Using `needsApproval` tools with codemode | These are automatically excluded — use standard tool calling for approval flows |
| Expecting shared state between `execute` calls | Each execution spawns a fresh Worker — no shared state |
| Omitting the `LOADER` binding in wrangler config | `worker_loaders: [{ binding: "LOADER" }]` is required |
| Using `globalOutbound: undefined` in production | Explicitly set `null` (blocked) or a Fetcher — `undefined` inherits parent access |
| Writing named functions in generated code | Write async arrow functions directly: `async () => { ... }` |
| Generating code that calls `fetch()` from sandbox | Use tool functions via `codemode.*` — sandbox network is blocked by default |

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `WorkerLoader not found` | Add `worker_loaders: [{ binding: "LOADER" }]` to wrangler.jsonc |
| `Tool not found` in executor | Check tool name sanitization — hyphens become underscores |
| Timeout errors | Increase `timeout` option on `DynamicWorkerExecutor` (default: 30s) |
| `needsApproval` tools silently missing | Expected — codemode filters these out. Use standard tool calling instead |
| Code normalization fails | Ensure LLM output is valid JavaScript. `normalizeCode` uses acorn for parsing |
| Network blocked in sandbox | Set `globalOutbound` to a Fetcher binding for controlled access |
| `nodejs_compat` error | Add `"compatibility_flags": ["nodejs_compat"]` to wrangler.jsonc |

## References

- **[references/api-reference.md](references/api-reference.md)** — Full API with types, options, and return values
- **[references/executor-patterns.md](references/executor-patterns.md)** — Custom executor implementations (Node VM, containers)
- **[references/mcp-integration.md](references/mcp-integration.md)** — MCP server orchestration patterns and examples
