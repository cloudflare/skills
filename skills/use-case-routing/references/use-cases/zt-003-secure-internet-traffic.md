---
id: zt-003
name: Protect users from web threats and enforce browsing policies
category: zero-trust-secure-access
description: Filter DNS and HTTP traffic to protect users from malware, phishing, and malicious sites and to enforce acceptable use policies for web and SaaS access.
products: [Gateway, Browser Isolation, DLP, WARP]
default_path: swg-deployment
aliases:
  - Secure Web Gateway
  - SWG deployment
  - Filter and protect web browsing
  - Enforce acceptable use policies
  - Secure guest WiFi
keywords:
  - "block malicious sites"
  - "phishing protection"
  - "DNS filtering"
  - "URL filtering"
  - "acceptable use policy"
  - "TLS inspection"
  - "isolate risky websites"
  - "remote browser isolation"
related:
  - zt-008
  - zt-010
  - zt-011
---

# Protect users from web threats and enforce browsing policies

## Ask first

**What do you want to secure?**
- Employee Internet browsing → swg-deployment
- SaaS application access → swg-deployment
- Guest WiFi network → dns-only-filtering
- Both employee and SaaS → swg-deployment

**What level of filtering is needed?**
- DNS-only filtering (block malicious domains) → dns-only-filtering
- Full HTTP/HTTPS inspection → full-swg
- DNS filtering plus selective HTTP inspection → swg-deployment

**Do you need to isolate risky web content?**
- Yes, browser isolation matters → swg-with-isolation
- No, filtering and inspection is sufficient → continue with the chosen path above

## Paths

### swg-deployment (default)

Standard Secure Web Gateway deployment:

1. Deploy the WARP client to route user traffic through Gateway
2. Create DNS filtering policies to block malicious domains
3. Create HTTP inspection policies for content filtering
4. Enable TLS decryption for HTTPS traffic inspection
5. Add applications that should bypass TLS inspection to a do-not-inspect list

### swg-with-isolation

SWG with Browser Isolation for risky content:

1. Deploy the WARP client
2. Create DNS filtering policies
3. Create HTTP policies that use the isolate action for risky categories
4. Configure isolation policies (uncategorized, risky, etc.)
5. Set copy/paste and upload/download data controls for isolated sessions

### dns-only-filtering

Lightweight DNS-only filtering (good fit for guest WiFi):

1. Configure DNS locations or deploy WARP for DNS routing
2. Create DNS policies to block security threats
3. Block content categories per acceptable use policy

### full-swg

Full Secure Web Gateway with TLS inspection and DLP:

1. Deploy the WARP client to user devices
2. Create DNS filtering policies
3. Create HTTP inspection policies
4. Enable TLS decryption
5. Install the Cloudflare root certificate on managed devices
6. Enable DLP profiles for HTTP traffic scanning

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-one/ (Gateway, Browser Isolation, DLP, WARP).
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
