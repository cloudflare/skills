# Cloudflare WAN / Site Connectivity

## Assessment

Ask only the prompts relevant to the task.

- Site topology, on-ramp type, route ownership, tunnel redundancy, static vs BGP-managed routes, network firewall needs, and appliance/profile ownership. Retrieve [Cloudflare WAN](https://developers.cloudflare.com/cloudflare-wan/) and [Cloudflare Network Firewall](https://developers.cloudflare.com/cloudflare-network-firewall/) docs before proposing site connectivity changes.

## Guardrails

- Cloudflare WAN is connectivity, not a security service. Apply inspection and policy with Gateway and Network Firewall where required.
- WAN firewall expressions are not the same language as Gateway wirefilter expressions. Retrieve the current syntax before editing.
- Generated IPsec PSKs and some OAuth/client secrets are returned once. Store them immediately.

## Validation

- Cloudflare WAN: verify tunnel health, route priority/ownership, traffic flow, firewall expression syntax, and connector/appliance telemetry where applicable.
