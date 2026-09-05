# Product Selection

Use this file when the user asks a broad Cloudflare architecture, storage, compute, AI, networking, security, analytics, or deployment question and the right product is not obvious.

## Retrieval Rule

Use this as a selection checklist, not an API reference. Retrieve current Cloudflare docs before exact commands, limits, pricing, configuration fields, beta status, or API shapes.

## Prefer Focused Skills

Use the user's goal as the routing signal. Load or follow focused skills first when one clearly matches:

| User need | Prefer |
| --- | --- |
| Create, inspect, configure, or deploy Cloudflare resources from the CLI | `wrangler` |
| Automate a real browser for screenshots, PDFs, crawlers, CDP, Playwright, or Puppeteer | `browser-run` |
| Run AI-generated or runtime-loaded Worker code inside a Worker | `dynamic-workers` |
| Coordinate durable multi-step work with sleeps, retries, waits, or rollbacks | `workflows` |
| Review Worker code or apply production Worker implementation patterns | `workers-best-practices` |
| Keep per-object state, coordinate WebSockets, or use SQLite per object | `durable-objects` |
| Build a stateful AI agent, chat app, MCP integration, scheduler, or voice workflow | `agents-sdk` |
| Execute untrusted code, run an interpreter, or need filesystem/process isolation | `sandbox-next` for new or preview projects, `sandbox-stable` for existing stable apps |
| Send transactional email or route inbound email | `cloudflare-email-service` |
| Evaluate feature flags, target users, or roll out changes gradually | `flagship` |
| Add CAPTCHA or Turnstile bot protection to a form or app | `turnstile-spin` |
| Plan Zero Trust, Access, Gateway, WARP, SASE, or private network work | `cloudflare-one` or `cloudflare-one-migrations` |

## Architecture References

When the user asks for a design rather than a single product task, check the current [Reference Architecture docs](https://developers.cloudflare.com/reference-architecture/) before inventing architecture guidance. Especially useful starting points include SaaS platform design, streamlined WAF deployment across zones and applications, load balancing, secure application delivery, serverless global APIs, programmable platforms, and storage patterns.

## Common Choices

| Need | Default choice | Use something else when |
| --- | --- | --- |
| Stateless HTTP/API code | Workers | The app is static-first; use Workers Static Assets. Preserve existing Pages deployments during unrelated work. |
| Static or full-stack frontend | Workers Static Assets | Existing Pages project conventions dominate. |
| Per-room, per-user, per-tenant coordination | Durable Objects | Data needs global relational querying; use D1 or external DB. |
| Key-value config, cache, sessions | KV | You need read-after-write consistency, relational queries, or high write rate to one key. |
| Feature flags, targeting, gradual rollouts | Flagship | Static config can stay in Wrangler vars; low-level key-value config belongs in KV. |
| Relational SQLite data | D1 | Large binary/object data belongs in R2; existing Postgres/MySQL may fit Hyperdrive. |
| Object/file storage | R2 | You need relational indexes or transactions; pair with D1/DO metadata. |
| Versioned file trees, repositories, build outputs, checkpoints | Artifacts | You only need blobs without Git-like history; use R2. |
| Data lake tables in object storage | R2 Data Catalog | Plain object storage is enough, or the workload is transactional rather than analytical. |
| SQL over R2/Iceberg data | R2 SQL | The data is small, operational, or latency-sensitive; use D1, Analytics Engine, or an external warehouse. |
| Streaming ingest into R2/Iceberg | Pipelines | You only need a task queue; use Queues, or use Analytics Engine for custom metrics. |
| Persistent CDN cache for cacheable origin assets | Cache Reserve | The workload needs object storage, range-heavy media delivery, or application-owned metadata; use R2, Stream, or normal cache rules. |
| Background jobs | Queues | Multi-step durable orchestration with checkpoints fits Workflows. |
| Multi-step durable business process | Workflows | One-off async fanout may be simpler with Queues. |
| Lightweight AI-generated or untrusted code execution | Dynamic Workers | You need filesystem/process isolation, shell, or package installs; use Sandbox SDK or Containers. |
| Linux/runtime-specific workloads | Containers | Plain Workers or the Sandbox SDK can satisfy the runtime, CPU, filesystem, or isolation need. |
| Vector search | Vectorize | Managed RAG over a website, R2 bucket, or uploaded documents may fit AI Search. |
| Long-lived agent memory, when the beta product is available | Agent Memory | You need custom schema/query control; use D1, Durable Objects, KV, or Vectorize. |
| LLM/image/embedding inference on Cloudflare | Workers AI | You need provider routing/caching/observability across multiple AI providers; use AI Gateway. |
| AI provider gateway, caching, routing, logs | AI Gateway | You only need Workers AI binding calls in one Worker. |
| Managed RAG/search over websites, R2, or uploaded docs | AI Search | You need custom ingestion/scoring/schema control; use Vectorize plus your own pipeline. |
| Shared reusable secrets | Secrets Store | A per-Worker Wrangler secret is simpler and rotation/sharing requirements are modest. |
| Existing Postgres/MySQL from Workers | Hyperdrive | Edge-native SQLite is enough; use D1. |
| Private Worker access to internal services | Workers VPC | Public HTTP origin, Tunnel, Hyperdrive, or sockets are enough. |
| Worker-to-origin client certificate auth | mTLS binding | The target is a proxied Cloudflare zone; current docs warn that Worker mTLS returns 520 there. |
| In-code user, tenant, route, or API-key rate limits | Rate Limiting binding | You need perimeter rate limiting before the Worker starts; use WAF rate limiting rules. |
| Deployment-aware logs, metrics, or gradual rollout telemetry | Version Metadata binding | The app does not need version IDs/tags in runtime telemetry. |
| Private app/network access, WARP, Gateway, Access | Cloudflare One | Simple public HTTP reverse proxy may only need Tunnel or Workers. |
| Non-HTTP TCP/UDP proxy | Spectrum | HTTP/HTTPS traffic should normally use Cloudflare proxy/Workers. |
| Real-time audio/video or TURN | Realtime docs and TURN docs | Video-on-demand belongs in Stream; stateful chat often belongs in Durable Objects/WebSockets. |
| Browser automation, screenshots, PDFs | Browser Run | Simple HTTP/API scraping can use `fetch()`. |
| Image storage and transformation | Images or Images binding | Raw object storage with custom processing can use R2 plus Workers. |
| Video/audio transformation inside Workers | Media Transformations binding | Video storage/streaming alone belongs in Stream. |
| Video storage/streaming | Stream | Small static video assets may be enough in R2 or static assets. |
| Built-in Cloudflare analytics queries | GraphQL Analytics API | Custom high-cardinality application metrics fit Analytics Engine. |
| Custom application metrics | Analytics Engine | Debug logs/traces fit Workers observability. |
| Website traffic analytics or tag orchestration | Web Analytics or Zaraz | Product analytics, security analytics, or Worker metrics need other analytics products. |
| Domain onboarding, DNS records, nameservers, DNSSEC | DNS docs | Zone setup type, proxy status, DNSSEC, registrar, and internal/private DNS requirements can change the implementation path. |
| TLS certificates and encryption modes | SSL/TLS docs | Custom hostname certificates, mTLS, keyless SSL, geo key storage, or API Shield mTLS have product-specific docs. |
| Redirects, URL/header rewrites, origin overrides, compression, custom errors | Rules plus Ruleset Engine | A Worker is only needed when rule products cannot express the behavior or need application logic. |
| CDN behavior, cache keys, edge/browser TTLs, cache security | Cache Rules | Worker Cache API is useful for application-owned cache behavior; zone cache rules are often simpler for request/response policy. |
| Origin failover, traffic steering, active-active, private load balancing | Load Balancing | A single origin plus alerting may only need Health Checks; visitor queueing during surges belongs in Waiting Room. |
| Origin uptime monitoring and alerts | Health Checks | Load Balancing monitors are tied to load balancer pools; standalone Health Checks fit simple monitoring. |
| Planned traffic surges or fair visitor queueing | Waiting Room | Load Balancing handles origin selection; Waiting Room controls visitor admission during capacity events. |
| Safer staged zone config changes | Version Management | Normal API/Terraform/Wrangler changes may be enough when versioned environments and rollbacks are unnecessary. |
| Resource organization, ownership, billing attribution | Resource Tagging | Naming conventions may be enough for small accounts; tags help multi-team, multi-account, or billing/reporting workflows. |
| Customer custom domains for a SaaS product | Cloudflare for SaaS | Ordinary app-owned domains only need DNS/TLS/routes; Cloudflare for SaaS is for customer hostnames. |
| Customer-uploaded code or dynamic user Workers | Workers for Platforms | Ordinary multitenancy should use one app plus tenant data; use Workers for Platforms when customers deploy code. |
| Provision and manage customer Cloudflare accounts/services | Tenant API | Use Cloudflare for SaaS for custom hostnames on your zone; use Tenant for partner-style account/subscription management. |
| User authorization to Cloudflare APIs from an integration | OAuth docs | Static API tokens may be enough for internal automation; OAuth fits user-installed third-party or multi-account integrations. |
| Standard WAF rollout across many zones/apps | Account-level WAF plus Ruleset Engine | Zone-level rules are simpler for one-off apps; retrieve the WAF reference architecture for shared rules and exceptions. |
| Bot scoring, scraping control, AI crawler handling | Bots plus WAF custom rules | Turnstile verifies specific interactions; Bots/WAF classify and mitigate traffic at the edge. |
| API attack surface, schema/JWT/mTLS validation, sequence abuse | API Shield | Plain WAF custom rules may suffice for simple path/method controls. |
| Browser-side script inventory, CSP monitoring, malicious scripts | Client-side security | Server-side WAF and Turnstile do not monitor third-party scripts running in the visitor browser. |
| Human verification in forms, signup, login, contact flows | Turnstile | Challenge pages and JS detections protect traffic flows at the edge; Turnstile is embedded app verification. |
| Infrastructure as code | Terraform or Pulumi | App deploy loops often stay simpler with Wrangler. Do not co-manage the same resource from both. |

## Private Connectivity Chooser

Use this when a Worker, application, or user needs access to private networks, internal services, or non-HTTP protocols.

| Need | Start with | Current docs |
| --- | --- | --- |
| Worker HTTP access to one known private service | Workers VPC Service | `https://developers.cloudflare.com/workers-vpc/configuration/vpc-services/` |
| Worker broad private-network access or raw TCP through Tunnel, Mesh, or WAN | Workers VPC Network | `https://developers.cloudflare.com/workers-vpc/configuration/vpc-networks/` |
| Worker to private Postgres/MySQL | Hyperdrive with Workers VPC | `https://developers.cloudflare.com/hyperdrive/configuration/connect-to-private-database-vpc/` |
| Worker raw TCP sockets outside a VPC binding | Workers TCP sockets | `https://developers.cloudflare.com/workers/runtime-apis/tcp-sockets/` |
| Expose a private HTTP app or network to users with Zero Trust | Cloudflare Tunnel / Cloudflare One | `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/` |
| Public non-HTTP TCP/UDP proxying | Spectrum | `https://developers.cloudflare.com/spectrum/` |

For debugging private connectivity, retrieve the relevant troubleshooting page before relying on memory:

- Workers VPC troubleshooting: `https://developers.cloudflare.com/workers-vpc/reference/troubleshooting/`
- TCP sockets troubleshooting: `https://developers.cloudflare.com/workers/runtime-apis/tcp-sockets/#troubleshooting`
- Tunnel troubleshooting: `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/`

## Product Fit Notes

- Prefer bindings from Workers code over calling Cloudflare REST APIs from inside Workers.
- Use Wrangler for local reproducibility, generated types, and developer workflows.
- Use Cloudflare REST APIs for management-plane automation that Wrangler does not cover.
- Use Terraform/Pulumi for declarative infrastructure ownership, not for high-frequency app deploys unless the team already owns that flow.
- Use GraphQL Analytics API for Cloudflare product analytics; use Analytics Engine for metrics your Worker writes.
- Use R2 for binary/blob payloads; pair it with D1 or Durable Objects for transactional metadata, or KV for read-heavy metadata where eventual consistency is acceptable.
- For R2 Data Catalog, R2 SQL, Pipelines, Cache Reserve, and Realtime, retrieve the relevant product docs before assuming API shape, SQL support, limits, beta status, cache eligibility, or network/security behavior.
- Use Durable Objects for coordination and consistency boundaries; use Queues or Workflows for asynchronous work.
- Use Workers for Platforms only when customers or tenants deploy code; do not use it for ordinary multitenancy.
- Use Dynamic Workers for runtime-loaded code inside your own Worker; use Workers for Platforms when external customers manage deployed Worker scripts.
- Use Browser Run only when a real browser is required; start with `fetch()` for APIs and static HTML.
- Use Worker-native bindings for Rate Limiting, mTLS, Version Metadata, Images, Media Transformations, Stream, Flagship, AI Search, and Secrets Store instead of inventing REST/API-key paths from Workers.
- For zone/core operations, prefer product rules and configuration docs before reaching for Workers. DNS, SSL/TLS, Rules, Cache, Load Balancing, Health Checks, Waiting Room, WAF, Bots, API Shield, and Version Management often solve common application delivery and security needs without application code.
- For multi-tenant platform work, distinguish three separate concerns: custom hostnames for customer domains with Cloudflare for SaaS, customer-uploaded code with Workers for Platforms, and customer account/subscription provisioning with Tenant APIs.

## Validation Defaults

After choosing products, validate with the closest current checks:

```bash
npx wrangler types
npx wrangler deploy --dry-run
npm test
npx tsc --noEmit
```

For product-specific resources, retrieve the current Wrangler help before creating or deleting anything:

```bash
npx wrangler <resource> --help
```
