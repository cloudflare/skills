# Hyperdrive configuration

See [README.md](./README.md) for the retrieval workflow. Fetch the relevant guide before creating or changing resources; use current configuration fields and CLI syntax from these sources.

| Task | Official documentation |
|------|------------------------|
| Create the first configuration and bind it to a Worker | [Get started](https://developers.cloudflare.com/hyperdrive/get-started/index.md) |
| Create, inspect, update, or delete configurations; set cache or pool options | [Wrangler commands](https://developers.cloudflare.com/hyperdrive/reference/wrangler-commands/index.md) |
| Generate TypeScript types from Worker configuration | [Workers TypeScript](https://developers.cloudflare.com/workers/languages/typescript/index.md) |
| Connect a private database using the recommended Workers VPC route | [Workers VPC integration](https://developers.cloudflare.com/hyperdrive/configuration/connect-to-private-database-vpc/index.md) |
| Maintain a private database connection using Tunnel and Access | [Tunnel integration](https://developers.cloudflare.com/hyperdrive/configuration/connect-to-private-database/index.md) |
| Configure database network access | [Firewall and networking](https://developers.cloudflare.com/hyperdrive/configuration/firewall-and-networking-configuration/index.md) |
| Configure server verification or client certificates | [SSL/TLS certificates](https://developers.cloudflare.com/hyperdrive/configuration/tls-ssl-certificates-for-hyperdrive/index.md) |
| Rotate origin database credentials | [Credential rotation](https://developers.cloudflare.com/hyperdrive/configuration/rotate-credentials/index.md) |
| Configure cache freshness or separate cached and fresh-read bindings | [Query caching](https://developers.cloudflare.com/hyperdrive/concepts/query-caching/index.md) |
| Budget origin connections across configurations | [Tune connection pooling](https://developers.cloudflare.com/hyperdrive/configuration/tune-connection-pool/index.md) |
| Choose local database access or remote Hyperdrive testing | [Local development](https://developers.cloudflare.com/hyperdrive/configuration/local-development/index.md) |
| Place compute near a regional database | [Placement Hints](https://developers.cloudflare.com/workers/configuration/placement/index.md#configure-explicit-placement-hints) |

## Setup decisions

- Identify the database engine, provider, and network path first. The [PostgreSQL](https://developers.cloudflare.com/hyperdrive/examples/connect-to-postgres/index.md) and [MySQL](https://developers.cloudflare.com/hyperdrive/examples/connect-to-mysql/index.md) indexes route to provider-specific instructions.
- For private connectivity, choose Workers VPC or the existing Tunnel/Access integration before configuring credentials. Follow the selected guide's prerequisites and TLS guidance.
- Decide which reads may be stale before selecting cache settings. Multiple configurations against one database contribute to its total origin connection usage.
- Local direct database access does not exercise Hyperdrive pooling or caching. Use the local-development guide's remote option when verifying those behaviors, and identify the database that option targets before running writes.

See [api.md](./api.md) for drivers and [gotchas.md](./gotchas.md) for diagnosis.

## Place compute near the database

Fetch [Workers placement](https://developers.cloudflare.com/workers/configuration/placement/index.md) before configuring a database-backed Worker. For multiple sequential queries to one regional database, prefer an explicit region hint over waiting for Smart Placement to learn from traffic. Hyperdrive pools origin connections; its binding does not automatically configure Worker placement.

- Establish the database's actual cloud provider and region from provider metadata or the user. The [Hyperdrive configuration API](https://developers.cloudflare.com/api/resources/hyperdrive/subresources/configs/methods/get/index.md) exposes origin connection information, not a cloud region. Do not treat the runtime binding's connection hostname as the database's location.
- For PlanetScale, identify the branch used by the Hyperdrive origin and confirm its region using the [branch API](https://planetscale.com/docs/api/reference/get_branch) or provider dashboard. Retrieve the [Postgres](https://developers.cloudflare.com/hyperdrive/examples/connect-to-postgres/postgres-database-providers/planetscale-postgres/index.md) or [MySQL](https://developers.cloudflare.com/hyperdrive/examples/connect-to-mysql/mysql-database-providers/planetscale/index.md) guide. For [global replica credentials](https://planetscale.com/blog/introducing-global-replica-credentials), assess multiple regions instead of guessing from a gateway hostname.
- When the region is known, set the explicit region hint in the project's existing configuration format. Retrieve the [CF configuration mapping](https://developers.cloudflare.com/cf/wrangler/reference/index.md) for `cloudflare.config.ts`, or use the installed Wrangler schema for Wrangler projects. Preserve existing placement choices; use one placement option per Worker.
- If location is missing, ask for the provider and region. For unknown or multiple back-end locations, discuss [Smart Placement](https://developers.cloudflare.com/workers/configuration/placement/index.md#enable-smart-placement) and its traffic requirements. Host-based placement is experimental and requires a suitable single-homed endpoint; do not automatically copy an arbitrary origin hostname into it.
- Check handler eligibility: placement affects fetch handlers, not RPC methods or named entrypoints. Verify request duration on deployed Workers with representative queries and caching. Local development does not validate production placement.
