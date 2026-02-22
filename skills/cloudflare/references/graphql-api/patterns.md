# GraphQL Analytics API Patterns & Best Practices

## Time-Series Queries

### Traffic Over Time (5-Minute Buckets)

```graphql
query TrafficTimeSeries($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 1000
        orderBy: [datetimeFiveMinutes_ASC]
      ) {
        count
        dimensions {
          datetimeFiveMinutes
        }
        sum {
          edgeResponseBytes
        }
      }
    }
  }
}
```

### Hourly Aggregation

Use `datetimeHour` for longer time ranges (days/weeks):

```graphql
query HourlyTraffic($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 500
        orderBy: [datetimeHour_ASC]
      ) {
        count
        dimensions { datetimeHour }
        sum { edgeResponseBytes edgeRequestBytes }
        ratio { status4xx status5xx }
      }
    }
  }
}
```

## Top-N Queries

### Top Countries by Request Count

```graphql
query TopCountries($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 10
        orderBy: [count_DESC]
      ) {
        count
        dimensions {
          clientCountryName
        }
      }
    }
  }
}
```

### Top Paths by Bandwidth

```graphql
query TopPathsByBandwidth($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 20
        orderBy: [sum_edgeResponseBytes_DESC]
      ) {
        count
        dimensions { clientRequestPath }
        sum { edgeResponseBytes }
      }
    }
  }
}
```

### Top Error Status Codes

```graphql
query TopErrors($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
          edgeResponseStatus_geq: 400
        }
        limit: 20
        orderBy: [count_DESC]
      ) {
        count
        dimensions {
          edgeResponseStatus
          clientRequestHTTPHost
          clientRequestPath
        }
      }
    }
  }
}
```

## Workers Analytics

### Worker Performance Overview

```graphql
query WorkersOverview($accountTag: string!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      workersInvocationsAdaptive(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 100
        orderBy: [sum_requests_DESC]
      ) {
        sum {
          requests
          errors
          subrequests
          wallTime
        }
        quantiles {
          cpuTimeP50
          cpuTimeP99
          wallTimeP50
          wallTimeP99
        }
        dimensions {
          scriptName
        }
      }
    }
  }
}
```

### Worker Error Rate Over Time

```graphql
query WorkerErrorRate($accountTag: string!, $scriptName: string!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      workersInvocationsAdaptive(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
          scriptName: $scriptName
        }
        limit: 500
        orderBy: [datetimeFiveMinutes_ASC]
      ) {
        sum { requests errors }
        dimensions { datetimeFiveMinutes status }
      }
    }
  }
}
```

### Worker CPU Time Distribution

```graphql
query WorkerCPUDistribution($accountTag: string!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      workersInvocationsAdaptive(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 50
        orderBy: [sum_requests_DESC]
      ) {
        dimensions { scriptName }
        quantiles {
          cpuTimeP50
          cpuTimeP75
          cpuTimeP95
          cpuTimeP99
        }
        sum { requests }
      }
    }
  }
}
```

## Firewall / Security

### Recent Firewall Events

```graphql
query RecentFirewallEvents($zoneTag: string!, $start: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      firewallEventsAdaptive(
        filter: { datetime_gt: $start }
        limit: 50
        orderBy: [datetime_DESC]
      ) {
        action
        source
        clientIP
        clientCountryName
        userAgent
        clientRequestHTTPHost
        clientRequestPath
        ruleId
        datetime
      }
    }
  }
}
```

### Firewall Blocks by Rule Over Time

```graphql
query FirewallBlocksByRule($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      firewallEventsAdaptiveGroups(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
          action: "block"
        }
        limit: 100
        orderBy: [count_DESC]
      ) {
        count
        dimensions {
          ruleId
          source
          datetimeHour
        }
      }
    }
  }
}
```

## DNS Analytics

### DNS Query Volume Over Time

```graphql
query DNSQueryVolume($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      dnsAnalyticsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 500
        orderBy: [datetimeFiveMinutes_ASC]
      ) {
        count
        dimensions { datetimeFiveMinutes }
      }
    }
  }
}
```

## Storage Analytics (Account-Scoped)

### R2 Operations

```graphql
query R2Operations($accountTag: string!, $start: Date!, $end: Date!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      r2OperationsAdaptiveGroups(
        filter: { date_geq: $start, date_leq: $end }
        limit: 100
        orderBy: [date_DESC]
      ) {
        dimensions {
          date
          bucketName
          actionType
        }
        sum { requests }
      }
    }
  }
}
```

### KV Operations

```graphql
query KVOperations($accountTag: string!, $start: Date!, $end: Date!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      kvOperationsAdaptiveGroups(
        filter: { date_geq: $start, date_leq: $end }
        limit: 100
        orderBy: [date_DESC]
      ) {
        sum { requests }
        dimensions { date actionType }
      }
    }
  }
}
```

### D1 Database Analytics

```graphql
query D1Analytics($accountTag: string!, $start: Date!, $end: Date!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      d1AnalyticsAdaptiveGroups(
        filter: { date_geq: $start, date_leq: $end }
        limit: 100
        orderBy: [date_DESC]
      ) {
        count
        dimensions { date databaseId }
        sum { readQueries writeQueries rowsRead rowsWritten }
      }
    }
  }
}
```

## Cache Analytics

### Cache Hit Ratio Over Time

```graphql
query CacheHitRatio($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      # Cached requests
      cached: httpRequestsAdaptiveGroups(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
          cacheStatus: "hit"
        }
        limit: 500
        orderBy: [datetimeHour_ASC]
      ) {
        count
        dimensions { datetimeHour }
      }
      # Total requests
      total: httpRequestsAdaptiveGroups(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
        }
        limit: 500
        orderBy: [datetimeHour_ASC]
      ) {
        count
        dimensions { datetimeHour }
      }
    }
  }
}
```

### Cache Status Breakdown

```graphql
query CacheStatusBreakdown($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 20
        orderBy: [count_DESC]
      ) {
        count
        dimensions { cacheStatus }
        sum { edgeResponseBytes }
      }
    }
  }
}
```

## Multi-Dataset Queries

A single request can query multiple datasets. This is efficient because it avoids extra HTTP round-trips:

```graphql
query DashboardOverview($zoneTag: string!, $start: Time!, $end: Time!) {
  viewer {
    zones(filter: { zoneTag: $zoneTag }) {
      # HTTP traffic summary
      httpTraffic: httpRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 1
      ) {
        count
        sum { edgeResponseBytes }
        ratio { status4xx status5xx }
      }
      # Firewall summary
      firewallEvents: firewallEventsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 5
        orderBy: [count_DESC]
      ) {
        count
        dimensions { action source }
      }
      # DNS summary
      dnsQueries: dnsAnalyticsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 1
      ) {
        count
      }
    }
  }
}
```

## AI & Gateway Analytics

### Workers AI Inference Metrics

```graphql
query AIInference($accountTag: string!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      aiInferenceAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 100
        orderBy: [datetimeHour_DESC]
      ) {
        count
        sum { totalInputTokens totalOutputTokens totalRequestBytesIn }
        dimensions { modelId datetimeHour }
      }
    }
  }
}
```

### AI Gateway Request Analytics

```graphql
query AIGatewayRequests($accountTag: string!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      aiGatewayRequestsAdaptiveGroups(
        filter: { datetime_gt: $start, datetime_lt: $end }
        limit: 100
        orderBy: [datetimeHour_DESC]
      ) {
        count
        dimensions { gateway provider model datetimeHour }
        sum { cachedTokensIn cachedTokensOut uncachedTokensIn uncachedTokensOut }
      }
    }
  }
}
```

## Best Practices

### Always Include Time Filters

Queries without time filters scan all available data and are slow/expensive:

```graphql
# GOOD: bounded time range
filter: { datetime_gt: "2025-01-01T00:00:00Z", datetime_lt: "2025-01-02T00:00:00Z" }

# BAD: no time filter -- will be slow and may hit limits
filter: { clientCountryName: "US" }
```

### Match Time Granularity to Range

| Time Range | Recommended Dimension | Why |
|------------|----------------------|-----|
| < 6 hours | `datetimeMinute` or `datetimeFiveMinutes` | High resolution, manageable row count |
| 6-48 hours | `datetimeFiveMinutes` or `datetimeFifteenMinutes` | Balance of resolution and volume |
| 2-14 days | `datetimeHour` | Reasonable number of data points |
| 14+ days | `date` | Prevents limit overflow |

### Use Aliases for Multiple Queries

GraphQL aliases let you query the same dataset multiple times with different filters:

```graphql
{
  viewer {
    zones(filter: { zoneTag: "..." }) {
      us: httpRequestsAdaptiveGroups(
        filter: { datetime_gt: "...", clientCountryName: "US" }
        limit: 1
      ) { count }
      gb: httpRequestsAdaptiveGroups(
        filter: { datetime_gt: "...", clientCountryName: "GB" }
        limit: 1
      ) { count }
    }
  }
}
```

### Request Only What You Need

Select only the fields you need. Requesting all dimensions and all aggregations wastes query budget:

```graphql
# GOOD: specific fields
sum { requests errors }
dimensions { scriptName datetimeHour }

# BAD: requesting everything when you only need request counts
sum { requests errors subrequests cpuTimeUs wallTime duration responseBodySize clientDisconnects requestDuration }
dimensions { scriptName scriptTag scriptVersion environmentName status usageModel coloCode dispatchNamespaceName isDispatcher date datetime datetimeMinute datetimeFiveMinutes datetimeFifteenMinutes datetimeHour datetimeSixHours }
```

## See Also

- [README.md](README.md) - Overview, decision tree, dataset index
- [api.md](api.md) - Query structure, aggregation fields, filtering operators
- [configuration.md](configuration.md) - Authentication, client setup, introspection queries
- [gotchas.md](gotchas.md) - Rate limits, sampling, troubleshooting
