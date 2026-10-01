# DO Storage Configuration

Prefer SQLite for new classes. Inspect an existing class’s backend and lifecycle configuration before changing either.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Create a SQLite-backed class, binding, and generated types | [Getting started](https://developers.cloudflare.com/durable-objects/get-started/index.md) |
| Choose storage and manage class exports | [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/index.md) |
| Maintain legacy migration configuration | [Legacy class migrations](https://developers.cloudflare.com/durable-objects/reference/durable-object-class-migrations-legacy/index.md) |
| Initialize schemas or evolve application tables | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/index.md); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md) |
| Set placement hints or jurisdiction constraints | [Data location](https://developers.cloudflare.com/durable-objects/reference/data-location/index.md) |
| Configure CPU allowances and check storage constraints | [Limits](https://developers.cloudflare.com/durable-objects/platform/limits/index.md) |

A class configuration change is not an application-data migration. Check the documented backend transition constraints in [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/index.md) before planning a backend change.
