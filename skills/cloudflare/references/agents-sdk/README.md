# Cloudflare Agents SDK

Use the Agents SDK when a Workers application needs persistent per-instance state, real-time clients, scheduled work, or AI chat. For focused SDK implementation or debugging, use the repository's [Agents SDK skill](../../../agents-sdk/SKILL.md) when available.

Read the linked Cloudflare documentation before writing code; check installed SDK versions when adapting an existing application.

## Choose the starting point

| Task | Documentation |
|------|---------------|
| Create an agent | [Quick start](https://developers.cloudflare.com/agents/getting-started/quick-start/) |
| Add agents to a Workers application | [Add to an existing project](https://developers.cloudflare.com/agents/getting-started/add-to-existing-project/) |
| AI chat with history, streaming, and tools | [Chat agents](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/) |
| Custom stateful logic or real-time collaboration | [Agents API](https://developers.cloudflare.com/agents/runtime/agents-api/) |
| Expose tools through MCP | [MCP handler APIs](https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/) |

## Task references

- [Configuration](configuration.md): bindings, deployment, request and email routing.
- [APIs](api.md): state, SQL, RPC, clients, and MCP integration.
- [Patterns](patterns.md): chat tools, collaboration, and background processing.
- [Troubleshooting](gotchas.md): persistence, connections, configuration errors, and limits.
