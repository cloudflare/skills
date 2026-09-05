# Durable Objects Troubleshooting

Start with the observed failure and the object’s backend, deployment configuration, and connection type.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Lost memory, repeated constructors, timers, or unexpected shutdowns | [Object lifecycle](https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/); [Use WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/) |
| Overload, reset, or storage errors | [Troubleshooting](https://developers.cloudflare.com/durable-objects/observability/troubleshooting/); [Error handling](https://developers.cloudflare.com/durable-objects/best-practices/error-handling/) |
| CPU, storage, or request constraints | [Limits](https://developers.cloudflare.com/durable-objects/platform/limits/) |
| Failed class changes or destructive deletion semantics | [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/); [Legacy class migrations](https://developers.cloudflare.com/durable-objects/reference/durable-object-class-migrations-legacy/) |
| RPC routing or method availability | [Invoke methods](https://developers.cloudflare.com/durable-objects/best-practices/create-durable-object-stubs-and-send-requests/) |
| Alarm replacement, retries, and cleanup | [Alarms](https://developers.cloudflare.com/durable-objects/api/alarms/); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/) |
| Interleaving around external I/O or storage operations | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/) |
| Hibernation eligibility and connection state | [Use WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/); [Object lifecycle](https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/) |
