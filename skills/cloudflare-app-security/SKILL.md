---
name: cloudflare-app-security
description: Configure and troubleshoot Cloudflare web application protection using WAF, rate limiting, bot controls, DDoS signals, and API Shield. Use for abusive traffic, blocked legitimate requests, and operational protection rollout; not source-code security scans or Access identity policies.
---

# Cloudflare application security

Turn observed traffic into a scoped protection change, verify legitimate clients still work, and retain a recovery path. Preserve the user's existing application authentication, client integrations, infrastructure tooling, and authorized scope.

## Identify the request and enforcement layer

Establish the affected account, zone, hostname, route, time window, and expected client behavior from available configuration and evidence. Check how the hostname reaches the Worker or origin; a rule in one zone is not evidence that alternate application entry points are protected.

Use [Security Events](https://developers.cloudflare.com/waf/analytics/security-events/) to identify the acting product, action, rule/ruleset IDs, and request details. Correlate Ray IDs and timestamps with application logs where available. Security Events covers flagged or actioned traffic, can be sampled, and can contain multiple events per request; it is not a complete request log. Use the linked Security Analytics workflow for the broader traffic baseline. A 403 or 429 alone does not establish which layer rejected a request.

Before writing expressions, inspect existing rules, order, scope, and the account's actual entitlements. Read the selected product's current documentation below for supported fields, actions, and availability rather than copying limits or rule payloads from memory.

## Choose the control that matches the signal

| Signal or task | Start here | Decision to make |
|---|---|---|
| Requests match known exploit patterns or a managed rule blocks valid input | [Managed-rule exceptions](https://developers.cloudflare.com/waf/managed-rules/waf-exceptions/) | Identify the individual rule and matching request subset before changing an entire ruleset. |
| A known abusive request pattern needs targeted enforcement | [Custom rules](https://developers.cloudflare.com/waf/custom-rules/) | Select supported expression fields and an action compatible with affected clients. Check Log and regex availability before proposing them. |
| Repeated requests exhaust an endpoint | [Rate limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/) | Derive the threshold from legitimate bursts; distinguish the matching expression, counting characteristics, period, and mitigation duration. Check supported parameters for this plan. |
| Scraping or other automated traffic | [Bot plans](https://developers.cloudflare.com/bots/plans/) | Identify Bot Fight Mode, Super Bot Fight Mode, or Bot Management before choosing controls; preserve intended API clients and crawler policy. |
| Traffic flood or a DDoS rule false positive | [DDoS protection](https://developers.cloudflare.com/ddos-protection/) | Inspect the automatic mitigation and use the documented customization for the affected layer and plan. Do not infer an attack from volume alone. |
| API inventory, schema, token, or client-certificate enforcement | [API Shield](https://developers.cloudflare.com/api-shield/) | Follow the specific feature and availability links; preserve the API's current authentication and schema contract. |

For form-token verification, use the `turnstile-spin` skill. For identity-based access policies, use `cloudflare-one`. Do not expand traffic protection into an application authentication rewrite or repository vulnerability scan.

## Make a bounded change

- Capture the current rule and its position, enabled state, scope, and affected hostname/path. Prepare a minimal diff through the user's existing dashboard, API, or infrastructure-as-code workflow; avoid replacing a shared ruleset to edit one rule.
- Read [WAF phase ordering](https://developers.cloudflare.com/waf/reference/phases/) before interpreting a missing match. Custom rules precede rate limiting and managed rules; account rules precede zone rules within each phase. An earlier terminating action can prevent later rules from running.
- For false positives, prefer the offending managed rule's narrowly matched exception. Check [skip options](https://developers.cloudflare.com/waf/custom-rules/skip/options/): account-level skips do not skip zone-level rules, and Bot Fight Mode cannot be skipped. Do not convert one client's failure into a zone-wide bypass or skip unrelated protections. A user-agent string or an unverified client-supplied header alone is not proof of a trusted client.
- Rate limits are abuse controls, not exact billing quotas. Counter updates can lag; consider shared-IP clients and whether the chosen counting key is trustworthy. Browser challenges can break API clients, mobile applications, and webhooks; test the actual client type when selecting an action.
- Apply live changes only within existing authorization. When the request is for review or a proposed configuration, deliver the concrete diff and verification plan. Reuse authorization already granted for implementation; do not insert a blanket confirmation step.

## Verify, observe, and recover

Choose a bounded test scope and observation window. Use Log mode when supported and suitable; otherwise use available historical evidence and an isolated test hostname or narrowly scoped rollout. A locally valid expression does not prove deployed edge enforcement.

Check representative allowed traffic, the original false positive, a controlled abusive match, and nearby non-matching traffic. Include legitimate bursts/shared-IP clients for rate limits, actual non-browser callers for API routes, and unauthorized requests when an exception changes a protected path. Use harmless requests to test rule matching; do not generate a production flood as validation.

Compare client outcomes with the matched rule/action and application success/error signals. If legitimate failures increase or the change affects unexpected traffic, stop expanding it and restore the captured rule configuration within the authorized recovery scope. Report the exact scope and change, observed evidence, untested cases, and recovery operation. For temporary exceptions, record an owner and review/expiry condition instead of silently leaving a permanent bypass.
