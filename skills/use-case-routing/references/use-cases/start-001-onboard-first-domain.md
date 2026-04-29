---
id: start-001
name: Onboard your first domain to Cloudflare
category: getting-started
description: Add a domain, configure DNS, enable the proxy, and turn on baseline security and performance settings.
products: [DNS, SSL/TLS, CDN, Registrar]
default_path: existing-domain-onboard
aliases:
  - Add a domain to Cloudflare
  - Set up a new Cloudflare site
  - First-time Cloudflare setup
keywords:
  - "add domain"
  - "change nameservers"
  - "orange cloud"
  - "proxy DNS records"
  - "Full strict SSL"
  - "Always Use HTTPS"
  - "register new domain"
related:
  - start-002
  - perf-013
  - sec-017
---

# Onboard your first domain to Cloudflare

## Ask first

**Do you already have a domain registered?**
- Yes, at another registrar → existing-domain-onboard
- No, I need to register a new domain → new-domain-onboard

**What is the primary goal?** (informational; both paths cover both)
- Security (DDoS protection, WAF)
- Performance (CDN, caching)
- Both security and performance

## Paths

### existing-domain-onboard (default)

For a domain registered at another registrar:

1. Create a Cloudflare account
2. Add the domain to Cloudflare
3. Review the auto-scanned DNS records for accuracy
4. Update nameservers at the current registrar to Cloudflare's
5. Set the SSL/TLS encryption mode to Full (strict)
6. Enable Always Use HTTPS
7. Verify DNS records are proxied (orange cloud)

### new-domain-onboard

To register a new domain at Cloudflare and onboard it:

1. Search for an available domain
2. Register it through Cloudflare Registrar (at-cost pricing)
3. Set the SSL/TLS encryption mode to Full (strict)
4. Configure basic caching rules

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/dns/, /ssl/, /cache/, /registrar/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
