# GraphQL Analytics API Configuration

## Authentication

### API Token (Recommended)

Create a token with the appropriate analytics permission:

| Permission | Scope | Use Case |
|------------|-------|----------|
| **Account Analytics: Read** | Account-wide | Workers, R2, KV, D1, DO, AI, Network Analytics |
| **Zone Analytics: Read** | Per-zone | HTTP requests, Firewall, DNS, Load Balancing |
| **All zones - Analytics: Read** | All zones | Multi-zone HTTP/Firewall/DNS queries |

Create a token at: [dash.cloudflare.com > Account API Tokens](https://dash.cloudflare.com/?to=/:account/api-tokens)

```bash
# Verify token works
curl -s https://api.cloudflare.com/client/v4/graphql \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"query":"{ viewer { zones(filter: {zoneTag: \"YOUR_ZONE_ID\"}) { httpRequestsAdaptiveGroups(limit: 1, filter: {datetime_gt: \"2025-01-01T00:00:00Z\"}) { count } } } }"}'
```

### API Key + Email (Legacy)

Not recommended for new projects. Use API tokens instead.

```bash
curl -s https://api.cloudflare.com/client/v4/graphql \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: YOUR_GLOBAL_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"query":"{ viewer { zones(filter: {zoneTag: \"ZONE_ID\"}) { httpRequestsAdaptiveGroups(limit: 1, filter: {datetime_gt: \"2025-01-01T00:00:00Z\"}) { count } } } }"}'
```

## Client Setup

### curl

```bash
# Query with variables (recommended for complex queries)
curl -s https://api.cloudflare.com/client/v4/graphql \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "query": "query GetHTTPTraffic($zoneTag: string!, $start: Time!, $end: Time!) { viewer { zones(filter: {zoneTag: $zoneTag}) { httpRequestsAdaptiveGroups(filter: {datetime_gt: $start, datetime_lt: $end}, limit: 10, orderBy: [datetimeFiveMinutes_DESC]) { count dimensions { datetimeFiveMinutes } sum { edgeResponseBytes } } } } }",
    "variables": {
      "zoneTag": "YOUR_ZONE_ID",
      "start": "2025-01-01T00:00:00Z",
      "end": "2025-01-02T00:00:00Z"
    }
  }' | jq .
```

### TypeScript / JavaScript

```typescript
const CF_API_TOKEN = process.env.CF_API_TOKEN;
const GRAPHQL_ENDPOINT = "https://api.cloudflare.com/client/v4/graphql";

interface GraphQLResponse<T> {
  data: T | null;
  errors?: Array<{ message: string; path?: string[] }>;
}

async function queryGraphQL<T>(
  query: string,
  variables: Record<string, unknown> = {}
): Promise<T> {
  const response = await fetch(GRAPHQL_ENDPOINT, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${CF_API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const json: GraphQLResponse<T> = await response.json();

  // GraphQL can return 200 with errors
  if (json.errors?.length) {
    throw new Error(json.errors.map((e) => e.message).join("; "));
  }

  return json.data!;
}

// Usage
const data = await queryGraphQL(
  `query($zoneTag: string!, $start: Time!, $end: Time!) {
    viewer {
      zones(filter: { zoneTag: $zoneTag }) {
        httpRequestsAdaptiveGroups(
          filter: { datetime_gt: $start, datetime_lt: $end }
          limit: 100
          orderBy: [datetimeHour_DESC]
        ) {
          count
          dimensions { datetimeHour }
          sum { edgeResponseBytes }
        }
      }
    }
  }`,
  {
    zoneTag: "YOUR_ZONE_ID",
    start: "2025-01-01T00:00:00Z",
    end: "2025-01-02T00:00:00Z",
  }
);
```

### Python

```python
import requests
import os

CF_API_TOKEN = os.environ["CF_API_TOKEN"]
GRAPHQL_ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"

def query_graphql(query: str, variables: dict = None) -> dict:
    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers={
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"query": query, "variables": variables or {}},
    )
    response.raise_for_status()
    result = response.json()

    if result.get("errors"):
        raise Exception("; ".join(e["message"] for e in result["errors"]))

    return result["data"]

# Usage
data = query_graphql(
    """
    query($accountTag: string!, $start: Time!, $end: Time!) {
      viewer {
        accounts(filter: { accountTag: $accountTag }) {
          workersInvocationsAdaptive(
            filter: { datetime_gt: $start, datetime_lt: $end }
            limit: 100
            orderBy: [datetimeHour_DESC]
          ) {
            sum { requests errors }
            dimensions { datetimeHour scriptName }
            quantiles { cpuTimeP50 cpuTimeP99 }
          }
        }
      }
    }
    """,
    variables={
        "accountTag": "YOUR_ACCOUNT_ID",
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-01-02T00:00:00Z",
    },
)
```

### From a Cloudflare Worker

Workers can query the GraphQL API using a service token or API token stored in a secret:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const query = `
      query WorkerMetrics($accountTag: string!, $start: Time!, $end: Time!) {
        viewer {
          accounts(filter: { accountTag: $accountTag }) {
            workersInvocationsAdaptive(
              filter: { datetime_gt: $start, datetime_lt: $end }
              limit: 10
            ) {
              sum { requests errors }
              dimensions { scriptName }
            }
          }
        }
      }
    `;

    const now = new Date().toISOString();
    const oneDayAgo = new Date(Date.now() - 86400000).toISOString();

    const response = await fetch(
      "https://api.cloudflare.com/client/v4/graphql",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.CF_API_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          variables: {
            accountTag: env.ACCOUNT_ID,
            start: oneDayAgo,
            end: now,
          },
        }),
      }
    );

    const data = await response.json();
    return Response.json(data);
  },
};
```

## GraphQL API Explorer

The interactive explorer at [graphql.cloudflare.com](https://graphql.cloudflare.com/) provides:
- Schema documentation browser
- Autocomplete query editor
- Variable panel
- Response viewer
- Shareable query links

Authenticate in the explorer using your Cloudflare dashboard session (auto-detected).

## Schema Introspection

### Discover Available Datasets

```graphql
# List all zone-scoped datasets
{
  __type(name: "zone") {
    fields {
      name
      description
      args {
        name
        type { name kind }
      }
    }
  }
}

# List all account-scoped datasets
{
  __type(name: "account") {
    fields {
      name
      description
    }
  }
}
```

### Discover Dataset Fields

```graphql
# What dimensions are available on HTTP requests?
{
  __type(name: "ZoneHttpRequestsAdaptiveGroupsDimensions") {
    fields {
      name
      description
      type { name kind }
    }
  }
}

# What sum fields are available?
{
  __type(name: "ZoneHttpRequestsAdaptiveGroupsSum") {
    fields {
      name
      description
      type { name kind }
    }
  }
}

# What filter operators are available?
{
  __type(name: "ZoneHttpRequestsAdaptiveGroupsFilter_InputObject") {
    inputFields {
      name
      type { name kind }
    }
  }
}
```

### Discover Node Limits (Settings)

```graphql
{
  viewer {
    zones(filter: { zoneTag: "ZONE_ID" }) {
      settings {
        httpRequestsAdaptiveGroups {
          enabled
          maxDuration
          maxNumberOfFields
          maxPageSize
          notOlderThan
        }
      }
    }
  }
}
```

## Finding Your Zone and Account IDs

- **Zone ID**: Cloudflare Dashboard > select zone > Overview page (right sidebar) or via API
- **Account ID**: Cloudflare Dashboard > Account Home (URL contains account ID) or via API

```bash
# List zones
curl -s https://api.cloudflare.com/client/v4/zones \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, id}'

# List accounts
curl -s https://api.cloudflare.com/client/v4/accounts \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, id}'
```

## See Also

- [README.md](README.md) - Overview, decision tree, dataset index
- [api.md](api.md) - Query structure, aggregation fields, filtering operators
- [patterns.md](patterns.md) - Common query patterns (time-series, top-N, per-product)
- [gotchas.md](gotchas.md) - Rate limits, sampling, troubleshooting
