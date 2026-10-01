---
name: k2
description: Build and troubleshoot Cloudflare K2 or K2 Streams durable logs. Use for stream setup, producing from Workers or HTTP, configuring retention and inputs, and consuming through subscriptions.
---

# Cloudflare K2

K2 is a durable log for decoupling event producers and consumers. Start with the [K2 overview](https://developers.cloudflare.com/k2/index.md), then retrieve the relevant current documentation before giving setup instructions, code, limits, availability, permissions, or API details. The docs are the source of truth over this skill. While [cloudflare-docs PR #33858](https://github.com/cloudflare/cloudflare-docs/pull/33858) remains open, use its proposed pages if the public URLs have not been published.

## Documentation

| Task | Docs | Check for |
|------|------|-----------|
| Create a stream and try K2 | [Get started](https://developers.cloudflare.com/k2/get-started/index.md) | Prerequisites, setup sequence, current API examples |
| Understand streams and subscriptions | [Concepts](https://developers.cloudflare.com/k2/concepts/index.md) | Record model and delivery behavior |
| Configure a stream | [Configuration](https://developers.cloudflare.com/k2/configuration/index.md) | Inputs, authentication, CORS, retention |
| Produce from HTTP or a Worker | [Produce records](https://developers.cloudflare.com/k2/features/produce/index.md) | Request and binding syntax, encoding, errors, retries |
| Consume through subscriptions | [Consume records](https://developers.cloudflare.com/k2/features/consume/index.md) | Leases, acknowledgements, retries, errors |
| Size a stream or consumer | [Limits](https://developers.cloudflare.com/k2/platform/limits/index.md) | Current quotas and size limits |

Retrieve the matching pages above for each task and use their current examples. For capacity or cost questions, check current limits and any published pricing before quoting values. State when a requested pricing or availability detail is not yet published.

For SQL transformation and delivery to R2 Iceberg tables, use the `basin` skill. For task processing, consult [Queues](https://developers.cloudflare.com/queues/index.md).
