# Durable Objects API

Select the API for the object’s configured storage backend and communication path.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Implement constructors, RPC methods, or event handlers | [Base class](https://developers.cloudflare.com/durable-objects/api/base/); [Invoke methods](https://developers.cloudflare.com/durable-objects/best-practices/create-durable-object-stubs-and-send-requests/) |
| Create names, IDs, and stubs | [Namespace](https://developers.cloudflare.com/durable-objects/api/namespace/); [ID](https://developers.cloudflare.com/durable-objects/api/id/); [Stub](https://developers.cloudflare.com/durable-objects/api/stub/) |
| Control initialization, concurrency, lifecycle, or WebSocket state | [Durable Object State](https://developers.cloudflare.com/durable-objects/api/state/) |
| Read or write persistent data, use transactions, or restore backups | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/); [Legacy KV storage API](https://developers.cloudflare.com/durable-objects/api/legacy-kv-storage-api/) |
| Schedule and handle alarms | [Alarms](https://developers.cloudflare.com/durable-objects/api/alarms/) |
| Accept WebSockets and restore attachments | [Use WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/) |

See [configuration](configuration.md) and [troubleshooting](gotchas.md) for deployment and runtime issues.
