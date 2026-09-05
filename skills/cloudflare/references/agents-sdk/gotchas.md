# Agents SDK Troubleshooting

Match the symptom to the maintained guidance before changing application code.

| Symptom or concern | Documentation |
|--------------------|---------------|
| State does not persist or sync; choosing state versus SQL | [Store and sync state](https://developers.cloudflare.com/agents/runtime/lifecycle/state/) |
| Chat history growth, tool execution, or stream recovery | [Chat agents](https://developers.cloudflare.com/agents/communication-channels/chat/chat-agents/) |
| Connection lifecycle or hibernation behavior | [WebSockets](https://developers.cloudflare.com/agents/runtime/communication/websockets/) |
| Client connection, RPC, or streaming errors | [Client SDK](https://developers.cloudflare.com/agents/communication-channels/chat/client-sdk/) and [callable methods](https://developers.cloudflare.com/agents/runtime/lifecycle/callable-methods/) |
| Agent not found or requests return 404 | [Routing](https://developers.cloudflare.com/agents/runtime/communication/routing/) |
| Missing class, generated types, secrets, or migration errors | [Configuration](https://developers.cloudflare.com/agents/runtime/operations/configuration/) |
| Scheduled or queued work behaves unexpectedly | [Schedule tasks](https://developers.cloudflare.com/agents/runtime/execution/schedule-tasks/) and [queue tasks](https://developers.cloudflare.com/agents/runtime/execution/queue-tasks/) |
| MCP connection, authentication, or lifecycle errors | [MCP client API](https://developers.cloudflare.com/agents/model-context-protocol/apis/client-api/) |
| Runtime capacity or quota questions | [Agents limits](https://developers.cloudflare.com/agents/platform/limits/) and its linked Workers/Durable Objects limits |

Use the state update API for synchronized data and SQL for data that does not need to be broadcast to every client. Check the chat guide's message management guidance before changing persisted conversation history.
