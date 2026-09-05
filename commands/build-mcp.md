---
description: Build a remote MCP server on Cloudflare using the Agents SDK handler API
argument-hint: [mcp-description]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# Build MCP Server on Cloudflare

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

Read `agents-sdk/SKILL.md` for SDK guidance and `agents-sdk/references/mcp.md` for the relevant developer documentation. Follow the linked server and security guides for scaffolding, dependency versions, implementation, and authentication; use the migration guide when adapting an existing server. Validate the requested tools and endpoint locally before deployment.

## Example Usage

```
/build-mcp a GitHub integration server with repo tools
/build-mcp a database query tool with D1
/build-mcp an authenticated API gateway with OAuth
```
