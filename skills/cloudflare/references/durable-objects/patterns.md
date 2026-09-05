# Durable Objects Patterns

Choose the coordination boundary first, then retrieve the relevant implementation guide.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Per-entity sharding, parent-child objects, caching, or schema initialization | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/) |
| RPC calls or HTTP forwarding | [Invoke methods](https://developers.cloudflare.com/durable-objects/best-practices/create-durable-object-stubs-and-send-requests/) |
| Counters and serialized state updates | [Build a counter](https://developers.cloudflare.com/durable-objects/examples/build-a-counter/); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/) |
| Chat, collaboration, and session state over WebSockets | [Use WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/); [Hibernation server example](https://developers.cloudflare.com/durable-objects/examples/websocket-hibernation-server/) |
| Batch work or schedule multiple events per object | [Alarms](https://developers.cloudflare.com/durable-objects/api/alarms/); [Batching example](https://developers.cloudflare.com/durable-objects/examples/alarms-api/) |
| Expire objects and clean up storage | [Time to Live example](https://developers.cloudflare.com/durable-objects/examples/durable-object-ttl/) |
| Design rate limiting or locking around consistent state | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/) |

For application-specific rate limiting, locks, and reconnection policies, derive the behavior from the application’s contract and the documented storage and lifecycle guarantees.
