# Agents SDK APIs

Use the current API documentation for signatures, imports, and examples. For chat UI APIs, read the chat guide as well as the general client SDK guide.

| Task | Documentation |
|------|---------------|
| Agent lifecycle and HTTP handlers | [Agents API](https://developers.cloudflare.com/agents/runtime/agents-api/) |
| Persist and synchronize state; query SQLite | [Store and sync state](https://developers.cloudflare.com/agents/runtime/lifecycle/state/) |
| Expose callable methods to clients | [Callable methods](https://developers.cloudflare.com/agents/runtime/lifecycle/callable-methods/) |
| Handle connections, broadcasts, and hibernation | [WebSockets](https://developers.cloudflare.com/agents/runtime/communication/websockets/) |
| Connect React or vanilla JavaScript clients; call RPC methods | [Client SDK](https://developers.cloudflare.com/agents/communication-channels/chat/client-sdk/) |
| Build a chat agent and UI with streaming and tools | [Chat agents](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/) |
| Consume external MCP tools and handle OAuth | [MCP client API](https://developers.cloudflare.com/agents/model-context-protocol/apis/client-api/) |
| Publish an MCP server | [MCP handler APIs](https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/) |

For new MCP servers, start with the current handler API. Before migrating an existing server, check installed packages and its state/session requirements against the handler documentation's migration guidance.

See [patterns.md](patterns.md) for scheduling, queues, Workflows, and email.
