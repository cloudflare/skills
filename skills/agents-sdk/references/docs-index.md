# Agents SDK documentation index

Open the page for the current task.

| Topic | Docs URL | Use for |
|-------|----------|---------|
| Getting started | [Quick start](https://developers.cloudflare.com/agents/getting-started/quick-start/) | First agent, project setup |
| Adding to existing project | [Add to existing project](https://developers.cloudflare.com/agents/getting-started/add-to-existing-project/) | Install into existing Workers app |
| Configuration | [Configuration](https://developers.cloudflare.com/agents/api-reference/configuration/) | `wrangler.jsonc`, bindings, assets, deployment |
| Agent class | [Agents API](https://developers.cloudflare.com/agents/api-reference/agents-api/) | Agent lifecycle, patterns, pitfalls |
| State | [Store and sync state](https://developers.cloudflare.com/agents/api-reference/store-and-sync-state/) | `setState`, `validateStateChange`, persistence |
| Routing | [Routing](https://developers.cloudflare.com/agents/api-reference/routing/) | URL patterns, `routeAgentRequest` |
| Callable methods | [Callable methods](https://developers.cloudflare.com/agents/api-reference/callable-methods/) | `@callable`, RPC, streaming, timeouts |
| Scheduling | [Schedule tasks](https://developers.cloudflare.com/agents/api-reference/schedule-tasks/) | `schedule()`, `scheduleEvery()`, cron |
| Workflows | [Run workflows](https://developers.cloudflare.com/agents/api-reference/run-workflows/) | `AgentWorkflow`, durable multi-step tasks |
| HTTP/WebSockets | [WebSockets](https://developers.cloudflare.com/agents/api-reference/websockets/) | Lifecycle hooks, hibernation |
| Chat agents | [Chat agents](https://developers.cloudflare.com/agents/api-reference/chat-agents/) | `AIChatAgent`, streaming, tools, persistence |
| Client SDK | [Client SDK](https://developers.cloudflare.com/agents/api-reference/client-sdk/) | `useAgent`, `useAgentChat`, React hooks |
| Client tools | [Client tools](https://developers.cloudflare.com/agents/api-reference/client-tools/) | Client-side tools, `autoContinueAfterToolResult` |
| Server-driven messages | [Trigger patterns](https://developers.cloudflare.com/agents/api-reference/trigger-patterns/) | `saveMessages`, `waitUntilStable`, server-initiated turns |
| Resumable streaming | [Resumable streaming](https://developers.cloudflare.com/agents/api-reference/resumable-streaming/) | Stream recovery on disconnect |
| Email | [Email](https://developers.cloudflare.com/agents/api-reference/email/) | Email routing, secure reply resolver |
| MCP client | [MCP client](https://developers.cloudflare.com/agents/api-reference/mcp-client-api/) | Connecting to MCP servers |
| MCP server | [MCP server](https://developers.cloudflare.com/agents/api-reference/mcp-agent-api/) | Building MCP servers with `McpAgent` |
| MCP transports | [MCP transports](https://developers.cloudflare.com/agents/api-reference/mcp-transports/) | Streamable HTTP, SSE, RPC transport options |
| Securing MCP servers | [Securing MCP](https://developers.cloudflare.com/agents/api-reference/securing-mcp-servers/) | OAuth, proxy MCP, hardening |
| Human-in-the-loop | [Human-in-the-loop](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) | Approval flows, `needsApproval`, workflows |
| Durable execution | [Durable execution](https://developers.cloudflare.com/agents/api-reference/durable-execution/) | `runFiber()`, `stash()`, surviving DO eviction |
| Queue | [Queue](https://developers.cloudflare.com/agents/api-reference/queue-tasks/) | Built-in FIFO queue, `queue()` |
| Retries | [Retries](https://developers.cloudflare.com/agents/api-reference/retries/) | `this.retry()`, backoff/jitter |
| Observability | [Observability](https://developers.cloudflare.com/agents/api-reference/observability/) | Diagnostics-channel events |
| Push notifications | [Push notifications](https://developers.cloudflare.com/agents/api-reference/push-notifications/) | Web Push + VAPID from agents |
| Webhooks | [Webhooks](https://developers.cloudflare.com/agents/api-reference/webhooks/) | Receiving external webhooks |
| Cross-domain auth | [Cross-domain auth](https://developers.cloudflare.com/agents/api-reference/cross-domain-authentication/) | WebSocket auth, tokens, CORS |
| Readonly connections | [Readonly](https://developers.cloudflare.com/agents/api-reference/readonly-connections/) | `shouldConnectionBeReadonly` |
| Voice | [Voice](https://developers.cloudflare.com/agents/api-reference/voice/) | Experimental STT/TTS, `withVoice` |
| Browse the web | [Browser tools](https://developers.cloudflare.com/agents/api-reference/browse-the-web/) | Experimental CDP browser automation |
| Think | [Think](https://developers.cloudflare.com/agents/api-reference/think/) | Experimental higher-level chat agent class |
| Migrations | [AI SDK v5](https://developers.cloudflare.com/agents/guides/migration-to-ai-sdk-v5/), [AI SDK v6](https://developers.cloudflare.com/agents/guides/migration-to-ai-sdk-v6/) | Upgrading `@cloudflare/ai-chat` |
