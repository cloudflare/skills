---
name: workers-verification
description: Diagnose and verify Cloudflare Workers application behavior across browser requests, Worker execution, bindings, and persisted state. Use for failing endpoints, incorrect writes, integration failures, or verifying a fix with local traces and Local Explorer.
---

# Workers Verification

Use observable request and state evidence to establish where an application fails and whether the fix works. Retrieve current documentation before choosing commands or telemetry queries; use the project's installed Wrangler or Cloudflare Vite plugin, configuration, and test setup as the baseline.

## Establish the target

Identify the failing user action or request and its expected response and side effects. Inspect the dev command, selected environment, binding targets, and local persistence configuration before reproducing a write.

Distinguish where the Worker executes from where each binding stores data. A localhost Worker can use remote resources; local fixture changes will not repair missing data in a remote binding. Use [local development and remote bindings](https://developers.cloudflare.com/workers/local-development/) to check the actual mode and supported simulations. Keep reproduction writes within the intended test resources; do not switch to production bindings merely to make a local failure disappear.

## Discover Local Explorer and traces

Read [Local Explorer](https://developers.cloudflare.com/workers/local-development/local-explorer/) for current prerequisites, supported bindings, observability, and API discovery.

- Start the project's existing Wrangler or Cloudflare Vite development command and use its actual origin and port. Read the Local Explorer API hint from startup output and fetch its OpenAPI specification before forming requests. If no hint appears, consult the current docs and installed version; do not assume the default port or an endpoint from an older blog post.
- Use the discovered observability query operation to inspect the reproduced invocation's spans, errors, and correlated logs. Derive request bodies and SQL/table details from the served schema and endpoint guidance instead of inventing a telemetry schema.
- Prefer automatic local tracing before adding temporary logs or an instrumentation SDK. Current tooling captures local invocations automatically; deployed tracing has separate configuration. If the installed version lacks this capability, identify the version gap and use existing runtime logs/tests or an in-scope tooling update.
- For visual inspection, press `e` in Wrangler or open the documented Explorer path on the dev server. Use the API for focused programmatic inspection of supported local binding data.

Local traces can include remote-binding calls. That does not make Local Explorer's local data browser a view of the remote resource. Check the relevant remote resource separately when the reproduction uses remote bindings.

## Follow the request through the application

1. Reproduce the browser interaction when cookies, client code, redirects, or rendering are involved; capture the request and actual response. For an API-only issue, send the equivalent HTTP request. A rendered page or HTTP 200 alone does not establish that the intended Worker path ran.
2. Correlate that request with its invocation using the available trace identifiers, route, and time window. Follow handler, outbound fetch, and binding spans to the first divergent operation. Inspect the relevant logs and response body; absent spans alone do not prove an operation succeeded or never ran.
3. Inspect the smallest relevant state through Explorer: for example, D1 schema and the affected row, a KV key, R2 object metadata, SQLite Durable Object state, or Workflow instance history. Use read operations and bounded SQL queries for diagnosis. Local data edits, Workflow retries, and fixture seeding change state; keep them tied to the reproduction and avoid wholesale resets that erase the evidence.
4. Fix the demonstrated cause, then repeat the same action. Verify both the new trace and the expected response/state. If the request starts asynchronous work, check its completion or resulting state separately; successful enqueueing does not establish consumer success.

For example, a failing insert plus a missing local column may indicate an unapplied migration. Check the repository migration and actual target database before changing application SQL or applying the migration.

## Preserve evidence of the fix

Use the project's existing tests for the affected behavior. For a reusable regression check, consult [Workers testing](https://developers.cloudflare.com/workers/testing/) to choose runtime unit tests or integration tests across configured routes and production builds. Assert the externally relevant result or state transition, rather than only the absence of an exception.

Report the reproduction, observed cause, change, and verification evidence, including which resources were local or remote. Keep credentials and unrelated application data out of shared trace excerpts. State any untested boundary: local success does not verify deployed routing, Access policies, or network-specific behavior. For a deployed reproduction, consult [Workers Traces](https://developers.cloudflare.com/workers/observability/traces/) and check enablement and sampling before interpreting missing telemetry.
