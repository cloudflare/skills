# DO Storage API

Check the class’s backend before choosing operations; storage APIs and recovery capabilities differ.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Use SQL cursors, bound parameters, supported SQL, or database size | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md) |
| Use synchronous or asynchronous key-value methods on SQLite | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md) |
| Maintain asynchronous KV operations on a legacy backend | [Legacy KV storage API](https://developers.cloudflare.com/durable-objects/api/legacy-kv-storage-api/index.md) |
| Review transactions, write coalescing, storage options, or cleanup | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md); [Legacy KV storage API](https://developers.cloudflare.com/durable-objects/api/legacy-kv-storage-api/index.md) |
| Create bookmarks or restore SQLite data | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md) |
| Schedule, inspect, or cancel an alarm | [Alarms](https://developers.cloudflare.com/durable-objects/api/alarms/index.md) |
