---
id: perf-001
name: Accelerate content delivery globally (CDN)
category: application-performance-delivery
description: Cache and deliver static and dynamic content from Cloudflare's global Anycast network of 330+ cities.
products: [CDN, Cache, Tiered Cache, Cache Reserve, Argo Smart Routing]
default_path: standard-cdn
aliases:
  - CDN setup
  - Global content delivery
  - Improve site response time
keywords:
  - "improve TTFB"
  - "Time To First Byte"
  - "make website faster"
  - "reduce origin egress"
  - "cache hit ratio"
  - "Argo Smart Routing"
  - "Cache Reserve"
related:
  - perf-002
  - perf-004
  - perf-005
---

# Accelerate content delivery globally (CDN)

## Ask first

**What type of content are you delivering?**
- Static assets (images, CSS, JS, fonts) → standard-cdn
- Dynamic HTML pages → standard-cdn
- Large files (video, software downloads) → large-file-delivery
- Mix of everything → standard-cdn (then layer in large-file-delivery as needed)

**Is minimizing origin egress cost a priority?**
- Yes, egress costs are a concern → egress-optimized
- No, performance is the priority → ttfb-optimization

## Paths

### standard-cdn (default)

For static assets and dynamic HTML:

1. Configure cache rules for the relevant content types
2. Enable Tiered Cache (Smart Tiered Cache or a custom topology)
3. Add cache rules for dynamic content where caching is safe
4. Set browser cache TTL for optimal client-side caching

### large-file-delivery

For large files (video, software downloads):

1. Enable Tiered Cache for better cache hit ratios
2. Enable Cache Reserve for persistent storage of large objects
3. Ensure range request support for resumable downloads

### egress-optimized

To minimize origin egress:

1. Enable Tiered Cache to reduce origin pulls
2. Enable Cache Reserve for persistent caching
3. Enable Argo Smart Routing for optimal paths back to origin when needed

### ttfb-optimization

To minimize Time To First Byte:

1. Maximize cache hit ratio with appropriate cache rules
2. Enable Tiered Cache to reduce origin pulls
3. Enable Argo Smart Routing for optimized network paths
4. Enable Early Hints (103) to preload critical resources
5. Review cache analytics to identify uncached content

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cache/, /argo-smart-routing/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
