# Sandbox troubleshooting documentation

[Confirm the package line](./README.md#choose-the-package-line-first) and matching image before diagnosing API errors. Fetch the relevant guide rather than applying a generic retry loop or fixed timeout.

| Symptom or decision | Documentation |
| --- | --- |
| Preview launch failures, stale handles, or interrupted work | [Errors and recovery](https://developers.cloudflare.com/sandbox/1-0-preview/errors/) and [Troubleshooting](https://developers.cloudflare.com/sandbox/1-0-preview/troubleshooting/) |
| Stable command failures | [Execute commands](https://developers.cloudflare.com/sandbox/guides/execute-commands/) |
| Files or interpreter state disappear after sleep/replacement | [Stable lifecycle](https://developers.cloudflare.com/sandbox/concepts/sandboxes/) or [preview lifecycle](https://developers.cloudflare.com/sandbox/1-0-preview/lifecycle/), then [Backup and restore](https://developers.cloudflare.com/sandbox/guides/backup-restore/). A filesystem path alone does not make data durable. |
| Container keeps running or startup is slow | [Sandbox options](https://developers.cloudflare.com/sandbox/configuration/sandbox-options/) and the lifecycle page for your package line |
| Local ports or production preview URLs fail | [Dockerfile reference](https://developers.cloudflare.com/sandbox/configuration/dockerfile/) and [custom-domain setup](https://developers.cloudflare.com/sandbox/guides/preview-urls-custom-domain/) |
| Bucket mount fails | [Mount buckets](https://developers.cloudflare.com/sandbox/guides/mount-buckets/), including local-development limitations |
| Untrusted input, tenant isolation, credentials, or preview access | [Security model](https://developers.cloudflare.com/sandbox/concepts/security/) and [Outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) |
| Capacity or cost planning | [Limits](https://developers.cloudflare.com/sandbox/platform/limits/) and [Pricing](https://developers.cloudflare.com/sandbox/platform/pricing/) |
| Deprecated stable APIs | [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/); use [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) only when moving to `@next`. |
