# Platform Gotchas

## Contents
- How To Use This File
- Cross-Cutting
- Compute And Runtime
- Storage And Data
- Async And Orchestration
- AI And Search
- Media And Content
- Analytics And Observability
- Networking And Security
- Deployment And IaC
- Local Development

Use this file as a compact checklist of durable, agent-relevant failure modes. It intentionally avoids complete API examples, command inventories, limits tables, and pricing details. Retrieve current Cloudflare docs before exact values or syntax.

## How To Use This File

Before implementing or debugging a product without a focused skill:

1. Read the relevant section below.
2. Retrieve current product docs.
3. Inspect project config and generated types.
4. Apply the smallest fix.
5. Validate with Wrangler, tests, typecheck, or product-specific inspection.

## Cross-Cutting

- Generate types from config with `npx wrangler types`; do not hand-write binding interfaces in TypeScript projects.
- Keep secret values out of source, config, logs, shell history, and chat. Prefer Wrangler secrets or platform secret stores.
- Prefer runtime bindings from Workers code over Cloudflare REST API calls when a binding exists.
- Distinguish local simulations from remote resources. A local pass does not prove production bindings, permissions, or regional behavior.
- Confirm account, zone, worker, environment, and resource names before writes or deletes.
- For new or uncommon Wrangler commands, retrieve `npx wrangler <group> --help` first.
- Do not cache `env`, bindings, or secret values in module scope. Read them from the handler, Durable Object instance, or current request path.
- Binding-only deploys may reuse existing isolates. Any module-scope client derived from a secret or binding can keep stale credentials after a binding update.
- Importing `env` from `cloudflare:workers` can help deeply nested code, but runtime I/O still belongs in a request/object context. Top-level KV reads, service binding calls, or DO method calls will fail.
- Use `withEnv` or the current test helper when testing code that imports `env` globally.

## Compute And Runtime

### Workers Runtime

- Request and response bodies are streams. Read them once, or clone/tee before multiple consumers.
- Do not rely on module-scope variables for durable state. Use Durable Objects, D1, KV, R2, or external storage based on consistency needs.
- Keep runtime-bound calls such as `fetch()`, binding access, and secret reads inside handlers or object methods, not module initialization.
- Node.js APIs require current compatibility guidance. Prefer Workers-native APIs when the runtime feature is available without `nodejs_compat`.
- For Workers with compatibility date `2026-03-17` or later, binary WebSocket `message` events use `Blob` by default. Set `ws.binaryType = "arraybuffer"` before `accept()` when code expects `ArrayBuffer`, or retrieve the current `websocket_standard_binary_type` compatibility docs. Hibernatable Durable Object `webSocketMessage` handlers still receive binary data as `ArrayBuffer`.
- For Workers code review, prefer the focused `workers-best-practices` skill.

### Browser Run

- Prefer `browser-run` for real browser automation. Do not use Browser Run for simple API calls or fetchable HTML.
- Browser Run was formerly Browser Rendering. Current docs and older examples may mix names such as `browser-rendering`.
- The `.quickAction()` binding path requires a current compatibility date and remote mode for local development. Retrieve docs before debugging application code.
- Treat Live View URLs, session IDs, and CDP endpoints as sensitive. They can expose authenticated pages or human interaction.
- Browser Run traffic is identified as automated/bot traffic. Do not assume target sites treat it like a normal user browser.
- WebMCP is lab/experimental. Prefer structured WebMCP tools when available, but do not design production flows around lab-only APIs without retrieving current limits.

### Dynamic Workers

- Prefer `dynamic-workers` when loading Worker code at runtime, especially generated JavaScript or Code Mode-style tool orchestration.
- Raw Dynamic Workers inherit parent network access when `globalOutbound` is omitted. Set `globalOutbound: null` for untrusted code unless outbound access is intentionally designed.
- Give dynamic code narrow service bindings or `ctx.exports` capabilities instead of raw secrets or broad Internet access.
- Use stable, versioned IDs with `env.LOADER.get(id, callback)`. If code or config changes, change the ID.
- Do not assume repeated calls with the same ID run in the same isolate.
- Use Tail Workers or host-side logging for generated-code output, error capture, and auditing.
- Use Sandbox SDK or Containers when the workload needs filesystem, process, shell, package-install, or long-lived runtime behavior.

### Containers

- Containers run through a `Container` class that extends Durable Objects; use Durable Object storage for state that must survive container restarts.
- Container disk is ephemeral by default. Persist important outputs to Durable Object storage, R2, D1, or an external store.
- In an overridden container `fetch()`, call `containerFetch()` to proxy HTTP requests to the container and avoid recursive `this.fetch()` loops.
- `containerFetch()` does not support WebSockets; use the container `fetch()` path for WebSocket proxying and retrieve the current WebSocket example.
- Configure readiness deliberately with `defaultPort`, `requiredPorts`, and current startup APIs. Starting a container is not the same as proving every service is ready.
- If overriding idle/activity hooks, stop or destroy the container when intended; otherwise idle containers can keep renewing instead of sleeping.

### Placement And Latency

- Evaluate Smart Placement or explicit Placement Hints when a Worker makes multiple sequential round trips to a single backend region.
- Do not enable placement blindly on monolithic full-stack Workers, static-asset-heavy apps, or globally distributed backends; measure the request path first.
- Placement behavior, headers, beta status, and limitations change. Retrieve current docs before relying on `cf-placement` or exact eligibility rules.

## Storage And Data

### KV

- KV is eventually consistent. Avoid workflows that require immediate global read-after-write.
- Avoid hot-key write patterns. If many requests update the same logical value, use Durable Objects or a queue-backed aggregation pattern.
- Treat missing keys as expected; KV returns null for absent values.
- Use prefixes and metadata intentionally so list operations stay bounded and debuggable.

### D1

- Use prepared statements and bound parameters. For dynamic filters, build SQL from allowlisted column/order fragments and bind all user-controlled values.
- Production migrations require the remote database target; local migrations alone do not update production.
- SQLite types matter: represent booleans, dates, and JSON deliberately instead of assuming database-native types.
- Use indexes for frequent predicates, joins, and sort keys; verify with `EXPLAIN QUERY PLAN`, and avoid indexes with no query demand.
- Prefer keyset/cursor pagination for large ordered result sets; offset pagination is acceptable for small or admin-only tables.
- Avoid N+1 query loops. Use joins for related rows, and use `batch()` for independent statements that can share a round trip.
- Chunk large writes and imports; retrieve current batch, timeout, and import/export limits before sizing the chunks.
- Cache D1 reads only when staleness is acceptable. Give KV/cache entries explicit TTLs and update or invalidate them after writes when users expect fresh reads.
- Choose tenancy deliberately: shared database plus `tenant_id` for global queries and simple operations; per-tenant databases for stronger isolation or scale boundaries. Never derive binding names directly from untrusted tenant input without an allowlist.
- For global read replication, retrieve current D1 docs before coding. Do not invent a separate replica binding; current docs route replica reads through the D1 Sessions API.
- Retrieve current docs before using Time Travel, backups, Sessions API, pricing, limits, or beta features.
- For nested migration layouts such as Drizzle's `migrations/0001_init/migration.sql`, retrieve current `migrations_pattern` docs. The glob is relative to the Wrangler config file, defaults to `${migrations_dir}/*.sql`, and records migration names relative to `migrations_dir`.
- Store binary/blob data in R2 and keep D1 for relational metadata.
- Catch uniqueness and constraint errors and translate them into user-meaningful responses.

### R2

- R2 is object storage, not a database. Store searchable metadata elsewhere.
- Design object keys and prefixes for lifecycle, listing, and tenant isolation.
- Public access, custom domains, CORS, and signed URLs are separate concerns; retrieve current setup docs before wiring them.
- For S3-compatible clients, verify endpoint, region expectations, and credential scope.
- When listing, follow `truncated` and `cursor`; do not assume a page contains the requested limit or compare object counts.
- Use `httpEtag` when returning an R2 object's ETag as an HTTP header.
- Treat presigned URLs as bearer tokens. Return expiry metadata to clients and keep expirations short for sensitive operations.
- For multipart uploads, handle missing or completed upload IDs and abort/cleanup failures explicitly; resumed upload handles do not prove the upload still exists.

### R2 Data Catalog, R2 SQL, And Pipelines

- Retrieve current docs first: `https://developers.cloudflare.com/r2/data-catalog/`, `https://developers.cloudflare.com/r2-sql/`, and `https://developers.cloudflare.com/pipelines/`.
- Treat this as an analytics/lakehouse stack over R2 data, not an operational request-path database. Use D1, Durable Objects, Hyperdrive, or an external database when the app needs low-latency transactional reads/writes.
- Check R2 SQL limitations, SQL reference, beta status, and Wrangler/API auth before writing queries. Do not assume full SQL support or a Worker-native R2 SQL binding.
- For Pipelines, retrieve streams, sinks, SQL, and Wrangler docs before editing config. Current Wrangler config uses `stream` inside each `pipelines` binding; old `pipeline` examples are deprecated even though the runtime API remains `env.MY_PIPELINE.send(...)`.
- Validate event shape before sending pipeline events, use generated bindings/types, and inspect metrics when accepted events do not appear in the sink.
- For R2 Data Catalog/Iceberg, design schema evolution, partitions, compaction, and concurrent writes from the current docs. Prefer compatible schema changes and retry conflict-prone commits deliberately.

### Cache Reserve

- Retrieve current Cache Reserve and cache rule docs before configuring eligibility, purges, or billing-sensitive behavior: `https://developers.cloudflare.com/cache/`.
- Use Cache Reserve for persistent CDN cache of cacheable origin responses, not as application object storage.
- Treat Cache Reserve as zone-level automatic cache storage. Workers Cache API calls such as `caches.default`, `caches.open()`, and `cache.put()` only affect Workers edge/custom caches; they do not selectively write into Cache Reserve or Tiered Cache. Use normal `fetch()`, cache rules, and eligible origin responses for Cache Reserve behavior.
- Check cacheability inputs before debugging misses: cache rules, response headers, content length, cookies, `Vary`, range requests, R2 public buckets, and Orange-to-Orange paths.
- Treat purge and clear-data behavior as product-specific. Retrieve docs before promising immediate removal from persistent cache.

### Hyperdrive

- Use Hyperdrive for existing Postgres/MySQL from Workers; use D1 for edge-native SQLite.
- Close or release database clients correctly, especially around errors.
- For multiple sequential database calls, evaluate Smart Placement so the Worker runs near the database.
- Cacheability depends on query shape and driver behavior; retrieve current docs before promising query caching.

### Secrets Store

- Distinguish per-Worker secrets from account-level Secrets Store bindings. Secrets Store is useful for shared, scoped, and rotated secrets across Workers.
- Secrets Store bindings are async. Retrieve secrets through the binding API, not by assuming they behave like plain string env vars.
- Local development may use local secret values unless remote mode is enabled. Do not assume production Secrets Store values are available locally.

### Vectorize

- Match distance metric and dimensions to the embedding model.
- Keep source documents or object keys outside Vectorize when content needs retrieval; vectors alone are not full document storage.
- Rebuild or version indexes when changing embedding models.
- Treat metadata filters as part of schema design, not an afterthought.

### Artifacts

- Use Artifacts for versioned file trees and Git-compatible handoff, not as a generic blob store.
- Prefer repo-per-agent, repo-per-session, or repo-per-application boundaries over one shared write-heavy repository.
- Mint short-lived, least-privilege tokens. Do not hand every agent a long-lived write token.
- Use unique names with tenant, agent, or session IDs to avoid collisions.
- Use R2 for simple blob storage when Git history, forks, tokens, or repository semantics are unnecessary.

### Agent Memory

- Treat Agent Memory as a product-specific persistent memory layer, not a replacement for application databases.
- Namespace by application, environment, tenant, or memory layer; use profiles to isolate users, agents, teams, tenants, or entities.
- Do not assume recall is complete or authoritative. Confirm recalled information before irreversible actions.
- Batch memory ingestion at natural checkpoints instead of calling ingestion after every turn.
- If the beta product is unavailable or you need custom schema/query control, use Durable Objects, D1, KV, or Vectorize.

## Async And Orchestration

### Queues

- Queue delivery is at-least-once. Make consumers idempotent.
- Handle each message explicitly. An uncaught error can retry more than the one message you intended.
- Acknowledge skipped or intentionally ignored messages.
- Choose message content type based on consumers. Prefer JSON when dashboard inspection, HTTP pull consumers, or non-Worker consumers need to read payloads.
- Use dead-letter queues and error classification for poison messages.
- Do not use `batch.messages.forEach(async ...)`; use `for...of` with `await` or `Promise.all()` so processing completes before the handler returns.
- If a producer sends messages with `ctx.waitUntil()`, catch and log send failures because the HTTP response will not naturally surface them.
- If one message in a batch fails without explicit acknowledgements, more of the batch may retry than intended.
- Individual `ack()` and `retry()` decisions should be deliberate; retrieve current precedence rules before mixing per-message and batch calls.
- Leave consumer concurrency unset unless an upstream dependency needs protection. Setting max concurrency to one disables useful autoscaling.

### Workflows

- Design steps to be idempotent and restart-safe.
- Keep step names deterministic. Step names act like durable execution keys.
- Keep steps granular and self-contained; do not put an entire business process into one giant step.
- Workflow bindings can include `schedules` so cron runs create Workflow instances directly. Do not add a separate `scheduled()` Worker handler unless the app needs custom trigger logic.
- Do not rely on mutable state outside step returns. Workflows can hibernate and lose in-memory state.
- Put side effects inside `step.do()` unless repeating the action after a restart is acceptable. `step.do()` callbacks can receive context such as step name/count, attempt, and retry config; retrieve current types before relying on exact property names.
- Return serializable step state only. Do not return `Request`, `Response`, `Error`, class instances, functions, locked streams, or already-read streams.
- Use unique instance IDs deliberately. `create()` can fail for an existing ID within retention; `createBatch()` has different idempotency behavior.
- Use `NonRetryableError` for permanent validation failures and rollback handlers for compensating actions.
- Persist critical final outputs to durable storage before instance retention windows matter.
- Use Workflows for durable multi-step orchestration, not as a substitute for every background job.
- Validate workflow names, event types, and bindings against current docs and generated types.

### Cron Triggers

- Scheduled handlers need explicit error handling and idempotency.
- Use a durable execution ID or lock if missed, duplicated, or overlapping runs would hurt correctness.
- Test scheduled handlers locally only as a smoke test; validate deployed behavior separately.

## AI And Search

### Workers AI

- Retrieve current model IDs, inputs, output shapes, and SDK guidance before coding.
- Keep model choice configurable when product behavior depends on quality, cost, or latency.
- Handle provider/runtime errors with retries or fallbacks appropriate to the user workflow.

### AI Gateway

- Use AI Gateway when routing, caching, observability, rate limiting, provider fallback, or key management across AI providers matters.
- Verify provider URL patterns and SDK integration against current docs.
- Keep provider API keys in secrets, not request code or committed config.

### AI Search

- Use AI Search for managed RAG when the source is a website, R2 bucket, or uploaded documents and managed indexing/retrieval is enough.
- Distinguish namespace bindings from direct instance bindings. Retrieve current `ai_search_namespaces` and `ai_search` config docs before editing Wrangler config.
- Use namespace-level Wrangler commands when creating or managing AI Search namespaces for apps or tenants.
- Retrieve current AI Search indexing and sync behavior before promising freshness, deletion behavior, or crawl timing.
- For custom ingestion, scoring, or metadata schema control beyond AI Search settings, use Vectorize plus your own retrieval pipeline.

## Media And Content

### Images Binding

- Use the Images binding when a Worker must transform bytes from any source. Use R2 or Images product storage for storage concerns.
- For hosted Cloudflare Images, prefer `env.IMAGES.hosted` from Workers to upload, list, inspect, stream original bytes, update, or delete hosted images without API tokens.
- Binding transformations are not automatically cached. Cache or store transformed output deliberately when reuse matters.
- Local development may use a lower-fidelity implementation; use remote mode or deployed testing for pixel-sensitive output.

### Stream Binding

- Use the Stream binding for video library work from Workers: URL uploads, direct-upload provisioning, signed playback tokens, metadata, captions, downloads, watermarks, and video pipelines.
- Prefer the binding over Cloudflare REST calls from Workers when managing Stream videos. Use REST or SDKs for external management-plane automation.
- Store application metadata and permissions outside Stream when the app needs transactional queries or tenant-specific authorization.

### Media Transformations Binding

- Use Media Transformations for Worker-side video/audio transforms, frame extraction, audio extraction, and protected/R2-backed media processing.
- A binding `input()` result is single-use; do not reuse it across multiple transforms.
- Binding output is not automatically cached. Persist to R2 or cache intentionally if repeated delivery matters.
- Local development requires remote mode for real behavior and can touch billable resources.

## Analytics And Observability

### GraphQL Analytics API

- Always include time filters and request only needed fields.
- Responses can be HTTP 200 with GraphQL errors; inspect `errors`, not just status.
- Adaptive datasets can be sampled. Treat results as representative unless docs/schema prove exactness for the dataset.
- Use introspection or docs to verify dataset names, dimensions, scopes, and permissions.

### Analytics Engine

- Use it for custom high-cardinality metrics from Workers, not for querying built-in Cloudflare product analytics.
- Design indexes/blobs before writing data; query flexibility depends on what you wrote.
- Account for sampling and retention by retrieving current docs.
- Treat writes as telemetry emission, not transactional confirmation. Query Analytics Engine through its analytics/query surfaces, not from the Worker binding that writes data points.

### Workers Observability

- Enable observability deliberately in config for production debugging.
- Use structured logs and avoid secret-bearing log fields.
- Use `tracing.enterSpan()` from `cloudflare:workers` or `ctx.tracing.enterSpan()` for meaningful custom work units after traces are enabled. Attach only low-cardinality, non-secret attributes.
- Tail logs are diagnostic, not durable audit storage.
- Use Workers observability for Worker telemetry; use Cloudflare Logs or Log Explorer for account/zone log datasets.

## Networking And Security

### Zone Core Operations

- Retrieve the product docs before changing zone-level behavior. DNS, SSL/TLS, Rules, Cache, Load Balancing, Health Checks, Waiting Room, WAF, Bots, and API Shield have separate evaluation models, plan gates, and API/Terraform resource shapes.
- Prefer Cloudflare Rules products for redirects, header transforms, origin overrides, cache rules, compression, and custom errors when they can express the behavior. Use Workers when the request path needs application logic, custom state, external calls, or code-level branching.
- Use Ruleset Engine docs for expression language, phases, account-vs-zone rulesets, managed ruleset overrides, and API shapes. Do not guess phases, field names, or skip/exception semantics.
- For multi-zone WAF or shared security baselines, retrieve the streamlined WAF reference architecture. Avoid mixing account-level and zone-level ownership without a clear exception model.
- For traffic steering and failover, distinguish DNS/Load Balancing/Health Checks from application-level routing. Load Balancing changes traffic flow; Health Checks alone only monitor and notify.
- Waiting Room controls visitor admission during capacity events; it is not origin selection, DDoS mitigation, or a task queue.
- Version Management can stage and roll back supported zone configuration. Retrieve supported configuration docs before promising that a setting can be versioned.
- Resource tags are management metadata for organization, access control, and billing attribution. Do not rely on tags for request-time logic unless a specific product doc says they participate in evaluation.

### Cloudflare For Platforms And SaaS

- Use Cloudflare for SaaS for customer custom hostnames on a SaaS provider's zone. Use Workers for Platforms when customers upload or generate code that runs as user Workers. Use Tenant APIs for partner-style account and subscription provisioning.
- Workers for Platforms centers on dispatch namespaces, a dynamic dispatch Worker, user Workers, and optional outbound Workers. Do not create a namespace per customer unless current docs justify it; use tags, metadata, and app data for customer organization.
- The dynamic dispatch Worker is the platform control point for routing, auth, plan limits, response shaping, and calls to internal service bindings.
- User Workers are isolated by default and may need explicitly configured bindings, compatibility settings, limits, static assets, and observability. Generate or validate metadata against current upload docs before deploying user code.
- Use outbound Workers or Dynamic Workers egress controls for untrusted customer/AI-generated code that makes external requests. Do not pass raw platform secrets into user Workers.
- Cloudflare for SaaS custom hostnames have separate ownership validation, certificate issuance, security, WAF, analytics, and product compatibility docs. Retrieve the Cloudflare for SaaS docs before automating custom hostname lifecycle.
- For OAuth integrations, retrieve current Cloudflare OAuth docs and API scopes. Do not ask users for broad API tokens when an installable OAuth flow is the right product shape.

### Tunnel, Spectrum, And Private Connectivity

- Use Tunnel/Cloudflare One for private HTTP app exposure and Zero Trust access.
- Use Spectrum for non-HTTP TCP/UDP protocols.
- For private databases from Workers, compare Hyperdrive, TCP sockets, Tunnel, and VPC/private-network patterns against current docs.
- For Worker access to internal services, distinguish scoped Workers VPC Services from broader Workers VPC Networks before choosing raw TCP sockets.
- VPC Network bindings support `fetch()` for HTTP and `connect()` for raw TCP to private destinations reachable through Tunnel, Mesh, or Cloudflare WAN. Current `connect()` support is plaintext TCP only.
- A VPC Network binding with `network_id: "cf1:network"` sends public Internet egress through Cloudflare Gateway policies and logs. Treat this as a security-control path, not just a routing knob.
- Retrieve current troubleshooting docs when debugging private connectivity: `https://developers.cloudflare.com/workers-vpc/reference/troubleshooting/`, `https://developers.cloudflare.com/workers/runtime-apis/tcp-sockets/#troubleshooting`, and `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/`.
- For physical/private interconnects, design high availability from the start; single-link setups are operationally fragile.

### Realtime And TURN

- Retrieve current Realtime docs before choosing RealtimeKit, SFU, TURN, Stream, or Durable Objects/WebSockets: `https://developers.cloudflare.com/realtime/`.
- Use Realtime SFU/RealtimeKit/TURN for WebRTC audio, video, data channels, and restrictive-network relay. Use Stream for video-on-demand, and Durable Objects/WebSockets for stateful chat or collaboration without media.
- Keep Realtime API tokens and app secrets server-side. Create sessions, participants, and TURN credentials from Workers or another backend, not from browser code.
- Validate user identity, permissions, session IDs, and track IDs before creating or subscribing to media. Rate limit session creation endpoints.
- Retrieve current network, pricing, and TURN docs before promising connectivity through restrictive firewalls or estimating media cost.

### Rate Limiting Binding

- Use the Rate Limiting binding for in-code user, tenant, route, or API-key limits after a Worker starts. Use WAF rate limiting rules when traffic should be limited before Worker execution.
- Choose stable keys such as user IDs, tenant IDs, route IDs, or API keys. Avoid IP/location keys unless the broad grouping is intentional.
- Rate limits are per Cloudflare location and intentionally permissive/eventually consistent. Do not use them for accurate accounting.
- Bindings with the same namespace ID share counters across Workers in the same account.
- Rate limiting bindings may not appear in the dashboard; emit Workers logs or Analytics Engine events for monitoring.

### mTLS Binding

- Use the mTLS binding when a Worker must present a client certificate to an upstream service.
- Upload certificate/key material with Wrangler or the current API; never commit private keys.
- Current docs warn that Worker mTLS cannot be used for requests to services on proxied Cloudflare zones; expect 520 errors there.
- The binding behaves like a Fetcher. Use generated types and call `env.MY_CERT.fetch()`.

### WAF, API Shield, Bot Management

- Stage risky rules in log/simulate or narrow scopes before blocking production traffic.
- Schema and JWT validation failures are often configuration mismatch, not attacker traffic.
- For API Shield schema validation migrations, check for lingering Classic Schema Validation rules before blaming the uploaded OpenAPI schema. Retrieve current docs for Schema Validation 2.0, supported OpenAPI versions, external-reference support, and body-inspection limits.
- For BOLA, sequence mitigation, API discovery, and risk labels, verify unique session identifiers and current minimum traffic/training requirements before expecting detections or blocking behavior.
- For Bot Management JavaScript Detections, check lifecycle and browser prerequisites: CSP must allow `/cdn-cgi/challenge-platform/`, first HTML-page visits may not have JSD data yet, ad blockers or disabled JavaScript can prevent a pass signal, and Managed Challenge behavior differs from a plain Block rule.
- API discovery and ML-driven features may need enough representative traffic before conclusions are reliable.
- Keep bypasses and exceptions documented with owner, reason, and expiry.

### Turnstile

- Prefer `turnstile-spin` for end-to-end setup.
- Never call siteverify directly from the browser; validate through a server-side Worker or backend.

## Deployment And IaC

### Terraform And Pulumi

- Do not manage the same Cloudflare resource from both Terraform/Pulumi and Wrangler unless the ownership boundary is explicit.
- IaC can create D1 databases, buckets, or projects, but app-level deploys and migrations may still require Wrangler or product-specific commands.
- Provider versions can rename resources or change schema. Retrieve current provider docs and migration guides before upgrading.
- Import existing resources before managing them declaratively.

### Pages, Workers Static Assets, And C3

- Confirm whether the project is Pages, Workers with static assets, or framework-generated before editing config.
- Bindings and environment variables differ between Pages Functions, Workers, and local dev.
- Do not start new Workers Sites projects; use Workers static assets or Pages.
- C3/scaffold commands change; retrieve current create command and platform flags before generating.

### Temporary Deployments

- `wrangler deploy --temporary` is for unauthenticated AI-agent or prototype deploys, not production or CI.
- Start with normal deploy; if Wrangler reports missing credentials and suggests `--temporary`, rerun with that flag.
- Temporary preview accounts expire if not claimed. Return the live URL and claim URL promptly.
- Treat claim URLs as sensitive because they grant ownership of the temporary preview account.
- Temporary deployments support only a subset of products; retrieve current claim deployment docs before using advanced bindings.

## Local Development

- Miniflare and local Wrangler simulations are fast feedback tools, not perfect production replicas.
- Remote bindings can touch real resources; call that out before enabling them.
- Some services require deployed or remote testing. Do not claim local-only validation proves production behavior.
