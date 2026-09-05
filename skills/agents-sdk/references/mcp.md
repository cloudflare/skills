# MCP Integration

Fetch https://developers.cloudflare.com/agents/api-reference/mcp-client-api/ and https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/ for complete documentation.

Agents include a multi-server MCP client for connecting to external MCP servers, and `createMcpHandler` for building MCP servers.

## Add an MCP Server

```typescript
import { Agent, callable } from "agents";

export class MyAgent extends Agent<Env, State> {
  @callable()
  async addServer(name: string, url: string) {
    // Options-based API (recommended)
    const result = await this.addMcpServer(name, url, {
      callbackHost: "https://my-worker.workers.dev",
      transport: { headers: { Authorization: "Bearer ..." } }
    });

    if (result.state === "authenticating") {
      // OAuth required - redirect user to result.authUrl
      return { needsAuth: true, authUrl: result.authUrl };
    }

    return { ready: true, id: result.id };
  }
}
```

## Use MCP Tools

```typescript
async onChatMessage() {
  // Get AI-compatible tools from all connected MCP servers
  const mcpTools = this.mcp.getAITools();
  
  const allTools = {
    ...localTools,
    ...mcpTools
  };

  const result = streamText({
    model: openai("gpt-4o"),
    messages: await convertToModelMessages(this.messages),
    tools: allTools
  });
  
  return result.toUIMessageStreamResponse();
}
```

## List MCP Resources

```typescript
// List all registered servers
const servers = this.mcp.listServers();

// List tools from all servers
const tools = this.mcp.listTools();

// List resources
const resources = this.mcp.listResources();

// List prompts
const prompts = this.mcp.listPrompts();
```

## Remove Server

```typescript
await this.removeMcpServer(serverId);
```

## Building an MCP Server

For new servers on Agents SDK v0.20.0 or later, use an SDK v2 server factory with `createMcpHandler` from `agents/mcp/server`. `McpAgent` is deprecated and feature-frozen. For existing stateful servers or older pinned SDKs, follow the [migration guide](https://developers.cloudflare.com/agents/model-context-protocol/guides/migrate-to-mcp-sdk-v2/) before changing state or session behavior.

Install `agents`, `zod`, and the exact `@modelcontextprotocol/server` version supported by that Agents release; see the [handler API](https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/) for dependencies.

Pass a factory that creates a fresh server per request. Keep the Worker object `fetch()` export; do not default-export the handler function. A stateless MCP handler does not require a Durable Object binding or migration.

```typescript
import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";

function createServer() {
  const server = new McpServer({ name: "my-mcp", version: "1.0.0" });
  server.registerTool("hello", {
    description: "Return a greeting",
    inputSchema: { name: z.string() }
  }, async ({ name }) => ({
    content: [{ text: `Hello, ${name}!`, type: "text" }]
  }));
  return server;
}

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    return createMcpHandler(createServer)(request, env, ctx);
  }
};
```

## Transports

Fetch https://developers.cloudflare.com/agents/model-context-protocol/protocol/transport/ for complete documentation.

| Transport | Use for |
|-----------|---------|
| Streamable HTTP (`createMcpHandler`) | External/public clients (recommended) |
| SSE (`McpAgent.serveSSE`) | Existing legacy servers only (deprecated; see migration guide) |
| RPC (`addMcpServer(name, env.Binding)`) | Same-Worker internal calls (fastest) |

### RPC Transport (Same Worker)

```typescript
async onStart() {
  await this.addMcpServer("internal-tools", this.env.MyMCPBinding, {
    props: { userId: this.name }
  });
}
```

## Retry on MCP Connections

```typescript
await this.addMcpServer("tools", url, {
  retry: { maxAttempts: 3, baseDelayMs: 500 }
});
```

## Securing MCP Servers

Fetch https://developers.cloudflare.com/agents/model-context-protocol/guides/securing-mcp-server/ for complete documentation.

Use `@cloudflare/workers-oauth-provider` to add OAuth in front of your MCP server. See the securing docs for proxy patterns and `redirect_uri` validation.
