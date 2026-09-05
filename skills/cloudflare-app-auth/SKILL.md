---
name: cloudflare-app-auth
description: Implement or troubleshoot login, sessions, and protected routes in applications on Cloudflare Workers, including native Workers and Cloudflare Access integration. Use for application authentication, not Wrangler account login or general Zero Trust network administration.
---

# Application authentication on Workers

Connect the application's identity system to its request handlers and verify that protected data requires the intended identity. Preserve the user's chosen auth provider, framework, and session model.

## Choose the authentication boundary

Inspect the existing auth middleware, callbacks, session storage, Worker configuration, generated deployment configuration, and public entry points before changing them.

| Requirement | Approach |
| --- | --- |
| Customer signup, social login, account recovery, or existing application sessions | Integrate the chosen auth provider/library with the Workers application. Read its current framework and runtime documentation before selecting an adapter. |
| Restrict an internal app or previews to employees, partners, or approved identities | Use [Cloudflare Access for Workers](https://developers.cloudflare.com/workers/configuration/cloudflare-access/). |
| Both customer accounts and employee-only administration | Keep customer sessions and Access policy scopes separate; map authenticated identities to application permissions explicitly. |
| Automated clients calling an Access-protected HTTP endpoint | Use [Access service tokens](https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/) and the documented Service Auth policy. A machine identity is not a signed-in customer. |

Access can provide the login boundary for an internal app without building a second login system. It does not implement an application's customer lifecycle or tenant authorization. Turnstile verifies bot challenges; it does not establish a user session.

## Customer login and sessions

- Reuse the existing provider's supported server-side integration. Verify Workers compatibility and required runtime flags against [external service integration guidance](https://developers.cloudflare.com/workers/configuration/integrations/external-services/) and the provider's current documentation; do not invent a Cloudflare-specific adapter.
- Wire the provider's login, callback, session lookup, and logout into the framework's server handlers. Use the provider's documented state/PKCE, redirect validation, cookie, CSRF, expiration, and revocation behavior. Keep application authorization at the server boundary, including tenant and resource ownership checks.
- Align callback URLs and cookie scope with the actual development, preview, and production origins. Store provider credentials and session signing secrets using [Workers secrets](https://developers.cloudflare.com/workers/configuration/secrets/), with separate environment configuration where required by the app.
- Inspect [Static Assets routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/): asset-first serving or SPA fallback can skip authentication middleware and OAuth callbacks. Arrange Worker-first routing for the paths requiring application checks; do not assume hiding a page protects its API or downloadable assets.

## Native Workers and Access integration

Read the [current integration guide](https://developers.cloudflare.com/workers/configuration/cloudflare-access/) before configuring protection. It is the implementation reference for the [Workers-protected-by-Access announcement](https://blog.cloudflare.com/workers-protected-by-access/).

1. Confirm Zero Trust is enabled and identify the existing Access applications, policies, Worker, and account. Select the scope the user needs: one Worker, all Workers, or a hostname/path; previews only or production and previews. A single-app request does not imply changing account-wide defaults.
2. For whole-Worker protection, attach Access to the Worker so protection follows its routes, Custom Domains, `workers.dev`, and previews. Use hostname/path protection for a deliberately narrower surface. Follow the guide for dashboard or API setup and reuse suitable existing policies.
3. Inspect [Access hierarchy](https://developers.cloudflare.com/workers/configuration/cloudflare-access/#understand-access-hierarchy) when policies overlap or a bypass exists. More specific rules take precedence; deleting one can expose a broader rule underneath. Do not assume layered policies are cumulative.
4. For directly authenticated Worker invocations, use [ctx.access](https://developers.cloudflare.com/workers/configuration/cloudflare-access/#read-authenticated-user-identity-with-ctxaccess) and its identity lookup instead of adding manual JWT plumbing. Keep app-specific permissions explicit and reject missing required identity claims.

### Identity context has boundaries

Read [ctx.access limitations](https://developers.cloudflare.com/workers/configuration/cloudflare-access/#ctxaccess-limitations) before implementing identity-dependent code:

- Service Binding HTTP and RPC invocations do not carry the caller's Access context into the downstream Worker. Treat downstream authorization as a separate application contract; do not trust an arbitrary forwarded email header.
- With Static Assets, Access still protects the app and assets, but the internal router does not pass `ctx.access` to the user Worker. Inspect generated configuration too: the Vite plugin can add assets. Worker-first asset routing does not establish that context propagation works.
- If identity is needed where native context is unavailable, consult [Access JWT validation](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/) for a supported request-token integration. Validate the signature, expected issuer and audience, and token lifetime before trusting claims; decoding a header alone is insufficient. Verify that the actual request path supplies the token.

## Verify the boundary

For handlers that consume native `ctx.access`, use the [local Access simulation](https://developers.cloudflare.com/workers/configuration/cloudflare-access/#test-ctxaccess-locally): configure `access.dev` with an audience and test identity, then remove the development block to exercise missing context. This exercises native-context handling; it does not inject a request JWT, test a JWT fallback, or prove deployed Access policy enforcement.

For a request-token fallback, test the verifier separately using signed test tokens and verifier fixtures: valid claims, invalid signature, wrong issuer or audience, and expired tokens. On the deployed request path, verify token presence and rejection of missing or invalid tokens; this is especially relevant when Static Assets makes native context unavailable.

Test the flows affected by the change:

- Customer auth: successful login and callback, invalid callback/state, missing or expired session, logout, and authenticated users denied another tenant's data.
- Access: allowed and denied identities, unauthenticated access, and machine authentication if configured. Exercise the relevant custom domain, `workers.dev`, and preview URLs, including static assets and protected API routes.
- Routing: callbacks reach server code, public routes remain usable as intended, and protected resources cannot be reached through an alternate entry point.

Report which local and deployed checks actually ran, the effective policy scope, and any remaining provider configuration. Distinguish a local identity simulation from a successful browser sign-in and deployed denial check.
