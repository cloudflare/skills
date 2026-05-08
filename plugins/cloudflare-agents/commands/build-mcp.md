---
description: Build a remote MCP server on Cloudflare using McpAgent
argument-hint: [mcp-description]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# Build MCP Server on Cloudflare

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

When this command is invoked:

1. Read the skill file at `agents-sdk/SKILL.md` for core SDK guidance
2. Read `agents-sdk/references/mcp.md` for MCP client and server APIs, transports, and securing
3. Read `agents-sdk/references/configuration.md` for wrangler setup
4. Fetch https://developers.cloudflare.com/agents/api-reference/mcp-agent-api/ for the latest McpAgent API
5. For OAuth/security, fetch https://developers.cloudflare.com/agents/api-reference/securing-mcp-servers/

## Scaffold Steps

1. **Create project**: `npx create-cloudflare@latest --template cloudflare/agents-starter` (or start fresh)
2. **Install MCP SDK**: `npm install @modelcontextprotocol/sdk zod`
3. **Configure wrangler.jsonc**: DO binding + `new_sqlite_classes` migration for the McpAgent class
4. **Implement McpAgent**: extend `McpAgent`, create `McpServer`, register tools in `init()`
5. **Serve transport**: `MyMCP.serve("/mcp", { binding: "MyMCP" })` (Streamable HTTP, recommended)
6. **Test**: `npx @modelcontextprotocol/inspector@latest`
7. **Deploy**: `npx wrangler deploy`

## Quick Reference

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { z } from "zod";

export class MyMCP extends McpAgent<Env, State, {}> {
  server = new McpServer({ name: "my-mcp", version: "1.0.0" });
  initialState = { counter: 0 };

  async init() {
    this.server.registerTool("my_tool", {
      description: "Does something useful",
      inputSchema: { query: z.string() }
    }, async ({ query }) => ({
      content: [{ text: `Result: ${query}`, type: "text" }]
    }));
  }
}

// Entry point
export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    return MyMCP.serve("/mcp", { binding: "MyMCP" }).fetch(request, env, ctx);
  }
};
```

## Transport Options

| Transport | Method | Use for |
|-----------|--------|---------|
| Streamable HTTP | `MyMCP.serve("/mcp")` | External/public clients (recommended) |
| SSE | `MyMCP.serveSSE("/sse")` | Legacy clients only (deprecated) |
| RPC | `addMcpServer(name, env.Binding)` | Same-Worker internal calls |

## Example Usage

```
/build-mcp a GitHub integration server with repo tools
/build-mcp a database query tool with D1
/build-mcp an authenticated API gateway with OAuth
```
