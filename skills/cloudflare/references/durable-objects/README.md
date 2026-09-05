# Cloudflare Durable Objects

Choose one object per entity that needs coordinated state. Keep essential data in durable storage; in-memory state must be reconstructible. Prefer SQLite for new classes, and inspect the backend of existing classes before selecting APIs. For idle WebSocket servers, prefer hibernation and plan for state restoration.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Create a Worker and Durable Object | [Getting started](https://developers.cloudflare.com/durable-objects/get-started/) |
| Design coordinated state and sharding | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/) |
| Select APIs | [API routing](api.md) |
| Configure bindings, classes, and placement | [Configuration routing](configuration.md) |
| Choose implementation patterns | [Pattern routing](patterns.md) |
| Diagnose failures and constraints | [Troubleshooting routing](gotchas.md) |
| Work on persistence or tests | [Storage reference](../do-storage/README.md); [Testing](../do-storage/testing.md) |

For focused Durable Objects work, use the [Durable Objects skill](../../../durable-objects/SKILL.md).
