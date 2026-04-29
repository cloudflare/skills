---
id: sec-001
name: Prevent DDoS attacks
category: network-application-security
description: Protect applications and networks from denial-of-service attacks of any size and kind.
products: [DDoS Protection, Magic Transit, Spectrum, WAF, Smart Shield]
default_path: l7-ddos
aliases:
  - L3/L4 DDoS protection
  - Magic Transit deployment
  - Network DDoS protection
keywords:
  - "stop DDoS attack"
  - "site under attack"
  - "active attack"
  - "I'm Under Attack Mode"
  - "denial of service"
related:
  - net-006
  - sec-002
  - sec-019
  - net-004
  - net-005
---

# Prevent DDoS attacks

## Ask first

**What are you protecting?**
- Web applications (HTTP/HTTPS) → l7-ddos
- Network infrastructure (IP subnets, data centers) → network-ddos
- Non-HTTP services (gaming, email, custom TCP/UDP) → spectrum-ddos

**Do you have your own IP address space?** (network infrastructure only)
- Yes (own ASN/IP prefixes) → enables Magic Transit
- No → use Spectrum or L7 protection instead

**Deployment model?** (Magic Transit only)
- Always-on (traffic always routed through Cloudflare)
- On-demand (activate during attacks only)

If the user describes an active attack regardless of asset type, also
walk the `active-incident` path.

## Paths

### l7-ddos (default)

For web application protection:

- Enable HTTP DDoS Attack Protection managed ruleset
- Enable Adaptive DDoS Protection for traffic profiling
- Add WAF rate limiting rules as an additional layer

### network-ddos

For network infrastructure with own IP space (Magic Transit):

1. Onboard IP prefixes to Cloudflare via BGP
2. Configure GRE or IPsec tunnels for clean traffic return
3. Enable tunnel health checks and automatic failover
4. Add Magic Firewall (Smart Shield) rules for granular traffic control

**For always-on:** advertise prefixes immediately and enable flow
analytics for traffic visibility.

**For on-demand:** register prefixes without advertising, pre-configure
tunnels for activation, and set up the activation trigger (API,
dashboard, or auto-detection).

### spectrum-ddos

For non-HTTP services:

1. Create a Spectrum application for the TCP/UDP service
2. Point to the origin server IP and port
3. Monitor mitigation in Security Analytics

### active-incident

For an ongoing attack regardless of asset type:

1. Confirm the attack via Security Analytics and traffic graphs
2. Enable I'm Under Attack Mode (immediate JS challenge on all requests)
3. Create WAF custom rules to block attack patterns (IP ranges, ASNs, countries)
4. Increase DDoS managed rule sensitivity to High
5. Contact Cloudflare support for Enterprise-tier mitigation
6. After the attack: review analytics and tune rules to prevent recurrence

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/ddos-protection/, /magic-transit/,
/spectrum/, /waf/, /magic-firewall/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
