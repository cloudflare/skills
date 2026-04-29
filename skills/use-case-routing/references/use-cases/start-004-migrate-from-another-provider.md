---
id: start-004
name: Migrate from another provider to Cloudflare
category: getting-started
description: Move a site or application from another hosting or CDN provider to Cloudflare.
products: [Workers, Pages, DNS, CDN]
default_path: migrate-dns-cdn
aliases:
  - Switch CDN providers
  - Move to Cloudflare
  - Migrate hosting to Cloudflare
keywords:
  - "migrate from Vercel"
  - "migrate from Netlify"
  - "migrate from AWS CloudFront"
  - "migrate from Fastly"
  - "switch from CloudFront"
  - "leaving Vercel"
related:
  - start-001
  - dev-006
  - perf-001
---

# Migrate from another provider to Cloudflare

## Ask first

**What are you migrating?**
- A full-stack web application (with server-side code) → migrate-fullstack
- A static site or frontend → migrate-static
- Just DNS and CDN, keeping the existing origin → migrate-dns-cdn

**Where is the site currently hosted?** (informational; affects migration guide and adapter steps)
- Vercel
- Netlify
- AWS (CloudFront, S3, Lambda)
- Other provider

## Paths

### migrate-dns-cdn (default)

Keep the existing origin and move DNS and CDN to Cloudflare:

1. Add the domain to Cloudflare
2. Import existing DNS records
3. Configure caching rules to match current CDN behavior
4. Update nameservers at the registrar to activate Cloudflare

### migrate-fullstack

Move a server-side application to Workers:

1. Review the migration guide for the current provider
2. Adapt application code for the Workers runtime
3. Set up storage and database bindings (R2, D1, KV) to replace external services
4. Deploy the application and verify functionality
5. Update DNS to point to the new deployment

### migrate-static

Move a static site or frontend to Pages:

1. Create a Pages project and connect the Git repository
2. Configure build settings for the framework
3. Deploy and verify the site
4. Point the custom domain to the Pages deployment

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/workers/, /pages/, /dns/, /cache/, /r2/, /d1/, /kv/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
