# Agents SDK Patterns

Choose the workflow first, then read its current implementation guide.

| Task | Documentation |
|------|---------------|
| AI chat with server tools, client tools, or tool approvals | [Chat agents](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/) |
| Custom WebSocket protocols, presence, and collaboration | [WebSockets](https://developers.cloudflare.com/agents/runtime/communication/websockets/) and [state synchronization](https://developers.cloudflare.com/agents/runtime/lifecycle/state/) |
| Execute work at a future time or on a recurring schedule | [Schedule tasks](https://developers.cloudflare.com/agents/runtime/execution/schedule-tasks/) |
| Process asynchronous tasks in an agent's built-in queue | [Queue tasks](https://developers.cloudflare.com/agents/runtime/execution/queue-tasks/) |
| Durable multi-step background processing | [Run Workflows](https://developers.cloudflare.com/agents/runtime/execution/run-workflows/) |
| Wait for human input or approval in durable work | [Human-in-the-loop patterns](https://developers.cloudflare.com/agents/concepts/agentic-patterns/human-in-the-loop/) |
| Process inbound email and send replies | [Email](https://developers.cloudflare.com/agents/communication-channels/email/) |

Use the chat abstraction for managed conversation history and streaming; use the base Agent for custom state and protocols. Scheduling, queued processing, and durable Workflows address different execution needs; choose using the linked guides.
