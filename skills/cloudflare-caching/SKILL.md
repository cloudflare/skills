---
name: cloudflare-caching
description: Implement and troubleshoot Cloudflare application and CDN caching, including Workers Cache, Cache Rules, cache keys, stale responses, misses, and scoped invalidation. Use when adding caching or diagnosing incorrect cached content on Cloudflare.
---

# Cloudflare Caching

Identify the cache serving the response before changing its policy. Read the current documentation linked for the relevant mechanism; inspect the project's pinned Wrangler version, configuration, and framework adapter before choosing syntax.

## Choose the cache boundary

- **Workers Cache** is the default for new application response caching. It can return a response before Worker code runs, and belongs to the Worker independently of zones. Zone Cache Rules and zone purges do not control it. Read [Workers Cache](https://developers.cloudflare.com/workers/cache/), [configuration](https://developers.cloudflare.com/workers/cache/configuration/), and [limitations](https://developers.cloudflare.com/workers/cache/limitations/) before enabling it. For caching inner computations while keeping an outer handler dynamic, consult the [entrypoint patterns](https://developers.cloudflare.com/workers/cache/examples/).
- **Zone CDN cache / Cache Rules** controls caching for proxied origins. Use [Cache Rules](https://developers.cloudflare.com/cache/how-to/cache-rules/) for eligibility and policy; use Cloudflare Trace from that guide to check whether the intended rule matches. Changing these rules does not fix Workers Cache behavior.
- **Cache API** (`caches.default` / named caches) runs inside Worker code and is independent of Workers Cache. Its contents and `delete()` are local to a data center; `put()` does not use tiered caching. Read the [Cache API](https://developers.cloudflare.com/workers/runtime-apis/cache/) when maintaining existing usage or a concrete requirement needs it. Check Workers Cache patterns and limitations before selecting Cache API or KV as an alternative.
- **Framework, browser, and service worker caches** can still serve stale results after Cloudflare invalidation. Inspect the installed framework/adapter's cache storage and revalidation path and fetch its current documentation. Do not assume framework tags or revalidation APIs invalidate either Cloudflare cache.

## Implement the reuse contract

Identify which requests may share a response, acceptable freshness, and what data change invalidates it. Account for browser freshness separately from shared-cache freshness.

For Workers Cache, follow the [cache-key guide](https://developers.cloudflare.com/workers/cache/cache-keys/): host and cookies do not partition the cache by default. Check all output-varying inputs, especially host-based tenants, language, and identity. Use a documented partitioning pattern such as a validated tenant in `ctx.props` on an inner entrypoint, or bypass shared caching. Keep authentication/authorization on a path that runs for every protected request; a cached outer entrypoint skips its handler. For the gateway pattern, disable caching on the outer entrypoint in configuration, as the entrypoint examples specify.

Set explicit cache policy on personalized responses, including errors and redirects. With Workers Cache enabled, omitting `Cache-Control` can still allow heuristic caching; `no-cache` means revalidation, not no storage. Do not remove `Set-Cookie` or add `public` merely to force hits: the [configuration guide](https://developers.cloudflare.com/workers/cache/configuration/) documents automatic bypass conditions and authorization exceptions. Verify the effective CDN-specific headers too.

Retain per-version isolation unless reuse across deployments is compatible with the response contract. If enabling cross-version caching, design invalidation for data and schema changes before doing so.

## Diagnose with evidence

Reproduce the actual request method, URL, relevant headers, and target environment. Compare repeated requests with stable inputs; record status, body identity, `CF-Cache-Status`, `Age` when present, effective cache-control headers, and Worker/origin execution evidence. Avoid logging tokens or private bodies.

Use [Workers Cache debugging](https://developers.cloudflare.com/workers/cache/debugging/) for Worker-owned responses and [CDN cache statuses](https://developers.cloudflare.com/cache/concepts/cache-responses/) for zone responses. Correlate subrequest evidence with the final response rather than interpreting a single header as proof for every layer.

- **Repeated misses or bypass:** Check enablement in the selected environment, supported invocation type, cacheability, and changing key inputs. A new Worker version starts cold by default. Cache API locality can explain different results from different locations.
- **Stale content:** Locate the first layer returning old data. Check TTL, revalidation, stale-serving policy, validators, and whether the origin or framework already returned stale content. A purge cannot repair an origin that repopulates the same old response.
- **Wrong user's or tenant's content:** Stop shared reuse on the affected path, repair the partition/bypass policy, and invalidate affected entries within the authorized scope. Verify isolation before restoring caching.

## Invalidate and verify

Match invalidation to the cache owner and key. Prefer the narrowest documented operation that covers the affected entries:

- [Workers Cache purging](https://developers.cloudflare.com/workers/cache/purge/) is scoped to the owning Worker and calling entrypoint. Choose tags or path prefixes with their actual match scope; a zone purge or a purge in a different entrypoint will not clear it.
- [Zone cache purging](https://developers.cloudflare.com/cache/how-to/purge-cache/) uses zone operations. For custom keys, consult the Cache Rules guide before assuming a URL-only purge covers all variants.
- Cache API deletion is local; consult its documentation for supported broader purge methods and custom-key restrictions.

Before a live purge, establish the target account, Worker/entrypoint or zone, environment, and affected content from the task's authorization. Do not broaden a failed targeted purge to purge-everything by default; inspect its scope and key mismatch first.

Verify a cold fill, repeated reuse, intended expiry/revalidation, and update/invalidation behavior. When personalization or tenancy is involved, test at least two distinct identities/tenants and the anonymous path. Separate local policy tests from deployed cache behavior; state which environment and cache layers were actually observed. Report the cause, focused change, evidence, and any remaining deployment or invalidation action.
