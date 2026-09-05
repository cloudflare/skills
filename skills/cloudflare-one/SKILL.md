---
name: cloudflare-one
description: "Guides Cloudflare One Zero Trust and SASE work across Access, Gateway, WARP, Tunnel, Cloudflare WAN, DLP, CASB, device posture, and identity. Use when designing, configuring, troubleshooting, or reviewing Cloudflare One deployments. Retrieval-first: use current Cloudflare docs/API schemas instead of embedded product docs."
---

# Cloudflare One

Before citing limits, settings, API fields, category IDs, or exact UI paths, retrieve current information from the [Cloudflare One docs](https://developers.cloudflare.com/cloudflare-one/), the Cloudflare docs MCP server, or the Cloudflare API schema.

## Workflow

1. Classify the ask: architecture, configuration, troubleshooting, migration, or review.
2. Gather context: account ID, users/sites/apps, identity provider, SCIM/group sync, device management, traffic path, compliance constraints, and rollout blast radius.
3. Retrieve only the current docs needed for the products involved: Access, Gateway, WARP/device client, Tunnel/Mesh, Cloudflare WAN, DLP, CASB, device posture, or identity.
4. If account access is available, inspect existing resources before proposing or making changes: Access apps/policies/groups/IdPs, Gateway rules/lists/categories, device profiles/posture checks, tunnels/routes, DNS/resolver settings, and locations/sites.
5. Propose the change set with prerequisites, validation, and rollback. For risky changes, stage disabled or scoped to a pilot group/site unless the user explicitly asks otherwise.

## Product references

Use the assessment prompts, guardrails, and validation for the products involved; ask only relevant questions.

| Topic | Reference |
|-------|-----------|
| Architecture and Current State | [architecture.md](references/architecture.md) |
| Access and SaaS Federation | [access.md](references/access.md) |
| Device Client Deployment | [device-client.md](references/device-client.md) |
| Tunnel and Private Networking | [private-networking.md](references/private-networking.md) |
| Gateway, TLS, and DLP | [gateway-tls-dlp.md](references/gateway-tls-dlp.md) |
| CASB, Device Posture, and Risk | [casb-posture-risk.md](references/casb-posture-risk.md) |
| Infrastructure Access | [infrastructure-access.md](references/infrastructure-access.md) |
| Logs, Analytics, and DEX | [logs-analytics-dex.md](references/logs-analytics-dex.md) |
| Cloudflare WAN / Site Connectivity | [wan.md](references/wan.md) |

## Guardrails

- Access controls application authorization; Gateway controls traffic inspection/filtering. Use both when the requirement spans identity-aware app access and network/web security.
- Public hostname Access apps can be clientless. Private destination apps require WARP/Device client or another network on-ramp plus routes and DNS resolution. Retrieve [self-hosted private app](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/self-hosted-private-app/) docs before configuring private destinations.
- Cloudflare Tunnel is an off-ramp from a private network to Cloudflare. Cloudflare WAN and Mesh are other off-ramps which can also be on-ramps.
- Group-based policies depend on IdP group claims or SCIM. If group sync is missing, do not invent group selectors.
- Private hostnames need explicit DNS routing/resolution; creating an Access app alone is not enough. Use [resolver policies](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) and review [Connect a private hostname](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/connect-private-hostname/)
- HTTP inspection and DLP for encrypted web traffic require TLS inspection and planned Do Not Inspect exceptions.
- Gateway DNS, Network, HTTP, and Egress policies have different evaluation semantics. Retrieve [order of enforcement](https://developers.cloudflare.com/cloudflare-one/traffic-policies/order-of-enforcement/) docs before explaining precedence.
- Start broad block/allow/DLP/TLS policies disabled limited to a pilot with specific target users or groups unless the user approves a wider rollout.

## Output Defaults

- Designs: current assumptions, target architecture, product responsibilities, rollout phases, validation, and open decisions.
- Configuration work: prerequisites, exact resources to inspect/create/change, test cases, and rollback.
- Troubleshooting: traffic path, likely failure point, evidence to collect, and next test.

## API Safety

- Use fully qualified MCP tool names when MCP tools are available.
- Never guess category IDs, application IDs, wirefilter fields, or API request bodies. Retrieve the current schema/docs and existing account objects.
- Do not enable broad production policies without explicit approval.
