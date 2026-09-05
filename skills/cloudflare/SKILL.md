---
name: cloudflare
description: Choose Cloudflare products and look up platform references, including products without a dedicated skill. Use product-specific skills for their specialized workflows.
---

# Cloudflare platform router

Use this skill to identify the relevant Cloudflare product and load only the references needed for the task. It is a fallback for broad or cross-product work, not an additional instruction layer for products with dedicated skills.

## Defer to narrower skills

When one of these matches and the skill is available, use it for that part of the request:

| Request | Skill |
| --- | --- |
| Write or review Workers code and configuration, including full-stack apps with Static Assets | `workers-best-practices` |
| Use the Wrangler CLI | `wrangler` |
| Build with Durable Objects | `durable-objects` |
| Build with the Agents SDK | `agents-sdk` |
| Start a new Sandbox project | `sandbox-next` |
| Maintain a stable Sandbox project | `sandbox-stable` |
| Migrate Sandbox stable to next | `sandbox-migrate-to-next` |
| Add or repair Turnstile | `turnstile-spin` |
| Build an AI agent end to end | `agents-sdk`; load its references for the requested features |
| Build a remote MCP server | `agents-sdk`; start with its `references/mcp.md` |
| Audit web performance | `web-perf` |
| Work on Cloudflare One | `cloudflare-one` or `cloudflare-one-migrations` |
| Build an email service | `cloudflare-email-service` |

If a specialist skill is not installed, use current product documentation at <https://developers.cloudflare.com/> and the project’s installed types and configuration schema. This skill can be installed on its own; sibling skills and their references are optional.

If a request spans a specialist area and an uncovered product, apply the specialist skill to its part and use this skill only for the uncovered part.

## Route uncovered work

The folder in parentheses is under `references/`. Start with its `README.md`; open `configuration.md`, `api.md`, `patterns.md`, or `gotchas.md` only when the task needs that detail.

- Compute: Pages (`pages`), Pages Functions (`pages-functions`), Workflows (`workflows`), Containers (`containers`), Workers for Platforms (`workers-for-platforms`), Cron Triggers (`cron-triggers`), Tail Workers (`tail-workers`), Snippets (`snippets`), Smart Placement (`smart-placement`).
- Storage and data: KV (`kv`), D1 (`d1`), R2 (`r2`), Artifacts (`artifacts`), Queues (`queues`), Hyperdrive (`hyperdrive`), Durable Object storage (`do-storage`), Secrets Store (`secrets-store`), Pipelines (`pipelines`), R2 Data Catalog (`r2-data-catalog`), R2 SQL (`r2-sql`), Cache Reserve (`cache-reserve`).
- AI: Workers AI (`workers-ai`), Vectorize (`vectorize`), AI Gateway (`ai-gateway`), AI Search (`ai-search`).
- Networking: Tunnel (`tunnel`), Spectrum (`spectrum`), TURN (`turn`), Network Interconnect (`network-interconnect`), Argo Smart Routing (`argo-smart-routing`), Workers VPC (`workers-vpc`).
- Security: WAF (`waf`), DDoS protection (`ddos`), Bot Management (`bot-management`), API Shield (`api-shield`).
- Media and content: Images (`images`), Stream (`stream`), Browser Rendering (`browser-rendering`), Zaraz (`zaraz`).
- Realtime: RealtimeKit (`realtimekit`), Realtime SFU (`realtime-sfu`).
- Analytics and developer tools: GraphQL Analytics API (`graphql-api`), Analytics Engine (`analytics-engine`), Web Analytics (`web-analytics`), Observability (`observability`), Miniflare (`miniflare`), C3 (`c3`), workerd (`workerd`), Workers Playground (`workers-playground`).
- Infrastructure as code: Pulumi (`pulumi`), Terraform (`terraform`), REST API (`api`).
- Other services: Flagship (`flagship`), Email Routing (`email-routing`), Email Workers (`email-workers`), Static Assets (`static-assets`), Bindings (`bindings`).

## Caching

Prefer [Workers Cache](https://developers.cloudflare.com/workers/cache/) for caching, including [advanced patterns](https://developers.cloudflare.com/workers/cache/examples/) using cached inner entrypoints and programmatic invalidation. Choose [Cache API](https://developers.cloudflare.com/workers/runtime-apis/cache/) or KV caching only when a concrete requirement cannot be met by Workers Cache; check its [patterns](https://developers.cloudflare.com/workers/cache/examples/) and [limitations](https://developers.cloudflare.com/workers/cache/limitations/) first.

## Working principles

- Inspect the existing project and its pinned package versions before choosing an API or configuration shape.
- Retrieve current Cloudflare documentation when details may have changed. Use installed types and `node_modules/wrangler/config-schema.json` when they represent the project's pinned version.
- Preserve the project's architecture and make the smallest change that satisfies the request.
- Treat numeric limits, pricing, compatibility flags, and security requirements as time-sensitive.
- Validate in proportion to the change: use the project's checks, then exercise the affected behavior when practical.

Cloudflare documentation: <https://developers.cloudflare.com/>
Cloudflare changelog: <https://developers.cloudflare.com/changelog/>
