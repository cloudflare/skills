---
name: flagship
description: Build and manage Cloudflare Flagship feature flags. Load for feature flags, typed flag values, targeting rules, percentage rollouts, OpenFeature SDKs, Workers flag evaluation, audit history, or Flagship API automation. Retrieve current docs before exact APIs.
---

# Cloudflare Flagship

Use Flagship for runtime feature flags, targeting, and gradual rollouts. Prefer Wrangler `vars` for static deploy-time configuration and KV/D1/Durable Objects for application data.

## Retrieval Sources

Your Flagship knowledge may be outdated. Retrieve current docs before exact API fields, limits, beta status, SDK names, or token scopes.

| Topic | URL |
| --- | --- |
| Overview | https://developers.cloudflare.com/flagship/ |
| Workers binding | https://developers.cloudflare.com/flagship/binding/ |
| OpenFeature SDKs | https://developers.cloudflare.com/flagship/sdk/ |
| API reference | https://developers.cloudflare.com/api/resources/flagship/ |

## Workflow

1. Classify the work: evaluate flags, create/update flags, design rollout rules, migrate from another flag system, or audit existing flags.
2. Inspect `wrangler.*`, generated types, package versions, and existing Flagship app/flag keys before coding.
3. For Workers, prefer the Flagship binding over outbound HTTP calls to Cloudflare APIs.
4. Model flag values deliberately: boolean for gates, string/number/object for variants, and typed defaults for every evaluation.
5. Design targeting and rollout rules with a rollback path. Keep high-risk launches disabled or narrowly targeted until validated.
6. After binding/config changes, run `npx wrangler types` and the project typecheck/tests.

## Workers Binding Pattern

Retrieve current config docs before editing `wrangler.jsonc`; binding shape may change while the product is in beta.

```typescript
const enabled = await env.FLAGS.getBooleanValue("new-checkout", false);
```

Evaluation should happen close to the decision point. Pass user, account, tenant, or request context according to current docs when targeting rules depend on attributes.

## Management API

- Use the API for account-level automation: apps, flags, changelog entries, and flag evaluation.
- Create a scoped API token with Flagship permissions; do not reuse broad account tokens in app code.
- Treat flag keys as stable contracts. Renaming a flag is a migration, not a cosmetic edit.
- Prefer disabled-by-default or conservative default variations when creating flags for production.

## Gotchas

- Always provide a default value in evaluation code so unavailable flag config fails predictably.
- Do not put secrets or sensitive per-user data in flag values, rules, metadata, logs, or audit descriptions.
- Avoid stale flag debt: add an owner, cleanup condition, and expected removal date for temporary rollout flags.
- Do not use Flagship as a general key-value store. If the value is not a feature decision, choose another product.
