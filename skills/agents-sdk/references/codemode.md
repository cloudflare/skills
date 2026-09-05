# Codemode (Experimental)

## Contents
- Fit
- Setup
- Usage
- With MCP Tools
- How It Works
- Network Isolation
- Limitations


Fetch https://developers.cloudflare.com/agents/model-context-protocol/protocol/codemode/ and https://developers.cloudflare.com/dynamic-workers/ for complete documentation.

Codemode lets LLMs write and execute code that orchestrates your tools, instead of calling them one at a time. Current Code Mode uses `createCodemodeRuntime`, connectors, and a durable execution log. Generated JavaScript runs in a Worker Loader-backed Dynamic Worker sandbox.

## Fit

| Scenario | Use Codemode? |
|----------|---------------|
| Single tool call | No — standard tool calling is simpler |
| Chained tool calls with logic | Yes |
| Conditional logic across tools | Yes |
| MCP multi-server workflows | Yes |
| Simple Q&A chat | No |

## Setup

### Wrangler Config

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }],
  "compatibility_flags": ["nodejs_compat"]
}
```

Load `dynamic-workers` when the task involves raw Worker Loader APIs, custom sandbox bindings, egress control, Tail Worker logging, Dynamic Workflows, or Durable Object facets.

### Install

```bash
npm install @cloudflare/codemode ai
```

## Usage

```typescript
import { createCodemodeRuntime, DynamicWorkerExecutor } from "@cloudflare/codemode";
import { streamText, convertToModelMessages } from "ai";

export class MyAgent extends Agent<Env, State> {
  async onChatMessage() {
    const runtime = createCodemodeRuntime({
      ctx: this.ctx,
      executor: new DynamicWorkerExecutor({ loader: this.env.LOADER }),
      connectors: [
        // Add connector instances that expose typed globals to generated code.
      ]
    });

    const result = streamText({
      model,
      system: "You are a helpful assistant.",
      messages: await convertToModelMessages(this.messages),
      tools: { codemode: runtime.tool() }
    });

    return result.toUIMessageStreamResponse();
  }
}
```

## With Connectors And MCP Tools

```typescript
const runtime = createCodemodeRuntime({
  ctx: this.ctx,
  executor: new DynamicWorkerExecutor({ loader: this.env.LOADER }),
  connectors: [
    // Add connector instances that expose typed globals to generated code.
  ]
});
```

## How It Works

1. `createCodemodeRuntime` builds one `codemode` tool from typed connectors and any tool surfaces supported by current docs.
2. The model discovers capabilities, writes code against typed globals, and can reuse saved snippets.
3. Code runs in a Dynamic Worker sandbox via `DynamicWorkerExecutor`.
4. Tool and connector calls route back to the host through Workers RPC.
5. The durable execution log lets approved or completed calls replay instead of re-running after interruption.

## Network Isolation

```typescript
const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  globalOutbound: null           // isolate generated code from the public network
  // globalOutbound: env.MY_SERVICE  // route through a Fetcher
});
```

Raw Dynamic Workers inherit parent network access when `globalOutbound` is omitted. Code Mode executors should be configured so generated code can only use the tools or gateways you intentionally expose.

## Limitations

- Experimental — API may change
- Approval-gated actions can pause execution and resume after approval; retrieve current docs before wiring UX around pending approvals.
- JavaScript execution only
- Requires `worker_loaders` binding
- Generated code still needs input/output bounds, logging, and safe tool descriptions
