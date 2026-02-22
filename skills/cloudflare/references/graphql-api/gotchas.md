# GraphQL Analytics API Gotchas & Troubleshooting

## Rate Limits

### Query Rate Limit

| Limit | Value |
|-------|-------|
| GraphQL queries per user | **Default 300 per 5 minutes** (max 320, varies by query cost; at least 1/second) |
| General API rate limit | 1200 requests per 5 minutes (shared across all API calls) |
| Zone scope per query | Up to **10 zones** |
| Account scope per query | Exactly **1 account** |

The GraphQL rate limit is separate from but additional to the general API rate limit. Exceeding either results in `HTTP 429 Too Many Requests` and blocks all API calls for 5 minutes.

Enterprise customers can contact support to raise limits.

### "429 Too Many Requests"

**Cause:** Exceeded rate limit (default 300 / max 320 GraphQL queries per 5 min, or 1200 total API calls / 5 min).

**Solution:**
- Batch multiple datasets into a single query using multi-dataset queries
- Cache results on your side
- Increase interval between queries
- Use the `cost` field in responses to monitor budget consumption

```graphql
# Check remaining budget
{ viewer { budget } }
```

## Sampling & Data Accuracy

### Adaptive Bit Rate (ABR) Sampling

Datasets with `Adaptive` in the name use adaptive sampling. This means:

- Results are **statistically representative**, not exact row-for-row
- Running the same query twice may return **slightly different numbers**
- Higher traffic = higher sampling rate = more accurate results
- Low-traffic periods or rare events may show more variance

**The `sampleInterval` dimension** indicates the sampling ratio. A value of `1` means no sampling (every event counted). A value of `10` means roughly 1-in-10 events were sampled and results are extrapolated.

```graphql
# Check sampling level in your results
dimensions { sampleInterval }
avg { sampleInterval }
```

### "My query returns different results each time"

**Cause:** ABR dynamically adjusts resolution based on query complexity and timing.

**Solution:**
- This is expected behavior for sampled datasets
- For high-confidence numbers, use `confidence(level: 0.95)`:

```graphql
httpRequestsAdaptiveGroups(filter: { ... }, limit: 1) {
  count
  confidence(level: 0.95) {
    count {
      estimate
      lower
      upper
      sampleSize
    }
  }
}
```

- For exact counts on smaller datasets, use rollup nodes (`httpRequests1hGroups`, `httpRequests1dGroups`) which are pre-aggregated without sampling

### Rollup vs. Adaptive Datasets

| Feature | Rollup (`*1hGroups`, `*1dGroups`) | Adaptive (`*AdaptiveGroups`) |
|---------|-----------------------------------|-----------------------------|
| Sampling | No (pre-aggregated) | Yes (ABR) |
| Flexibility | Fixed time buckets only | Any time granularity |
| Dimensions | Fewer | Many more |
| Accuracy | Exact | Statistical estimate |
| Best for | Simple totals, billing verification | Flexible analysis, debugging |

## Common Errors

### "Access denied" / "authentication error"

**Cause:** Token lacks required permission or wrong scope.

**Solution:**
- Account-scoped queries need **Account Analytics: Read**
- Zone-scoped queries need **Zone Analytics: Read** for that specific zone
- Verify token: `curl -s https://api.cloudflare.com/client/v4/user/tokens/verify -H "Authorization: Bearer $TOKEN"`

### "field not found" / "Cannot query field"

**Cause:** Wrong dataset name, field doesn't exist on this node, or wrong scope (zone vs. account).

**Solution:**
- Dataset names are case-sensitive and camelCase: `httpRequestsAdaptiveGroups` not `HttpRequestsAdaptiveGroups`
- Zone datasets go under `zones(...)`, account datasets under `accounts(...)`
- Use introspection to verify field names (see configuration.md)

### "filter is required" / empty results

**Cause:** Missing required filter (usually time range) or filter too broad.

**Solution:**
- Always include `datetime_gt` / `datetime_lt` (or `_geq` / `_leq`) in dataset filters
- For zone queries, ensure `zoneTag` is correct
- For account queries, ensure `accountTag` is correct

```graphql
# Always include time range
filter: {
  datetime_gt: "2025-01-01T00:00:00Z"
  datetime_lt: "2025-01-02T00:00:00Z"
}
```

### "limit is required" / "limit exceeds maximum"

**Cause:** Missing `limit` argument or exceeding the node's max page size.

**Solution:**
- Always specify `limit` on every dataset node
- Max limit varies by dataset (typically 10,000 for groups, 100 for raw events)
- Check node limits via the settings query (see configuration.md)

### "query is too complex" / "query exceeds budget"

**Cause:** Query requests too many fields, datasets, or covers too broad a time range.

**Solution:**
- Reduce time range
- Request fewer dimensions and metrics
- Query fewer datasets per request
- Break into multiple smaller queries
- Check `cost` and `budget` in responses to understand consumption

### 200 Response with Errors

The GraphQL API returns HTTP 200 even when queries fail. Always check the `errors` array:

```json
{
  "data": null,
  "errors": [
    {
      "message": "filter is required for httpRequestsAdaptiveGroups",
      "path": ["viewer", "zones", "0", "httpRequestsAdaptiveGroups"]
    }
  ]
}
```

**Always parse `response.errors` in addition to checking HTTP status.**

## Plan-Based Availability

### Dataset Availability

Not all datasets are available on all plans. Higher plans get:
- More datasets
- Longer historical data retention (`notOlderThan`)
- Wider time range per query (`maxDuration`)
- More fields per query (`maxNumberOfFields`)
- Larger page sizes (`maxPageSize`)

Use the settings introspection to discover what's available for your zone/account:

```graphql
{
  viewer {
    zones(filter: { zoneTag: "ZONE_ID" }) {
      settings {
        httpRequestsAdaptiveGroups {
          enabled
          maxDuration
          notOlderThan
          maxPageSize
          maxNumberOfFields
        }
      }
    }
  }
}
```

### "node is not available" / "node is disabled"

**Cause:** Dataset not available on your plan, or the product is not enabled for your account/zone.

**Solution:**
- Check `settings { <nodeName> { enabled } }` to verify availability
- Some datasets require specific product subscriptions (e.g., Network Analytics requires Magic Transit/Spectrum)
- Upgrade plan or enable the product

## DateTime & Timezone Handling

### All Times Are UTC

The API exclusively uses UTC. All datetime inputs and outputs are in ISO 8601 UTC format:

```
"2025-01-15T10:30:00Z"
```

There is no timezone parameter. Convert to/from local time in your application.

### Time Filters Are Start-Inclusive

Filtering uses event start timestamps. Requests that start within the filter window but end after it will be included.

```graphql
# This includes events that START between these times
filter: {
  datetime_geq: "2025-01-15T00:00:00Z"
  datetime_lt: "2025-01-16T00:00:00Z"
}
```

### Date vs. Time Fields

- `Date` type: `"2025-01-15"` (day granularity, used in `date_geq`, `date_leq`)
- `Time` type: `"2025-01-15T10:30:00Z"` (used in `datetime_gt`, `datetime_lt`)

Some datasets (e.g., KV, R2 storage) use `date` filters; others use `datetime`. Check the filter input type via introspection.

## Performance Tips

### Narrow Time Ranges

Queries over shorter time ranges are faster and cheaper:

```
# Fast: 1 day
datetime_gt: "2025-01-15T00:00:00Z", datetime_lt: "2025-01-16T00:00:00Z"

# Slow: 90 days
datetime_gt: "2024-10-15T00:00:00Z", datetime_lt: "2025-01-15T00:00:00Z"
```

### Avoid Selecting All Dimensions

Request only the dimensions you need for grouping. Each additional dimension increases query cost:

```graphql
# GOOD: only needed dimensions
dimensions { datetimeHour clientCountryName }

# BAD: all 83 HTTP dimensions
dimensions { clientCountryName clientRequestHTTPHost clientRequestHTTPMethodName clientRequestPath edgeResponseStatus originResponseStatus cacheStatus coloCode ... }
```

### Use Pre-Aggregated Rollups When Possible

For simple time-series without complex dimension breakdowns, rollup nodes are faster:

```graphql
# Faster for daily totals
httpRequests1dGroups(filter: { date_geq: "2025-01-01", date_leq: "2025-01-31" }) {
  dimensions { date }
  sum { requests pageViews }
  uniq { uniques }
}
```

### Batch Multiple Datasets Per Query

Instead of separate HTTP requests, combine datasets in one query:

```graphql
# One request, three datasets -- cheaper than three separate requests
{
  viewer {
    zones(filter: { zoneTag: "..." }) {
      http: httpRequestsAdaptiveGroups(...) { count }
      firewall: firewallEventsAdaptiveGroups(...) { count }
      dns: dnsAnalyticsAdaptiveGroups(...) { count }
    }
  }
}
```

## See Also

- [README.md](README.md) - Overview, decision tree, dataset index
- [api.md](api.md) - Query structure, aggregation fields, filtering operators
- [configuration.md](configuration.md) - Authentication, client setup, introspection queries
- [patterns.md](patterns.md) - Common query patterns (time-series, top-N, per-product)
