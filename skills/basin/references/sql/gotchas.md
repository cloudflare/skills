# Basin SQL Gotchas

Operational pitfalls. For the authoritative list of supported features, unsupported features, and recommended workarounds, pull `https://developers.cloudflare.com/basin-sql/reference/limitations-best-practices/index.md` and `https://developers.cloudflare.com/basin-sql/troubleshooting/index.md`.

## Access

- **No Workers binding.** There is no `env.R2_SQL`. Query the REST endpoint via `fetch()` from a Worker ([patterns.md](patterns.md#dashboard-worker)), or use D1 / an external DB for OLTP.
- Wrangler needs `WRANGLER_BASIN_SQL_AUTH_TOKEN` — it does **not** reuse the `wrangler login` OAuth session.
- R2 Storage **Admin Read & Write is currently required even for read-only** queries. Verify this in the live authentication docs.

## Type Safety

```sql
-- ❌ wrong                          -- ✅ right
WHERE status = '200'                 WHERE status = 200
WHERE ts > '2026-01-01'              WHERE ts > '2026-01-01T00:00:00Z'   -- need time + tz
WHERE method = GET                   WHERE method = 'GET'
```

No implicit conversions. Timestamps must be RFC3339 with timezone; dates ISO 8601.

## Performance

- **File count dominates latency** — enable automatic compaction.
- **Partition-filter + narrow time windows + always `LIMIT`.**
- **Multi-way JOINs on large tables** can exceed resource limits — filter heavily, join through dimension tables.
- Per-query `metrics` (`files_scanned`, `bytes_scanned`, `cache_hits`) are the primary observability signal; `bytes_scanned` ≈ billable data. For LIMIT bounds, pagination, and other guidance, see the limitations-best-practices doc.

## Debug Checklist

1. `wrangler basin catalog enable <bucket>` — catalog on?
2. `echo $WRANGLER_BASIN_SQL_AUTH_TOKEN` — token set?
3. `SHOW DATABASES` → `SHOW TABLES IN ns` → `DESCRIBE ns.table`
4. `SELECT COUNT(*) FROM ns.table` — data present?
5. Add filters incrementally; read `metrics` to tune.

## See Also

- [api.md](api.md) · [patterns.md](patterns.md) · [configuration.md](configuration.md)
