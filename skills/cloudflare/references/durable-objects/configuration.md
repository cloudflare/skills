# Durable Objects Configuration

Inspect existing bindings, storage backends, and class lifecycle configuration before changing deployment settings.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Create bindings, generate types, develop, and deploy | [Getting started](https://developers.cloudflare.com/durable-objects/get-started/) |
| Create, rename, delete, or transfer classes using declarative exports | [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/) |
| Maintain a Worker using the migrations array | [Legacy class migrations](https://developers.cloudflare.com/durable-objects/reference/durable-object-class-migrations-legacy/) |
| Move from migrations to exports | [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/) |
| Choose jurisdiction restrictions or placement hints | [Data location](https://developers.cloudflare.com/durable-objects/reference/data-location/) |
| Separate staging, production, and local development | [Environments](https://developers.cloudflare.com/durable-objects/reference/environments/) |
| Configure CPU allowances or check resource constraints | [Limits](https://developers.cloudflare.com/durable-objects/platform/limits/) |

Class lifecycle configuration and application SQL schema migrations are different tasks; see [patterns](patterns.md) for schema initialization.
