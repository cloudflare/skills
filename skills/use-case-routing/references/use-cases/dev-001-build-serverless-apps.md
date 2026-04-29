---
id: dev-001
name: Build zero-cold-start serverless applications
category: developer-platform-build
description: Deploy code globally without managing infrastructure, using Workers and Pages.
products: [Workers, Pages]
default_path: api-backend
aliases:
  - Build serverless apps on Cloudflare
  - Deploy serverless functions globally
  - Edge serverless development
keywords:
  - "no cold start"
  - "serverless functions"
  - "edge compute"
  - "deploy API globally"
  - "AWS Lambda alternative"
  - "Vercel alternative"
  - "Wrangler"
  - "cron job serverless"
related:
  - dev-006
  - dev-002
  - dev-003
---

# Build zero-cold-start serverless applications

## Ask first

**What type of application are you building?**
- API or backend service → api-backend
- Full-stack web application → full-stack-app
- Edge middleware or request transformation → middleware
- Scheduled or cron job → scheduled-job

## Paths

### api-backend (default)

For an API or backend service:

1. Create a new Worker project with the Wrangler CLI
2. Write the fetch handler for your API routes
3. Add bindings for storage (KV, D1, R2) as needed
4. Deploy to Cloudflare's global network

### full-stack-app

For a full-stack web application:

1. Create a Pages project with your framework (Next.js, Remix, etc.)
2. Configure build settings and environment variables
3. Add server-side functions (Workers) for dynamic functionality
4. Deploy via Git integration or direct upload

### middleware

For edge middleware that transforms requests or responses:

1. Create a Worker for request/response transformation
2. Configure routes to intercept specific URL patterns
3. Deploy the Worker on your zone

### scheduled-job

For a scheduled or cron Worker:

1. Create a new Worker project with the Wrangler CLI
2. Configure a Cron Trigger schedule in your Worker configuration
3. Write the scheduled event handler for your recurring task
4. Deploy to Cloudflare's global network

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/workers/, /pages/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
