# Smart Placement Gotchas

## Common Errors

### "INSUFFICIENT_INVOCATIONS"

**Cause:** Not enough traffic for Smart Placement to analyze
**Solution:**
- Ensure Worker receives consistent global traffic
- Wait longer (analysis takes up to 15 minutes)
- Send test traffic from multiple global locations
- Check Worker has fetch event handler

### "UNSUPPORTED_APPLICATION"

**Cause:** Smart Placement made Worker slower rather than faster
**Reasons:**
- Worker doesn't make backend calls (runs faster at edge)
- Backend calls are cached (network latency to user more important)
- Backend service has good global distribution
- Worker mainly serves static assets or cached content

**Solutions:**
- Disable Smart Placement: `{ "placement": { "mode": "off" } }`
- Review whether Worker actually benefits from Smart Placement
- Consider caching strategy to reduce backend calls
- For Workers Static Assets apps with distinct edge and backend placement needs, consider a separate backend Worker

### "No request duration metrics"

**Cause:** Smart Placement not enabled, insufficient time passed, insufficient traffic, or analysis incomplete
**Solution:**
- Ensure Smart Placement enabled in config
- Wait 15+ minutes after deployment
- Verify Worker has sufficient traffic
- Check `placement_status` is `SUCCESS`

### "cf-placement header missing"

**Cause:** Smart Placement not enabled, beta feature removed, or Worker not analyzed yet
**Solution:** Verify Smart Placement enabled, wait for analysis (15min), check if beta feature still available

## Workers Static Assets + Smart Placement

**Problem:** Placement decisions do not match the desired split between edge-first asset handling and compute near a backend.

**Cause:** When Workers Static Assets uses `assets.run_worker_first`, Smart Placement places the entire Worker script as one unit. This setting belongs to Workers Static Assets, not Pages.

**Solution:** Measure request duration and choose asset-first routing, selective `run_worker_first` patterns, or separate Workers according to the workload:
```jsonc
// Review carefully: the whole Worker is placed as one unit
{
  "name": "full-stack-app",
  "placement": { "mode": "smart" },
  "assets": { "run_worker_first": true }
}

// Alternative: separate edge assets from placed backend compute
// frontend/wrangler.jsonc
{
  "name": "frontend",
  "assets": { "directory": "./dist" }
}

// backend/wrangler.jsonc
{
  "name": "backend-api",
  "placement": { "mode": "smart" }
}
```

Do not claim a guaranteed slowdown or a fixed performance multiplier; the live documentation describes this as a placement-model limitation whose impact depends on the application.

## Monolithic Full-Stack Worker

**Problem:** Frontend and backend logic in single Worker with Smart Placement enabled.

**Cause:** Smart Placement optimizes for backend latency but increases user-facing response time.

**Solution:** Split into two Workers:
```jsonc
// frontend/wrangler.jsonc
{
  "name": "frontend",
  "placement": { "mode": "off" },  // Explicit: stay at edge
  "services": [{ "binding": "BACKEND", "service": "backend-api" }]
}

// backend/wrangler.jsonc
{
  "name": "backend-api",
  "placement": { "mode": "smart" },
  "d1_databases": [{ "binding": "DB", "database_id": "xxx" }]
}
```

## Local Development Confusion

**Issue:** Smart Placement doesn't work in `wrangler dev`.

**Explanation:** Smart Placement only activates in production deployments, not local development.

**Solution:** Test Smart Placement in staging environment: `wrangler deploy --env staging`

## Baseline Traffic & Analysis Time

**Note:** Smart Placement routes 1% of requests WITHOUT optimization for comparison (expected).

**Analysis time:** Up to 15 minutes. During analysis, Worker runs at edge. Monitor `placement_status`.

## RPC Methods Not Affected (Critical Limitation)

**Problem:** Enabled Smart Placement on backend but RPC calls still slow.

**Cause:** Smart Placement ONLY affects `fetch` handlers. RPC methods (Service Bindings with `WorkerEntrypoint`) are NEVER affected.

**Why:** RPC bypasses `fetch` handler - Smart Placement can only route `fetch` requests.

**Solution:** Convert to fetch-based Service Bindings:

```typescript
// ❌ RPC - Smart Placement has NO EFFECT
export class BackendRPC extends WorkerEntrypoint {
  async getData() {
    // ALWAYS runs at edge
    return await this.env.DATABASE.prepare('SELECT * FROM table').all();
  }
}

// ✅ Fetch - Smart Placement WORKS
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Runs close to DATABASE when Smart Placement enabled
    const data = await env.DATABASE.prepare('SELECT * FROM table').all();
    return Response.json(data);
  }
}
```

## Requirements

- **Wrangler 2.20.0+** required
- **Consistent multi-region traffic** needed for analysis
- **Only affects fetch handlers** - RPC methods and named entrypoints not affected

## Limits

| Resource/Limit | Value | Notes |
|----------------|-------|-------|
| Analysis time | Up to 15 minutes | After enabling |
| Baseline traffic | 1% | Routed without optimization |
| Min Wrangler version | 2.20.0+ | Required |
| Traffic requirement | Multi-region | Consistent needed |

## Disabling Smart Placement

```jsonc
{ "placement": { "mode": "off" } }  // Explicit disable
// OR remove "placement" field entirely (same effect)
```

Both behaviors identical - Worker runs at edge closest to user.

## When NOT to Use Smart Placement

- Workers serving only static content or cached responses
- Workers without significant backend communication
- Pure edge logic (auth checks, redirects, simple transformations)
- Workers without fetch event handlers
- Workers Static Assets apps whose `run_worker_first` routing does not match whole-script placement
- Workers using RPC methods instead of fetch handlers

These scenarios won't benefit and may perform worse with Smart Placement.
