# Basin Pipelines

Streaming ingest: receive events over HTTP/Workers/Logpush, transform with SQL, write to R2 as Iceberg tables or Parquet/JSON files.

## Documentation

This reference is a fast-start with verified code and gotchas. For limits, settings, full SQL syntax, and pricing, **retrieve the live docs** — use the Cloudflare MCP `docs` tool if available, otherwise `webfetch` the URL. Docs are source of truth over this file.

| Topic | URL |
|-------|-----|
| Overview / getting started | `https://developers.cloudflare.com/basin-pipelines/getting-started/index.md` |
| Streams (write, manage, Logpush) | `https://developers.cloudflare.com/basin-pipelines/streams/index.md` |
| Sinks | `https://developers.cloudflare.com/basin-pipelines/sinks/index.md` |
| Basin Pipelines & SQL transforms | `https://developers.cloudflare.com/basin-pipelines/pipelines/index.md` |
| SQL reference (statements, types) | `https://developers.cloudflare.com/basin-pipelines/sql-reference/index.md` |
| Wrangler commands | `https://developers.cloudflare.com/basin-pipelines/reference/wrangler-commands/index.md` |
| Terraform | `https://developers.cloudflare.com/basin-pipelines/reference/terraform/index.md` |
| Limits | `https://developers.cloudflare.com/basin-pipelines/platform/limits/index.md` |
| Pricing | `https://developers.cloudflare.com/basin-pipelines/platform/pricing/index.md` |
| Metrics (GraphQL) | `https://developers.cloudflare.com/basin-pipelines/observability/metrics/index.md` |

## Three Components

```
Sources → Stream → Pipeline (SQL) → Sink → R2
          ↑          ↓                 ↓
   HTTP / Workers / Transform     Iceberg (Basin Catalog)
   Logpush          (row-level)   or Parquet/JSON files
```

| Component | Purpose |
|-----------|---------|
| **Stream** | Receives events (HTTP endpoint, Worker binding, or Logpush). Structured (schema-validated) or unstructured. |
| **Pipeline** | SQL connecting a stream to a sink. Row-level transforms only — no GROUP BY/aggregation. |
| **Sink** | Writes to R2 — Iceberg via Basin Catalog, or raw Parquet/JSON. |

**Status:** The linked docs PR proposes Basin general availability. Verify current availability, limits, and pricing in the live docs before making claims or sizing workloads.

## Quick Start

```bash
# Interactive — creates stream + sink + pipeline, optionally bucket + catalog
npx wrangler basin pipelines setup
```

Minimal Worker producer:
```typescript
interface Env { MY_STREAM: Pipeline; }

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    ctx.waitUntil(env.MY_STREAM.send([{ event_id: crypto.randomUUID(), amount: 29.99 }]));
    return new Response("OK");
  }
} satisfies ExportedHandler<Env>;
```

## Which Sink Type?

```
Need SQL queries / ACID / time-travel on the data?
  → Basin Catalog (Iceberg)   ✅ Basin SQL, schema evolution   ❌ more setup

Just archival / external tools (Spark, Athena)?
  → R2 raw files (Parquet/JSON) ✅ simple, partitioned files  ❌ no built-in SQL
```

## Critical Behaviors (read before building)

These are non-obvious and prevent most failures — see [gotchas.md](gotchas.md) for detail.

- **Everything is immutable after creation** — stream schema, pipeline SQL, sink config. To change, delete and recreate.
- **Sinks create their own table** — they cannot target an existing Iceberg table.
- **`__ingest_ts` is added automatically** (TIMESTAMP, partitioned by day). Don't define it in your schema.
- **Data isn't queryable immediately** — first flush takes **3–7 minutes** (warm-up + table creation) even with a short roll interval.
- **Schema validation is deferred** — invalid events are accepted then silently dropped. Monitor via GraphQL error metrics.
- **Binding field renamed `pipeline` → `stream`** (June 2026); old field still accepted.

## Reading Order

1. [configuration.md](configuration.md) — schema, streams, sinks, pipelines (CLI + REST + Terraform), bindings
2. [api.md](api.md) — `send()`, HTTP ingest, REST API, pipeline SQL, lifecycle states
3. [patterns.md](patterns.md) — fire-and-forget, validation, Logpush, observability, end-to-end
4. [gotchas.md](gotchas.md) — silent drops, immutability, REST≠CLI field names

## See Also

- [Basin Catalog](../catalog/) — Iceberg sink destination
- [Basin SQL](../sql/) — query the ingested data
- [r2](https://developers.cloudflare.com/r2/index.md) · [queues](https://developers.cloudflare.com/queues/index.md) · [workers](https://developers.cloudflare.com/workers/index.md)
