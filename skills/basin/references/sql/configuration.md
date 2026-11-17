# Basin SQL Configuration

Auth and setup. For the current permission matrix and wrangler flags, pull `https://developers.cloudflare.com/basin-sql/reference/wrangler-commands/index.md` and the Basin Catalog manage-catalogs doc.

## Prerequisites

- R2 bucket with Basin Catalog enabled ([catalog/configuration.md](../catalog/configuration.md))
- R2 API token with **Basin Catalog** read, **R2 Storage Admin Read & Write**, and **Basin SQL** read permissions
- Wrangler CLI (for CLI queries)

> R2 Storage **Admin Read & Write is required even for read-only Basin SQL queries**. Verify the current permission list in [Query data](https://developers.cloudflare.com/basin-sql/query-data/index.md#authentication).

## Enable Catalog + Get Warehouse

```bash
npx wrangler basin catalog enable my-bucket
```

You query by **warehouse** name (`{ACCOUNT_ID}_{BUCKET}`), shown in the output alongside the Catalog URI.

## Configure Auth

### Wrangler CLI

```bash
export WRANGLER_BASIN_SQL_AUTH_TOKEN=<your-token>
# or a .env file in the project dir (auto-loaded): WRANGLER_BASIN_SQL_AUTH_TOKEN=<your-token>
```

> Wrangler does **not** use the `wrangler login` OAuth session for Basin SQL — the env var is required.

### REST API

```bash
curl -X POST \
  "https://api.sql.cloudflarestorage.com/api/v1/accounts/$ACCOUNT_ID/basin-sql/query/$BUCKET" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM default.my_table LIMIT 10"}'
```

## Verify Setup

```bash
npx wrangler basin sql query "${ACCOUNT_ID}_my-bucket" "SHOW DATABASES"
npx wrangler basin sql query "${ACCOUNT_ID}_my-bucket" "SHOW TABLES IN default"
```

## See Also

- [api.md](api.md) — SQL syntax · [patterns.md](patterns.md) — query examples · [gotchas.md](gotchas.md) — troubleshooting
