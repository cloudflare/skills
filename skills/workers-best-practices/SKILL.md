---
name: workers-best-practices
description: Reviews and authors Cloudflare Workers code against production best practices. Load when writing new Workers, reviewing Worker code, configuring wrangler.jsonc, or checking for common Workers anti-patterns (streaming, floating promises, global state, secrets, bindings, observability).
---

Produce Workers code and reviews that are correct for the project's deployed runtime, safe under Workers platform constraints, and supported by proportionate evidence.

## Establish the Project Contract

Start with the project itself: its compatibility date and flags, pinned Wrangler and Workers types, generated environment types, configuration, package lockfile, tests, and established patterns. These define the contract an existing deployment must satisfy.

Do not silently judge pinned code against a newer platform version. When proposing an upgrade, distinguish problems in the current contract from opportunities that require changing a dependency, compatibility date, or flag.

Retrieve authoritative Cloudflare documentation or current published types when:

- the relevant API or configuration contract is absent, ambiguous, or disputed locally;
- the task explicitly targets the latest platform behavior or a version upgrade;
- a finding depends on behavior that may have changed since the pinned version; or
- the consequence of guessing is material and local validation cannot settle it.

Use the narrowest useful source: the installed type declarations or Wrangler schema for pinned behavior, and the official Workers documentation or release information for current behavior. Record the applicable version, compatibility date, or flag when it affects the conclusion. Do not download packages merely to begin a routine task.

## Reference Documentation

- `references/rules.md` — all best practice rules with code examples and anti-patterns
- `references/review.md` — type validation, config validation, binding access patterns, review process

## Rules Quick Reference

### Configuration

| Rule | Summary |
|------|---------|
| Compatibility date | Set `compatibility_date` to today on new projects; update periodically on existing ones |
| nodejs_compat | Enable the `nodejs_compat` flag — many libraries depend on Node.js built-ins |
| wrangler types | Run `wrangler types` to generate `Env` — never hand-write binding interfaces |
| Secrets | Use `wrangler secret put`, never hardcode secrets in config or source |
| wrangler.jsonc | Use JSONC config for non-secret settings — newer features are JSON-only |

### Request & Response Handling

| Rule | Summary |
|------|---------|
| Streaming | Stream large/unknown payloads — never `await response.text()` on unbounded data |
| waitUntil | Use `ctx.waitUntil()` for post-response work; do not destructure `ctx` |

### Architecture

| Rule | Summary |
|------|---------|
| Bindings over REST | Use in-process bindings (KV, R2, D1, Queues) — not the Cloudflare REST API |
| Queues & Workflows | Move async/background work off the critical path |
| Service bindings | Use service bindings for Worker-to-Worker calls — not public HTTP |
| Hyperdrive | Always use Hyperdrive for external PostgreSQL/MySQL connections |

### Observability

| Rule | Summary |
|------|---------|
| Logs & Traces | Enable `observability` in config with `head_sampling_rate`; use structured JSON logging |

### Code Patterns

| Rule | Summary |
|------|---------|
| No global request state | Never store request-scoped data in module-level variables |
| Floating promises | Every Promise must be `await`ed, `return`ed, `void`ed, or passed to `ctx.waitUntil()` |

### Security

| Rule | Summary |
|------|---------|
| Web Crypto | Use `crypto.randomUUID()` / `crypto.getRandomValues()` — never `Math.random()` for security |
| No passThroughOnException | Use explicit try/catch with structured error responses |

## Anti-Patterns to Flag

| Anti-pattern | Why it matters |
|-------------|----------------|
| `await response.text()` on unbounded data | Memory exhaustion — 128 MB limit |
| Hardcoded secrets in source or config | Credential leak via version control |
| `Math.random()` for tokens/IDs | Predictable, not cryptographically secure |
| Bare `fetch()` without `await` or `waitUntil` | Floating promise — dropped result, swallowed error |
| Module-level mutable variables for request state | Cross-request data leaks, stale state, I/O errors |
| Cloudflare REST API from inside a Worker | Unnecessary network hop, auth overhead, added latency |
| `ctx.passThroughOnException()` as error handling | Hides bugs, makes debugging impossible |
| Hand-written `Env` interface | Drifts from actual wrangler config bindings |
| Direct string comparison for secret values | Timing side-channel — use `crypto.subtle.timingSafeEqual` |
| Destructuring `ctx` (`const { waitUntil } = ctx`) | Loses `this` binding — throws "Illegal invocation" at runtime |
| `any` on `Env` or handler params | Defeats type safety for all binding access |
| `as unknown as T` double-cast | Hides real type incompatibilities — fix the design |
| `implements` on platform base classes (instead of `extends`) | Legacy — loses `this.ctx`, `this.env`. Applies to DurableObject, WorkerEntrypoint, Workflow |
| `env.X` inside platform base class | Should be `this.env.X` in classes extending DurableObject, WorkerEntrypoint, etc. |

## Apply Judgment

Inspect enough surrounding code and configuration to understand binding access, runtime boundaries, and deployment assumptions. Focus the review or implementation on risks relevant to the change: types and binding consistency, streaming and memory use, promise lifetime, cross-request state, serialization, secrets and cryptography, observability, and explicit error handling.

Validate in proportion to the change. Prefer the project's own typecheck, tests, lint rules, and Wrangler validation. For a review, report only findings supported by code, local contracts, tool output, or a directly relevant official source. See `references/review.md` for deeper review guidance and `references/rules.md` for Workers-specific patterns.

## Scope

This skill covers Workers-specific best practices and code review. For related topics:

- **Durable Objects**: load the `durable-objects` skill
- **Workflows**: see [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)
- **Wrangler CLI commands**: load the `wrangler` skill

## Principles

- **Be certain.** Verify uncertain API or configuration claims against the applicable local contract or authoritative documentation before flagging them.
- **Provide evidence.** Reference line numbers, tool output, or docs links.
- **Focus on what developers will copy.** Workers code in examples and docs gets pasted into production.
- **Correctness over completeness.** A concise example that works beats a comprehensive one with errors.
