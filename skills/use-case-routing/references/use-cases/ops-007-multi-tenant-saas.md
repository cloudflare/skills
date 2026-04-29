---
id: ops-007
name: Build and scale multi-tenant SaaS platforms
category: developer-platform-operate
description: Run customer code, provision custom domains and SSL per tenant, and reduce egress for SaaS platforms built on Cloudflare.
products: [Workers for Platforms, Cloudflare for SaaS, R2, CDN]
default_path: workers-for-platforms
aliases:
  - Build multi-tenant SaaS platforms
  - Scale SaaS platforms globally
  - SaaS provider infrastructure
keywords:
  - "custom domains per customer"
  - "tenant isolation"
  - "customer SSL certificates"
  - "run customer code"
  - "untrusted code execution"
  - "dispatch namespaces"
  - "white-label hosting"
  - "Vercel for SaaS"
  - "Heroku alternative SaaS"
related:
  - dev-001
  - sec-010
  - ops-011
  - ops-014
---

# Build and scale multi-tenant SaaS platforms

## Ask first

**What multi-tenant capability do you need?**
- Let customers run their own code on my platform → workers-for-platforms
- Custom domains and SSL for each customer → cloudflare-for-saas
- Reduce infrastructure and egress costs → saas-cost-reduction
- Application security and performance → walk workers-for-platforms or cloudflare-for-saas plus saas-cost-reduction
- All of the above → walk all three paths

## Paths

### workers-for-platforms (default)

For platforms that run customer code:

1. Enable dispatch namespaces for tenant isolation
2. Create a dispatch namespace for customer Workers
3. Deploy individual customer Workers into the namespace
4. Route incoming requests to the correct customer Worker

### cloudflare-for-saas

For custom domains and SSL per customer:

1. Configure your fallback origin
2. Create custom hostnames for each customer domain
3. Let Cloudflare for SaaS automatically provision SSL certificates per hostname
4. Set up routing rules per custom hostname

### saas-cost-reduction

For reducing infrastructure and egress costs:

1. Migrate object storage to R2 (zero egress fees)
2. Maximize CDN cache hit ratio
3. Move compute workloads to Workers for cost efficiency

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-for-platforms/, /r2/,
/cache/, /workers/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
