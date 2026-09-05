---
description: Build a remote MCP server on Cloudflare using the Agents SDK handler API
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
4. Fetch https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/ for the current handler API and supported dependency versions
5. For OAuth/security, fetch https://developers.cloudflare.com/agents/api-reference/securing-mcp-servers/

## Scaffold Steps

1. **Create project**: `npx create-cloudflare@latest --template cloudflare/agents-starter` (or start fresh)
2. **Install MCP SDK**: install `agents`, `zod`, and the exact `@modelcontextprotocol/server` version supported by the installed Agents release
3. **Configure wrangler.jsonc**: set the Worker entrypoint and compatibility date; a stateless MCP handler needs no DO binding or migration
4. **Implement server factory**: create a fresh SDK v2 `McpServer` and register tools inside the factory
5. **Serve transport**: invoke `createMcpHandler(createServer)(request, env, ctx)` inside the Worker object `fetch()` export
6. **Test**: `npx @modelcontextprotocol/inspector@latest`
7. **Deploy**: `npx wrangler deploy`

For the server implementation and transport guidance, use `agents-sdk/references/mcp.md`. For existing `McpAgent` servers or older pinned SDKs, follow the [migration guide](https://developers.cloudflare.com/agents/model-context-protocol/guides/migrate-to-mcp-sdk-v2/) before changing state or session behavior.

## Example Usage

```
/build-mcp a GitHub integration server with repo tools
/build-mcp a database query tool with D1
/build-mcp an authenticated API gateway with OAuth
```
