---
id: ops-017
name: Find and fix errors caused by your origin server
category: developer-platform-operate
description: Diagnose and resolve common origin misconfigurations — SSL mismatches, 5xx errors, timeouts, and DNS issues — so the site stops showing error pages.
products: [SSL/TLS, DNS, Health Checks, Analytics, Cache]
default_path: fix-5xx-errors
aliases:
  - Debug Cloudflare error pages
  - Origin troubleshooting
keywords:
  - "502 Bad Gateway"
  - "520 error"
  - "521 error"
  - "522 error"
  - "523 error"
  - "524 error"
  - "origin server not responding"
  - "SSL handshake failed"
  - "origin timeout"
  - "why is my site showing an error"
  - "Wikipedia of errors"
related:
  - start-001
  - sec-016
  - sec-010
  - perf-001
---

# Find and fix errors caused by your origin server

## Ask first

**What kind of error are you seeing?**
- 5xx error page (502, 520, 521, 522, 523, 524) → fix-5xx-errors
- SSL or certificate error → fix-ssl-errors
- Site is slow or timing out → fix-timeouts
- Site works sometimes but not always → fix-timeouts
- Not sure what the error means → fix-5xx-errors, then fix-ssl-errors

**When did the problem start?** (helps narrow SSL vs other causes)
- Right after adding the site to Cloudflare → fix-ssl-errors
- After changing DNS or SSL settings → fix-ssl-errors
- Random or intermittent → fix-timeouts
- Not sure → start with fix-5xx-errors

## Paths

### fix-5xx-errors (default)

To diagnose and fix 5xx error pages:

1. Check Analytics to identify which error codes are most common and when they started
2. Confirm via Health Checks that the origin server is online and responding
3. Confirm DNS records point to the correct origin IP
4. Ensure the SSL/TLS encryption mode matches the origin setup (use Full (strict) if the origin has a valid certificate)
5. Look up the specific error code (520-524) for targeted troubleshooting steps

### fix-ssl-errors

To fix SSL and certificate errors (top cause: mode mismatch between Flexible/Full/Full (strict) and the origin):

1. Verify the SSL/TLS mode against the origin
2. Check that the origin has a valid certificate installed (use a Cloudflare Origin CA certificate if needed)
3. Make sure the full certificate chain is installed on the origin
4. Enable Always Use HTTPS to prevent mixed content issues

### fix-timeouts

To resolve slow responses and timeouts:

1. Set up Health Checks to monitor origin response time and availability
2. Check Analytics for origin response time trends to identify when slowdowns occur
3. Test the origin server directly (bypassing Cloudflare) to confirm the issue is origin-side
4. Cache more content on Cloudflare to reduce load on the origin

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/ssl/, /dns/, /health-checks/, /analytics/, /cache/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
