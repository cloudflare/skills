---
id: arch-004
name: Replace your multi-vendor dev stack with one platform and one bill
category: multi-vendor-architecture
description: Replace multi-vendor dev stacks with Workers, Pages, R2, D1, and KV — one bill, zero egress.
products: [Workers, Pages, R2, D1, KV, Queues]
default_path: greenfield-setup
aliases:
  - Platform consolidation
  - Replace multi-vendor dev stack
  - Reduce cloud vendor sprawl
  - Single platform developer stack
  - One bill for infrastructure
keywords:
  - "consolidate cloud providers"
  - "zero egress fees"
  - "cloud platform migration"
  - "replace object storage"
  - "replace serverless functions"
  - "vendor sprawl"
  - "one bill for infrastructure"
related:
  - dev-001
  - dev-002
  - dev-003
  - dev-006
---

# Replace your multi-vendor dev stack with one platform and one bill

## Ask first

**What does your current stack look like?**
- Frontend host plus a separate backend → full-stack-migration
- Multiple cloud services stitched together → full-stack-migration
- Starting fresh, want to avoid vendor sprawl → greenfield-setup

**What data services do you need?**
- Object storage → add R2
- SQL database → add D1
- Key-value cache → add KV
- All of the above → bind R2, D1, and KV together

## Paths

### greenfield-setup (default)

For a new project on a single platform:

1. Initialize a new Workers project with Wrangler
2. Choose a framework (Next.js, Remix, Astro, Hono) or vanilla Workers
3. Add R2, D1, and KV bindings as needed
4. Deploy to Cloudflare's global network

### full-stack-migration

For consolidating an existing multi-vendor stack:

1. Create a Worker for the backend API or full-stack app
2. Create R2 buckets for object storage
3. Create D1 databases for relational data
4. Create KV namespaces for key-value caching
5. Bind R2, D1, and KV to the Worker
6. Deploy and verify the consolidated stack

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/workers/, /pages/, /r2/, /d1/, /kv/, /queues/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
