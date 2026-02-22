# GraphQL Analytics API Reference

## Query Root

The schema has a single entry point: `Query.viewer`. Mutations are not supported.

```graphql
{
  cost       # uint64 -- query cost (returned in response)
  viewer {
    budget   # uint64 -- remaining budget
    zones(filter: { zoneTag: "..." }) { ... }
    accounts(filter: { accountTag: "..." }) { ... }
    organizations(filter: { ... }) { ... }  # deprecated alias for accounts
  }
}
```

**Cost and Budget**: Select the top-level `cost` field in your query to see how much it consumed. `viewer.budget` shows remaining budget for the current window.

## Aggregation Fields

Aggregated dataset nodes return these field categories. Not every node has all categories — use introspection to check a specific dataset.

### count

Total number of events/records in the group. Available on `*Groups` nodes but **not** on all `*Adaptive` nodes (e.g., `workersInvocationsAdaptive` has no `count` — use `sum { requests }` instead). Not available on rollup tables.

```graphql
httpRequestsAdaptiveGroups(...) {
  count  # uint64
}
```

### sum

Cumulative metrics per group. Fields vary by dataset.

```graphql
# HTTP requests
sum {
  edgeResponseBytes   # uint64
  edgeRequestBytes    # uint64
  visits              # uint64 -- unique visits (different referer host)
  edgeTimeToFirstByteMs  # uint64
  originResponseDurationMs  # uint64
}

# Workers invocations
sum {
  requests            # uint64
  errors              # uint64
  subrequests         # uint64
  cpuTimeUs           # uint64 -- microseconds
  wallTime            # uint64 -- microseconds
  duration            # float64 -- GB*s
  responseBodySize    # uint64
  clientDisconnects   # uint64
  requestDuration     # float64 -- microseconds
}
```

### avg

Average values per group. Commonly includes `sampleInterval`.

```graphql
avg {
  sampleInterval  # float64 -- useful for understanding sampling resolution
}
```

### quantiles

Percentile distributions. Available on datasets like `workersInvocationsAdaptive`.

```graphql
quantiles {
  # CPU time percentiles (microseconds)
  cpuTimeP25   cpuTimeP50   cpuTimeP75
  cpuTimeP90   cpuTimeP95   cpuTimeP99   cpuTimeP999

  # Wall time percentiles (microseconds)
  wallTimeP25  wallTimeP50  wallTimeP75
  wallTimeP90  wallTimeP95  wallTimeP99  wallTimeP999

  # Request duration percentiles (microseconds)
  requestDurationP25  requestDurationP50  requestDurationP75
  requestDurationP90  requestDurationP95  requestDurationP99

  # Duration percentiles (GB*s)
  durationP25  durationP50  durationP75
  durationP90  durationP95  durationP99

  # Response body size percentiles (bytes)
  responseBodySizeP25  responseBodySizeP50  responseBodySizeP75
  responseBodySizeP90  responseBodySizeP95  responseBodySizeP99
}
```

### ratio

Status code ratios (0 to 1). Available on HTTP request datasets.

```graphql
ratio {
  status4xx   # float64 -- proportion of 4xx responses (0 to 1)
  status5xx   # float64 -- proportion of 5xx responses (0 to 1)
}
```

### uniq

Unique counts. Available on rollup datasets (`*1hGroups`, `*1dGroups`), **not** on Adaptive datasets.

```graphql
httpRequests1dGroups(filter: { ... }, limit: 30) {
  dimensions { date }
  uniq {
    uniques   # uint64 -- unique IP count for the period
  }
}
```

### confidence

Statistical confidence intervals for sampled data. Requires a `level` argument (decimal between 0 and 1).

```graphql
confidence(level: 0.95) {
  count {
    estimate    # estimated value
    lower       # lower bound
    upper       # upper bound
    sampleSize  # number of sampled data points
  }
  # Also available on sum fields
}
```

**Supported**: Only on `Adaptive` (sampled) datasets. Works on `sum` and `count` fields. If `sampleSize` is very small, the confidence interval may be unreliable.

## Dimensions

Dimensions are fields you can group by. They appear in the `dimensions` sub-selection. Common dimensions across datasets:

### Time Dimensions

All datasets support multiple time granularities:

| Dimension | Granularity | Example Value |
|-----------|------------|---------------|
| `date` | Day | `"2025-01-15"` |
| `datetime` | Exact timestamp | `"2025-01-15T10:30:45Z"` |
| `datetimeMinute` | 1 minute | `"2025-01-15T10:30:00Z"` |
| `datetimeFiveMinutes` | 5 minutes | `"2025-01-15T10:30:00Z"` |
| `datetimeFifteenMinutes` | 15 minutes | `"2025-01-15T10:30:00Z"` |
| `datetimeHour` | 1 hour | `"2025-01-15T10:00:00Z"` |

Workers datasets also support `datetimeSixHours`.

### HTTP Request Dimensions (httpRequestsAdaptiveGroups)

83 dimensions available. Key ones:

| Dimension | Type | Description |
|-----------|------|-------------|
| `clientCountryName` | string | Country of origin (e.g., `"US"`, `"GB"`) |
| `clientRequestHTTPHost` | string | Requested hostname |
| `clientRequestHTTPMethodName` | string | HTTP method (`GET`, `POST`, etc.) |
| `clientRequestPath` | string | URI path |
| `edgeResponseStatus` | uint16 | Edge HTTP status code |
| `originResponseStatus` | uint16 | Origin HTTP status code |
| `cacheStatus` | string | Cache status (`hit`, `miss`, `dynamic`, etc.) |
| `coloCode` | string | IATA code for the Cloudflare datacenter |
| `clientDeviceType` | string | Device type (desktop, mobile, etc.) |
| `clientAsn` | string | Client ASN |
| `clientIP` | string | Client IP address |
| `userAgent` | string | Full user agent string |
| `userAgentBrowser` | string | Parsed browser name |
| `userAgentOS` | string | Parsed OS name |
| `botScore` | uint8 | Bot management score (0-99) |
| `botScoreSrcName` | string | Bot detection source |
| `botManagementDecision` | string | Bot management verdict |
| `wafAttackScore` | uint8 | WAF attack score |
| `wafAttackScoreClass` | string | WAF score class |
| `securityAction` | string | Firewall action taken |
| `securitySource` | string | Firewall product that triggered |
| `ja3Hash` | string | TLS fingerprint (MD5) |
| `ja4` | string | JA4 TLS fingerprint |
| `clientSSLProtocol` | string | SSL/TLS version |
| `sampleInterval` | uint32 | ABR sample interval |
| `zoneTag` | string | Zone ID (for account-scoped queries) |

### Workers Dimensions (workersInvocationsAdaptive)

| Dimension | Type | Description |
|-----------|------|-------------|
| `scriptName` | string | Worker script name |
| `scriptTag` | string | Unique script tag |
| `scriptVersion` | string | Worker version |
| `environmentName` | string | Environment name |
| `status` | string | Invocation status |
| `usageModel` | string | Usage model (bundled/unbound) |
| `coloCode` | string | Datacenter IATA code |
| `dispatchNamespaceName` | string | Workers for Platforms namespace |
| `isDispatcher` | uint8 | Whether from a Dispatch Worker |

### Firewall Dimensions (firewallEventsAdaptive)

| Dimension | Type | Description |
|-----------|------|-------------|
| `action` | string | Action taken (block, challenge, etc.) |
| `source` | string | Security product source |
| `ruleId` | string | Rule ID that triggered |
| `clientCountryName` | string | Client country |
| `clientIP` | string | Client IP |
| `clientAsn` | string | Client ASN |
| `userAgent` | string | User agent |

## Filtering

Filters are GraphQL Input Objects that support Boolean algebra on fields.

### Scope Filters

```graphql
# Zone filter (up to 10 zones)
zones(filter: { zoneTag: "ZONE_ID" })
zones(filter: { zoneTag_in: ["ZONE_1", "ZONE_2"] })

# Account filter (exactly 1 account)
accounts(filter: { accountTag: "ACCOUNT_ID" })
```

### Dataset Filters

Applied at the dataset (node) level. **Always include a time range filter.**

```graphql
httpRequestsAdaptiveGroups(
  filter: {
    datetime_gt: "2025-01-01T00:00:00Z"
    datetime_lt: "2025-01-02T00:00:00Z"
    clientCountryName: "US"
  }
  limit: 1000
)
```

### Filter Operators

#### Scalar Operators (all scalar types)

| Operator | Meaning | Example |
|----------|---------|---------|
| (none) | equals | `clientCountryName: "US"` |
| `_gt` | greater than | `datetime_gt: "2025-01-01T00:00:00Z"` |
| `_lt` | less than | `datetime_lt: "2025-01-02T00:00:00Z"` |
| `_geq` | greater or equal | `datetime_geq: "2025-01-01T00:00:00Z"` |
| `_leq` | less or equal | `datetime_leq: "2025-01-31T23:59:59Z"` |
| `_neq` | not equal | `cacheStatus_neq: "hit"` |
| `_in` | in list | `clientCountryName_in: ["US", "GB", "DE"]` |
| `_notin` | not in list | `clientCountryName_notin: ["CN", "RU"]` |

#### String Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `_like` | SQL LIKE with `%` wildcard | `clientRequestPath_like: "/api/%"` |
| `_notlike` | negated LIKE | `clientRequestPath_notlike: "/health%"` |

> **Note:** `_notin` and `_notlike` are present in the GraphQL schema but not listed in the official Cloudflare docs. They work in practice (confirmed via introspection).

#### Array Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `_has` | array contains value | `botDetectionIds_has: "abc123"` |
| `_hasall` | contains all values | `contentScanObjResults_hasall: ["clean", "safe"]` |
| `_hasany` | contains any value | `botDetectionTags_hasany: ["likely_automated"]` |

### Boolean Operators (AND / OR)

Multiple filters at the same level are implicitly AND-ed. Use `AND` or `OR` explicitly for complex logic:

```graphql
# Implicit AND -- fields at same level are AND-ed
filter: {
  datetime_gt: "2025-01-01T00:00:00Z"
  clientCountryName: "US"
}
# Translates to: WHERE datetime > '...' AND clientCountryName = 'US'

# Explicit AND -- useful when combining multiple conditions on the same field
filter: {
  AND: [
    { datetime_gt: "2025-01-01T00:00:00Z" }
    { datetime_lt: "2025-01-02T00:00:00Z" }
    { clientCountryName: "US" }
  ]
}

# Explicit OR
filter: {
  OR: [
    { clientCountryName: "US" }
    { clientCountryName: "GB" }
  ]
}

# Nested AND within OR
filter: {
  datetime_gt: "2025-01-01T00:00:00Z"
  OR: [
    { edgeResponseStatus: 403 }
    { edgeResponseStatus: 429 }
  ]
}
```

## Pagination

The GraphQL Analytics API does **not** support cursor-based pagination. Use `limit`, `orderBy`, and filter-based offsets.

```graphql
# First page
httpRequestsAdaptiveGroups(
  filter: { datetime_gt: "2025-01-01T00:00:00Z" }
  limit: 100
  orderBy: [datetime_ASC]
) { ... }

# Next page: filter by last seen value
httpRequestsAdaptiveGroups(
  filter: {
    datetime_gt: "2025-01-01T01:35:00Z"  # last datetime from previous page
  }
  limit: 100
  orderBy: [datetime_ASC]
) { ... }
```

## Sorting

Use the `orderBy` argument with enum values in the format `field_ASC` or `field_DESC`:

```graphql
httpRequestsAdaptiveGroups(
  filter: { ... }
  limit: 100
  orderBy: [datetimeFiveMinutes_DESC]
)
```

Multiple sort fields are supported as an array: `orderBy: [date_ASC, clientCountryName_ASC]`.

## Introspection

Discover available datasets and their fields using standard GraphQL introspection:

```graphql
# List all fields on a zone
{
  __type(name: "zone") {
    fields {
      name
      description
    }
  }
}

# Get details of a specific dataset
{
  __type(name: "ZoneHttpRequestsAdaptiveGroups") {
    fields {
      name
      type { name kind }
    }
  }
}
```

## Settings Node

Query per-node limits and availability for your zone/account:

```graphql
{
  viewer {
    zones(filter: { zoneTag: "ZONE_ID" }) {
      settings {
        httpRequestsAdaptiveGroups {
          enabled
          maxDuration       # max time range (seconds)
          maxNumberOfFields
          maxPageSize
          notOlderThan      # max historical lookback (seconds)
        }
      }
    }
  }
}
```

## See Also

- [README.md](README.md) - Overview, decision tree, dataset index
- [configuration.md](configuration.md) - Authentication, client setup, introspection queries
- [patterns.md](patterns.md) - Common query patterns (time-series, top-N, per-product)
- [gotchas.md](gotchas.md) - Rate limits, sampling, troubleshooting
