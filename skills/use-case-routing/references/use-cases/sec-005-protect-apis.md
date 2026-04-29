---
id: sec-005
name: Protect APIs from abuse and attack
category: network-application-security
description: Discover, validate, and secure API endpoints with schema validation and sequence enforcement.
products: [API Shield, API Gateway, WAF]
default_path: api-discovery
aliases:
  - API schema validation
  - API sequence enforcement
  - API discovery
keywords:
  - "OpenAPI schema validation"
  - "Swagger validation"
  - "mTLS for APIs"
  - "API rate limiting"
  - "API abuse"
  - "API data exfiltration"
  - "shadow API endpoints"
  - "unauthorized API access"
related:
  - sec-002
  - sec-004
  - sec-011
---

# Protect APIs from abuse and attack

## Ask first

**Do you have an OpenAPI specification?**
- Yes, an OpenAPI/Swagger spec is available → schema-based-protection
- No spec, or a different format → api-discovery
- Not sure what API documentation exists → api-discovery

**What is the primary API security concern?**
- Unauthorized access and authentication → api-auth
- Abuse and excessive usage → add WAF rate limiting on top of the chosen path
- Data exfiltration via API → schema-based-protection (with sequence enforcement)

## Paths

### api-discovery (default)

When no schema exists yet:

1. Enable API Discovery to map all endpoints
2. Review discovered endpoints and mark them as managed
3. Generate a learned schema from observed traffic patterns
4. Add WAF rate limiting for discovered endpoints

### schema-based-protection

When an OpenAPI schema is available:

1. Upload the OpenAPI schema to API Shield for validation
2. Enable schema validation to block non-conforming requests
3. Define expected API call sequences with sequence enforcement
4. Add per-endpoint rate limiting in WAF

### api-auth

For mTLS-based API authentication:

1. Set up mutual TLS in API Shield
2. Issue client certificates for authorized consumers
3. Add a WAF custom rule to block requests without a valid client certificate

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/api-shield/, /waf/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
