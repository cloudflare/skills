---
name: k2
description: Build and troubleshoot Cloudflare K2 or K2 Streams durable logs. Use for stream setup, producing from Workers or HTTP, configuring retention and inputs, and consuming through subscriptions.
---

# Cloudflare K2

K2 is a durable log for decoupling event producers and consumers. Start with the [K2 overview](https://developers.cloudflare.com/k2/index.md), then retrieve the relevant current documentation before giving setup instructions, code, limits, availability, permissions, or API details. The docs are the source of truth over this skill. K2 is in public beta on the Workers Paid plan; check the overview for current availability and beta storage limits.

## Documentation

| Task | Docs | Check for |
|------|------|-----------|
| Create a stream and try K2 | [Get started](https://developers.cloudflare.com/k2/get-started/index.md) | Prerequisites, setup sequence, current API examples |
| Understand streams and subscriptions | [Concepts](https://developers.cloudflare.com/k2/concepts/index.md) | Record model and delivery behavior |
| Configure a stream | [Configuration](https://developers.cloudflare.com/k2/configuration/index.md) | Inputs, authentication, CORS, retention |
| Produce from HTTP or a Worker | [Produce records](https://developers.cloudflare.com/k2/features/produce/index.md) | Request and binding syntax, encoding, errors, retries |
| Consume through subscriptions | [Consume records](https://developers.cloudflare.com/k2/features/consume/index.md) | Leases, acknowledgements, retries, errors |
| Reason about duplicates and redelivery | [Delivery guarantees](https://developers.cloudflare.com/k2/reference/delivery-guarantees/index.md) | At-least-once delivery, leases, retention effects |
| Size a stream or consumer | [Limits](https://developers.cloudflare.com/k2/platform/limits/index.md) | Current quotas and size limits |
| Estimate cost | [Pricing](https://developers.cloudflare.com/k2/platform/pricing/index.md) | Billing status, data produced, consumed, and retained |

Retrieve the matching pages above for each task and use their current examples. For capacity or cost questions, check current limits and pricing before quoting values, and state whether billing is enabled yet.

For SQL transformation and delivery to R2 Iceberg tables, use the `basin` skill. For task processing, consult [Queues](https://developers.cloudflare.com/queues/index.md).

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
