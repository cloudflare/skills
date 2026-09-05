# Smart Placement Configuration

## wrangler.jsonc Setup

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "placement": {
    "mode": "smart"
  }
}
```

## Placement Mode Values

| Mode | Behavior |
|------|----------|
| `"smart"` | Enable Smart Placement - automatic optimization based on traffic analysis |
| `"off"` | Explicitly disable Smart Placement - always run at edge closest to user |
| Not specified | Default behavior - run at edge closest to user (same as `"off"`) |

**Note:** Smart Placement vs Explicit Placement are separate features. Smart Placement (`mode: "smart"`) uses automatic analysis. For manual placement control, see explicit placement options (`region`, `host`, `hostname` fields - not covered in this reference).

## Frontend + Backend Split Configuration

### Frontend Worker (No Smart Placement)

```jsonc
// frontend-worker/wrangler.jsonc
{
  "name": "frontend",
  "main": "frontend-worker.ts",
  // No "placement" - runs at edge
  "services": [
    {
      "binding": "BACKEND",
      "service": "backend-api"
    }
  ]
}
```

### Backend Worker (Smart Placement Enabled)

```jsonc
// backend-api/wrangler.jsonc
{
  "name": "backend-api",
  "main": "backend-worker.ts",
  "placement": {
    "mode": "smart"
  },
  "d1_databases": [
    {
      "binding": "DATABASE",
      "database_id": "xxx"
    }
  ]
}
```

## Requirements & Limitations

### Requirements
- **Wrangler version:** 2.20.0+
- **Analysis time:** Up to 15 minutes
- **Traffic requirements:** Consistent multi-location traffic
- **Workers plan:** All plans (Free, Paid, Enterprise)

### What Smart Placement Affects

**CRITICAL LIMITATION - Smart Placement ONLY Affects `fetch` Handlers:**

Smart Placement is fundamentally limited to Workers with default `fetch` handlers. This is a key architectural constraint.

- ✅ **Affects:** `fetch` event handlers ONLY (the default export's fetch method)
- ❌ **Does NOT affect:** 
  - RPC methods (Service Bindings with `WorkerEntrypoint` - see example below)
  - Named entrypoints (exports other than `default`)
  - Workers without `fetch` handlers
  - Queue consumers, scheduled handlers, or other event types

**Example - Smart Placement ONLY affects `fetch`:**
```typescript
// ✅ Smart Placement affects this:
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // This runs close to backend when Smart Placement enabled
    const data = await env.DATABASE.prepare('SELECT * FROM users').all();
    return Response.json(data);
  }
}

// ❌ Smart Placement DOES NOT affect these:
export class MyRPC extends WorkerEntrypoint {
  async myMethod() { 
    // This ALWAYS runs at edge, Smart Placement has NO EFFECT
    const data = await this.env.DATABASE.prepare('SELECT * FROM users').all();
    return data;
  }
}

export async function scheduled(event: ScheduledEvent, env: Env) {
  // NOT affected by Smart Placement
}
```

**Consequence:** If your backend logic uses RPC methods (`WorkerEntrypoint`), Smart Placement cannot optimize those calls. You must use fetch-based patterns for Smart Placement to work.

**Solution:** Convert RPC methods to fetch endpoints, or use a wrapper Worker with `fetch` handler that calls your backend RPC (though this adds latency).

### Baseline Traffic
Smart Placement automatically routes 1% of requests WITHOUT optimization as baseline for performance comparison.

### Validation Rules

**Mutually exclusive fields:**
- `mode` cannot be used with explicit placement fields (`region`, `host`, `hostname`)
- Choose either Smart Placement OR explicit placement, not both

```jsonc
// ✅ Valid - Smart Placement
{ "placement": { "mode": "smart" } }

// ✅ Valid - Explicit Placement (different feature)
{ "placement": { "region": "us-east1" } }

// ❌ Invalid - Cannot combine
{ "placement": { "mode": "smart", "region": "us-east1" } }
```

## Dashboard Configuration

**Workers & Pages** → Select Worker → **Settings** → **General** → **Placement: Smart** → Wait 15min → Check **Metrics**

## TypeScript Types

```typescript
interface Env {
  BACKEND: Fetcher;
  DATABASE: D1Database;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const data = await env.DATABASE.prepare('SELECT * FROM table').all();
    return Response.json(data);
  }
} satisfies ExportedHandler<Env>;
```

## Workers Static Assets and `run_worker_first`

`assets.run_worker_first` is a Workers Static Assets setting, not a Pages setting. When it is combined with Smart Placement, the entire Worker script is placed as one unit. Placement therefore may not reflect the intended split between edge-first asset handling and compute located near a backend.

Choose based on the application's routing needs and measured request duration:

1. Prefer the default asset-first behavior when the Worker does not need to inspect matching asset requests.
2. Use selective `run_worker_first` route patterns when only specific paths require the Worker.
3. If edge and backend work have different placement needs, consider separate frontend and backend Workers.
4. Keep `run_worker_first: true` when middleware must run for every asset request, but validate the resulting placement rather than assuming it will help or hurt.

```jsonc
// Review carefully: the whole Worker is placed as one unit
{
  "name": "full-stack-app",
  "placement": { "mode": "smart" },
  "assets": { "run_worker_first": true }
}

// Alternative when frontend and backend have different placement needs
// frontend-worker/wrangler.jsonc
{
  "name": "frontend",
  "assets": { "directory": "./dist" }
}

// backend-worker/wrangler.jsonc
{
  "name": "backend-api",
  "placement": { "mode": "smart" },
  "d1_databases": [{ "binding": "DB", "database_id": "xxx" }]
}
```

**Key takeaway:** Treat Smart Placement plus `run_worker_first` as a whole-script placement trade-off and measure it. Do not describe degradation as guaranteed.

## Local Development

Smart Placement does NOT work in `wrangler dev` (local only). Test by deploying: `wrangler deploy --env staging`
