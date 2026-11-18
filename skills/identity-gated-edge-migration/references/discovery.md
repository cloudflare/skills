# DNS and application discovery

Read this reference when collecting or refreshing an application inventory. Discovery does not change DNS, proxy status, or Access configuration.

## Select the source

Ask where authoritative DNS is managed, which accounts or projects are in scope, and whether public and private views coexist. An account at a registrar does not establish where its DNS records are hosted.

| Existing provider | Read-only starting point |
|---|---|
| Google Cloud DNS | Approved project scope, zone exports, or read-only `gcloud` listings |
| AWS Route 53 | Approved accounts and profiles, hosted zones, record sets, and alias targets |
| Azure DNS | Approved subscriptions and resource groups, public/private zones, and record sets |
| Cloudflare | The selected account/profile, zones, records, and current proxy status through `cf` or supported read-only tools |
| DigitalOcean | Approved teams and `doctl` context, domains, and record listings |
| Registrar, appliance, or another DNS provider | An existing zone-file export or the provider's documented read-only API |

Check the installed CLI's help and the provider's current docs before constructing commands. Verify the selected identity without printing credentials. Handle pagination and scope limits, and record permission failures. Do not enable a provider API, change a profile, or escalate credentials to finish discovery without approval.

When the provider is unknown, inspect nameserver delegation for the user-supplied apex domains. Distinguish authoritative public records from stale exports, delegated subzones, and split-horizon/private records. A zone listing is not proof that it serves current traffic.

## Inventory fields

Retain enough provenance to explain every application candidate:

| Field | Record |
|---|---|
| Source | Provider, account/project/subscription, zone, public/private view, collection time, and method |
| DNS | Hostname, record types, relevant destination, proxy status where available, and delegation evidence |
| Application | Owner, protocol/port, existing authentication, users, service callers, and native-client dependencies |
| Alternate routes | IPv4/IPv6 listeners, additional hostnames, load balancers, failover sites, and direct origin paths |
| Classification | Protect/Public/Unknown, the owner's decision, supporting evidence, and unresolved questions |

Keep raw exports local and out of version control unless the owner approves an appropriate redacted artifact. Omit secret-bearing TXT values and unrelated records from the migration plan. Record secret-store references, never secret values.

Normalize DNS names for comparison, but retain their provider and public/private context. Do not merge conflicting records across accounts or views into an apparently authoritative result. Preserve previous owner decisions when refreshing records. Mark removed or newly discovered entries for review rather than silently deleting existing decisions.

## Coverage and classification limits

DNS alone does not identify all externally reachable services. Ask about bare-IP listeners, delegated zones, SaaS domains, unmanaged appliances, IPv6, and another team's records when relevant. Existing cloud load-balancer, ingress, or attack-surface inventories can supply missing ownership and route information.

Treat login-like labels, redirects, and status codes as hints. A customer-facing sign-in page may need to remain public. A verification CNAME is not necessarily an HTTP application. A native VPN or remote-desktop client is not automatically protected by gating its web portal.

Ask before sending domain names to Certificate Transparency search services or scanners. Ask before active probes, keep them within the approved scope, and preserve TLS verification. Do not follow redirects with credentials or capture session tokens in shared output.

Report sources successfully inspected, coverage gaps, candidate application counts, and unresolved classifications. Do not describe the inventory as exhaustive when there are uninspected accounts, private views, listeners, or delegated zones.
