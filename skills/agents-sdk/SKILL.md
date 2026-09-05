---
name: agents-sdk
description: Build AI agents on Cloudflare Workers using the Agents SDK. Load when creating stateful agents, durable workflows, real-time WebSocket apps, scheduled tasks, MCP servers, chat applications, voice agents, or browser automation. Covers Agent class, state management, callable RPC, Workflows, durable execution, queues, retries, observability, and React hooks. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.
---

# Cloudflare Agents SDK

Your knowledge of the Agents SDK may be outdated. **Prefer retrieval over pre-training** for any Agents SDK task.

## Retrieval Sources

Cloudflare docs: https://developers.cloudflare.com/agents/

For a documentation page by topic, use the [docs index](references/docs-index.md).

## FIRST: Verify Installation

```bash
npm ls agents  # Should show agents package
```

If not installed:
```bash
npm install agents
```

For chat agents:
```bash
npm install agents @cloudflare/ai-chat ai @ai-sdk/react
```

## Configuration constraints

**Gotchas:**
- Do NOT enable `experimentalDecorators` in tsconfig (breaks `@callable`)
- Never edit old migrations — always add new tags
- Each agent class needs its own DO binding + migration entry
- Add `"ai": { "binding": "AI" }` for Workers AI

## References

Read only the references relevant to the task. For an initial Agent class, Wrangler binding, routing, or React client example, use [quick-start.md](references/quick-start.md).

### Core
- **[references/state-scheduling.md](references/state-scheduling.md)** — State persistence, scheduling, SQL
- **[references/callable.md](references/callable.md)** — RPC methods, streaming, timeouts
- **[references/routing.md](references/routing.md)** — URL patterns, custom routing, `getAgentByName`
- **[references/configuration.md](references/configuration.md)** — Wrangler config, bindings, Vite setup

### Chat & Streaming
- **[references/streaming-chat.md](references/streaming-chat.md)** — AIChatAgent, resumable streams, tools
- **[references/client-sdk.md](references/client-sdk.md)** — `useAgent`, `useAgentChat`, `AgentClient`
- **[references/server-driven-messages.md](references/server-driven-messages.md)** — Trigger patterns, `saveMessages`
- **[references/human-in-the-loop.md](references/human-in-the-loop.md)** — Approval flows, `needsApproval`

### Background Processing
- **[references/workflows.md](references/workflows.md)** — Durable Workflows integration
- **[references/durable-execution.md](references/durable-execution.md)** — `runFiber`, `stash`, surviving eviction
- **[references/queue-retries.md](references/queue-retries.md)** — Built-in queue, retry with backoff

### Integrations
- **[references/mcp.md](references/mcp.md)** — MCP client and server, transports, securing
- **[references/email.md](references/email.md)** — Email routing and handling
- **[references/webhooks-push.md](references/webhooks-push.md)** — Webhooks, push notifications
- **[references/observability.md](references/observability.md)** — Diagnostics-channel events

### Experimental
- **[references/think.md](references/think.md)** — `@cloudflare/think` higher-level chat agent
- **[references/voice.md](references/voice.md)** — `@cloudflare/voice` STT/TTS
- **[references/codemode.md](references/codemode.md)** — Code Mode for tool orchestration
- **[references/browse-the-web.md](references/browse-the-web.md)** — CDP browser tools
