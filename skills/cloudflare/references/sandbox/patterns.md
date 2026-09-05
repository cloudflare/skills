# Sandbox workflow documentation

[Choose the package line](./README.md#choose-the-package-line-first), then fetch the guide for the workflow. Main-docs tutorials use stable APIs; apply the preview-specific pages when building on `@next`.

| Workflow | Documentation |
| --- | --- |
| AI code execution and rich results | [Stable code interpreter](https://developers.cloudflare.com/sandbox/guides/code-execution/) or [preview interpreter](https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/) |
| Development servers and readiness | [Stable background processes](https://developers.cloudflare.com/sandbox/guides/background-processes/) or [preview process execution](https://developers.cloudflare.com/sandbox/1-0-preview/processes/), then [Expose services](https://developers.cloudflare.com/sandbox/guides/expose-services/) |
| Real-time services | [WebSocket connections](https://developers.cloudflare.com/sandbox/guides/websocket-connections/) |
| Persistent data | [Mount buckets](https://developers.cloudflare.com/sandbox/guides/mount-buckets/) and [Backup and restore](https://developers.cloudflare.com/sandbox/guides/backup-restore/) |
| Clone, build, and test repositories | [Automated testing pipeline](https://developers.cloudflare.com/sandbox/tutorials/automated-testing-pipeline/); preview apps use [process execution](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) and the [migration guide](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) for changed command and Git APIs. |
| Tenant isolation and sandbox IDs | [Security model](https://developers.cloudflare.com/sandbox/concepts/security/) and [Architecture](https://developers.cloudflare.com/sandbox/concepts/architecture/). Stable [sessions](https://developers.cloudflare.com/sandbox/concepts/sessions/) share a sandbox and are not a security boundary. |
