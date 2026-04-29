---
id: obs-005
name: See how your application is performing and what to fix
category: observability-analytics
description: Get a complete picture of your application's speed, availability, and errors in one place — without jumping between multiple product dashboards.
products: [Analytics, Speed, Cache, Health Checks, Load Balancing]
default_path: speed-diagnostics
aliases:
  - App performance overview
  - Performance monitoring dashboard
  - End-to-end application health
  - Single pane of glass for performance
keywords:
  - "why is my site slow"
  - "what should I optimize"
  - "Core Web Vitals"
  - "cache hit ratio"
  - "origin response time"
  - "page load speed"
  - "site performance dashboard"
related:
  - obs-001
  - perf-001
  - perf-003
  - ops-017
---

# See how your application is performing and what to fix

## Ask first

**What are you trying to improve?**
- Page load speed for visitors → speed-diagnostics
- Origin server response time and reliability → origin-health-monitoring
- Cache hit ratio (serve more from Cloudflare, less from origin) → cache-optimization
- All of the above — a full picture → walk all three paths
- Not sure where to start → speed-diagnostics, then expand

**How many origin servers or endpoints?**
- One server → single-origin baseline
- Multiple servers or regions → also walk origin-health-monitoring
- Not sure → assume single origin

## Paths

### speed-diagnostics (default)

To diagnose and improve page load speed:

1. Run a speed test to measure Core Web Vitals and loading performance
2. Review Cloudflare's automatic recommendations for what to turn on or adjust
3. Check Cache to see which resources are served from cache vs fetched from origin
4. Enable Early Hints and other speed features recommended for the setup
5. Set up Analytics monitoring to track Core Web Vitals over time

### origin-health-monitoring

To monitor and improve origin health (especially with multiple origins):

1. Set up Health Checks to continuously monitor origin servers
2. Review origin response times in Analytics to spot slow endpoints
3. Configure Load Balancing to automatically route away from unhealthy origins
4. Configure alerts for origin downtime or response time spikes

### cache-optimization

To maximize the cache hit ratio:

1. Check current cache hit ratio in Analytics and identify what's not being cached
2. Create cache rules to cache more dynamic or static content
3. Enable Tiered Cache to reduce origin requests by serving from nearby data centers
4. Consider Cache Reserve for long-tail content that gets evicted too quickly

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/analytics/, /cache/, /health-checks/, /load-balancing/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
