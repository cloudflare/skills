---
description: Build an AI agent on Cloudflare using the Agents SDK
argument-hint: [agent-description]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# Build AI Agent on Cloudflare

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

When this command is invoked:

1. Read the skill file at `agents-sdk/SKILL.md` for core SDK guidance, APIs, and wrangler config
2. Based on what the user wants to build, read the relevant references from `agents-sdk/references/`:
   - For chat/AI agents: `streaming-chat.md`, `client-sdk.md`
   - For state management: `state-scheduling.md`
   - For RPC methods: `callable.md`
   - For background work: `workflows.md`, `durable-execution.md`, `queue-retries.md`
   - For MCP integration: `mcp.md`
   - For email handling: `email.md`
   - For webhooks/push: `webhooks-push.md`
   - For approval flows: `human-in-the-loop.md`
   - For voice: `voice.md`
   - For browser tools: `browse-the-web.md`
   - For higher-level chat: `think.md`
3. Fetch the relevant pages from https://developers.cloudflare.com/agents/ for the latest API details
4. Always start with `configuration.md` and `routing.md` for project setup

## Scaffold Steps

1. **Create project**: `npx create-cloudflare@latest --template cloudflare/agents-starter`
2. **Configure wrangler.jsonc**: DO bindings, migrations, AI binding, assets
3. **Implement agent class**: extend `Agent` or `AIChatAgent` depending on use case
4. **Wire routing**: `routeAgentRequest` in the default export
5. **Build client**: `useAgent` + `useAgentChat` React hooks
6. **Deploy**: `npx wrangler deploy`

## Key Decision: Agent vs AIChatAgent vs Think

| Need | Use | Package |
|------|-----|---------|
| Custom stateful logic, RPC, scheduling | `Agent` | `agents` |
| AI chat with streaming, tools, persistence | `AIChatAgent` | `@cloudflare/ai-chat` |
| AI chat with automatic tool loop, built-in workspace | `Think` | `@cloudflare/think` (experimental) |

## Example Usage

```
/build-agent a customer support chatbot with tool calling
/build-agent a real-time collaborative editor with state sync
/build-agent a background processing agent with scheduled tasks
/build-agent a voice assistant that can browse the web
```
