---
name: identity-gated-edge-migration
description: Inventory self-hosted HTTP applications and plan their migration behind Cloudflare Access, including DNS discovery, identity policies, origin restrictions, staged rollout, and validation. Use for identity-gated edge migration planning, not VPN/SASE vendor migrations or authenticating a client to an existing Access application.
---

# Identity-gated edge migration

Produce a local migration plan for putting selected HTTP applications behind Cloudflare Access. Start with the organization's existing DNS and application inventory, not a new Cloudflare configuration.

Match the requested scope. An inventory-only request does not authorize a migration or require a full configuration interview. Use `cloudflare-one-migrations` for VPN, SWG, or SASE replacement. Use `cloudflare-one` when a caller only needs to authenticate to an existing Access-protected application.

## Sources and boundaries

- Read the current [self-hosted application guide](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/index.md) and the specific docs linked from [configuration decisions](references/decisions.md) before recommending settings, API fields, plan availability, or exact configuration. Do not invent unsupported defaults.
- Discovery and planning are read-only against external systems. Confirm the account, DNS provider, authentication profile, and inventory scope before queries. Prefer the `cf-cli` skill for Cloudflare operations, with supported MCP or API tools as a fallback.
- Keep credentials in the user's existing secret store or environment. Do not request tokens in chat or include credentials, cookies, private keys, or verification-token values in the plan.
- Obtain approval before third-party inventory searches, active application probes, infrastructure changes, or publishing the plan. Show the affected resources immediately before an external change. Generating a plan or local configuration does not authorize applying it.

## Workflow

### 1. Establish scope

Identify the application owners, current DNS providers and accounts, intended callers, existing sign-in methods, and the migration goal. Ask only for information missing from available configuration or exports.

Agree on a plan path, defaulting to `identity-gated-edge-plan.md`. Resume an existing plan without overwriting decisions. Use [the plan template](assets/plan-template.md) for a new full migration plan, omitting sections outside the requested scope. Record existing IaC tooling and ownership before proposing generated files.

### 2. Discover and classify

Follow [DNS and application discovery](references/discovery.md). Use provider exports or read-only CLI/API listings. Record inaccessible accounts and incomplete pagination as coverage gaps, not empty inventories.

Start each application as `Unknown`. Propose classifications with supporting evidence and confirm them with the owner:

- **Protect:** the owner wants Access authentication before requests reach the HTTP application.
- **Public:** intentionally reachable without Access, with the reason recorded. This does not imply changing its DNS or proxy status.
- **Unknown:** insufficient evidence or an unresolved ownership or compatibility decision.

Preserve classifications, owners, authentication details, and notes on repeated discovery. Do not infer that a hostname is safe to migrate from its name or an HTTP status alone. Keep non-HTTP services, SaaS dependencies, callbacks, and DNS verification records distinct from protected web applications.

### 3. Make configuration decisions

Read [configuration decisions](references/decisions.md) for the relevant application class. Group questions by shared requirements rather than interviewing the user once per hostname.

Record each decision, rationale, documentation source, owner, and unresolved prerequisite. Cover human and machine authentication, application permissions, origin connectivity, Access JWT validation, existing application sign-in, caching, observability, and rollback. Mark unanswered decisions as unresolved, not accepted defaults.

Respect an existing approved origin pattern. If none is selected, evaluate Tunnel when the environment can run a connector and remove public origin ingress. Otherwise, evaluate restricted HTTPS origins or Dedicated CDN Egress IPs with CNI using the linked documentation. Neither source-IP allowlisting nor an Access redirect alone establishes that every origin path is protected.

### 4. Plan and verify the rollout

Select one owned pilot application. Record the current route, target route, dependencies, intended change sequence, and recovery procedure. Create Access protection before publishing a new Tunnel route. Keep existing applications protected during cutover and identify any temporary direct-origin exposure with an owner and deadline.

Define both legitimate-user and denial checks. Start every result as **not tested**. A configured policy, generated file, or successful redirect is not evidence that the protected application works or that alternate origin routes are closed.

Include browser and machine callers, application authorization, direct-origin and alternate-hostname attempts, invalid assertions at each validator, session lifecycle, personalized caching, and failover where applicable. Correlate edge outcomes with origin logs. A working positive control must establish that the evidence collection can observe successful requests.

### 5. Generate implementation artifacts only when requested

Match the user's existing IaC tool, provider version, and state ownership. Retrieve current resource schemas and inspect existing DNS, Access, Tunnel, and zone-level rulesets before generating changes. Extend or import owned resources rather than blindly replacing shared configuration.

Use the `cf-cli` skill for CLI discovery and the current product docs for unsupported operations. Do not claim that one CLI supports every needed API. Keep secrets out of generated files and report which formatting, validation, or plan commands actually ran. Apply and deployment remain separately approved actions.

Finish with the plan path, coverage and classification counts, unresolved risks, validation status, and the next action within the user's requested scope.
