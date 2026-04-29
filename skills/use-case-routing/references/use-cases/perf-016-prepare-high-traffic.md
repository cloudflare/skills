---
id: perf-016
name: Prepare for high traffic events
category: application-performance-delivery
description: Configure Waiting Room, cache settings, and origin scaling ahead of expected traffic surges.
products: [Waiting Room, Cache, Load Balancing]
default_path: event-preparation
aliases:
  - High traffic event preparation
  - Traffic surge planning
  - Flash sale preparation
  - Product launch traffic management
keywords:
  - "manage traffic surge"
  - "waiting room queue"
  - "flash sale traffic"
  - "Black Friday traffic"
  - "live event traffic"
  - "pre-warm cache"
related:
  - perf-001
  - perf-003
  - ind-002
---

# Prepare for high traffic events

## Ask first

**What type of event are you preparing for?**
- Flash sale or product launch → event-preparation
- Seasonal traffic spike (holiday, back-to-school) → event-preparation
- Live event (broadcast, stream, announcement) → event-preparation
- General preparedness → event-preparation
- Multiple event types → event-preparation

**Is the bottleneck protecting the origin from queuing-eligible page views?**
- Yes, need a dedicated queue on a specific page → waiting-room-setup
- No, broader readiness is the goal → event-preparation

**Do you know your expected traffic volume?**
- Yes, with estimates → use estimates to size Waiting Room thresholds
- No, unpredictable → set conservative thresholds and monitor in real time

## Paths

### event-preparation (default)

Broad readiness for any high-traffic event:

1. Review and optimize cache rules to maximize cache hit ratio
2. Enable tiered caching to reduce origin load
3. Set up a Waiting Room with thresholds appropriate for the expected traffic
4. Verify health checks and failover configuration on Load Balancing origin pools
5. Pre-warm the cache for key assets before the event starts

### waiting-room-setup

Dedicated queue for a specific high-traffic page:

1. Create a Waiting Room scoped to the high-traffic page
2. Set total active users and new users per minute thresholds
3. Customize the waiting room page with your branding
4. Configure session duration and cookie lifetime
5. Choose a queueing method (FIFO, random, or passthrough)

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/waiting-room/, /cache/, /load-balancing/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
