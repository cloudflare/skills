# Basin SQL

Serverless, distributed, **read-only** query engine (Apache DataFusion) for Apache Iceberg tables in Basin Catalog.

## Documentation

For full function lists, data types, and pricing, **retrieve the live docs** — use the Cloudflare MCP `docs` tool if available, otherwise `webfetch`.

| Topic | URL |
|-------|-----|
| Overview / get started | `https://developers.cloudflare.com/basin-sql/get-started/index.md` |
| Query data | `https://developers.cloudflare.com/basin-sql/query-data/index.md` |
| SQL reference | `https://developers.cloudflare.com/basin-sql/sql-reference/index.md` |
| Aggregate functions | `https://developers.cloudflare.com/basin-sql/sql-reference/aggregate-functions/index.md` |
| Scalar functions | `https://developers.cloudflare.com/basin-sql/sql-reference/scalar-functions/index.md` |
| Complex types | `https://developers.cloudflare.com/basin-sql/sql-reference/complex-types/index.md` |
| Limitations & best practices | `https://developers.cloudflare.com/basin-sql/reference/limitations-best-practices/index.md` |
| Wrangler commands | `https://developers.cloudflare.com/basin-sql/reference/wrangler-commands/index.md` |
| Pricing | `https://developers.cloudflare.com/basin-sql/platform/pricing/index.md` |

## Connection Values

| Value | Format |
|-------|--------|
| REST endpoint | `https://api.sql.cloudflarestorage.com/api/v1/accounts/{ACCOUNT_ID}/basin-sql/query/{BUCKET}` |
| Wrangler | `npx wrangler basin sql query "{WAREHOUSE}" "<SQL>"` with `WRANGLER_BASIN_SQL_AUTH_TOKEN` set |
| Warehouse | `{ACCOUNT_ID}_{BUCKET}` |

> The REST endpoint is `api.sql.cloudflarestorage.com` — **not** the account API host. The legacy `/r2-sql/query/` path may still work, but use `/basin-sql/query/` for new integrations.

## Quick Start

```bash
npx wrangler basin catalog enable my-bucket           # 1. enable catalog
export WRANGLER_BASIN_SQL_AUTH_TOKEN=<r2-token>              # 2. auth (Admin R&W + Basin SQL Read)
npx wrangler basin sql query "$ACCOUNT_ID"_my-bucket \
  "SELECT * FROM default.my_table LIMIT 10"                # 3. query
```

## SQL Surface

Basin SQL is read-only and supports a broad analytical SQL surface (SELECT, JOINs, subqueries, CTEs, set operations, window functions, and aggregate/scalar/JSON functions over complex types). For the authoritative, current list of supported syntax, functions, and limitations, see the SQL reference and limitations docs linked above. [api.md](api.md) has query templates.

## When to Use

**Use for:** SQL analytics over Iceberg (logs, BI, fraud, ad-hoc), multi-cloud queries without egress, dashboards (query from a Worker via HTTP).

**Don't use for:** writes (use PySpark/PyIceberg) or real-time OLTP (<100 ms).

## No Workers Binding

There is no `env.R2_SQL` binding. Query from a Worker via `fetch()` to the REST endpoint with the token as a secret (see [patterns.md](patterns.md#dashboard-worker)).

## Reading Order

1. [configuration.md](configuration.md) — enable catalog, tokens, env setup
2. [api.md](api.md) — SQL syntax templates, JOIN/window examples, response format, data types
3. [patterns.md](patterns.md) — CLI/REST/Worker queries, use cases, pagination, performance
4. [gotchas.md](gotchas.md) — what works vs. not, performance, troubleshooting

## See Also

- [Basin Catalog](../catalog/) — PyIceberg/PySpark, table management
- [Basin Pipelines](../pipelines/) — streaming ingest into queryable tables
