# Configuration decisions

Read only the product docs relevant to the current decision. Record the actual choice and its owner. A recommendation is not an approved configuration.

## Identity and application compatibility

| Decision | Questions and documentation |
|---|---|
| Application type and scope | Which hostnames, paths, protocols, and clients need protection? Read [application types](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/index.md) and the [self-hosted application guide](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/index.md). Keep private-network and non-HTTP requirements separate from a public HTTP gate. |
| Human authentication | Which [identity providers](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/index.md), groups, MFA requirements, and device constraints apply? Inspect existing [Access policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/index.md) before adding new ones. |
| Sessions | What are the application's session, revocation, and logout requirements? Read [session management](https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/session-management/index.md) rather than inventing a session duration. Test Access and application sessions separately. |
| Machine and agent callers | Which workloads need [service tokens](https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/index.md)? Does a user-authorized client support [managed OAuth](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/managed-oauth/index.md)? Confirm the application's compatibility instead of introducing a Bypass policy for automation. |
| Application identity | Where can the [Access JWT be validated](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/index.md)? Validate at a supported connector, proxy, or application. Retain the application's own SAML/OIDC sign-in when it needs its IdP response to create a session. Do not assume an Access JWT replaces that exchange or application authorization. |

## Origin connection

Select a connection pattern from current docs. Record prerequisites, origin-side validation, every alternate route, and how those routes will be restricted.

| Pattern | Documentation and decisions |
|---|---|
| Tunnel | Read the [Tunnel setup guide](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/index.md) and [origin parameters](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/origin-parameters/index.md). Confirm connector placement, redundancy, removal of public ingress, and Access validation on each route. |
| Restricted public HTTPS origin | Read [origin protection](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/index.md), [Full (strict)](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/index.md), and [Authenticated Origin Pulls](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/index.md). Specify the firewall and account/hostname-specific origin authentication rather than treating a shared Cloudflare source range as deployment identity. |
| Dedicated CDN Egress IPs, optionally with CNI | Read [Dedicated CDN Egress IPs](https://developers.cloudflare.com/smart-shield/configuration/dedicated-egress-ips/index.md) and [Access with CNI](https://developers.cloudflare.com/smart-shield/configuration/dedicated-egress-ips/other-products/index.md). Check entitlements, assigned address pools, interconnect routing, origin TLS, and failover. This is an alternative to Tunnel, not a Tunnel prerequisite. |

Authenticated Origin Pulls does not apply to Tunnel origins. A server certificate authenticates the origin server, not the clients allowed to reach it. Protect the hop from any validating proxy to the application so callers cannot bypass validation on an internal route.

## Traffic, DNS, and operations

| Decision | Questions and documentation |
|---|---|
| DNS migration | Does the current [DNS setup](https://developers.cloudflare.com/dns/zone-setups/index.md) support the intended Access path? Record delegation, record parity, partial-setup eligibility where relevant, and mail/verification records that must remain unchanged. Do not proxy every discovered hostname. |
| Request filtering | Which [WAF controls](https://developers.cloudflare.com/waf/index.md) fit the app and plan? Base path/method restrictions and rate limits on known application behavior. Account for callbacks, WebSockets, uploads, and API clients. WAF is not a substitute for identity or patching. |
| Personalized responses | Inspect existing [cache rules](https://developers.cloudflare.com/cache/how-to/cache-rules/index.md) and any Worker in the path. Specify how personalized responses avoid shared-cache leakage. Authentication alone does not make a response safe to cache. |
| Ownership and recovery | Identify the owner of Access, DNS, firewall, Tunnel, shared rulesets, certificates, and IaC state. Define logging, failure thresholds, failover checks, and a recovery procedure that preserves protection. |

## Acceptance evidence

Define cases for the selected application and controls rather than assigning a universal test list. Record persona, test location, input class, expected result, observed result, timestamp, and evidence. Keep credentials out of test records.

Establish a legitimate-user positive control before interpreting missing origin logs. Test anonymous and unentitled callers, application permissions, direct/alternate origin routes, and each configured JWT validator separately. An Access rejection alone does not demonstrate origin-side JWT validation.

Include machine credentials, session expiry/revocation, cache separation, and failover when applicable. Label results **not tested** until exercised against the intended deployment. Distinguish local configuration validation from a deployed pilot and production acceptance.
