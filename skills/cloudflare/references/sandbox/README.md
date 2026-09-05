# Cloudflare Sandbox SDK

Use Sandbox for isolated Linux code execution, AI code interpreters, development environments, and testing pipelines. Read the [architecture](https://developers.cloudflare.com/sandbox/concepts/architecture/) to understand how Workers, Durable Objects, and Containers fit together.

## Choose the package line first

Inspect the app's dependency, lockfile, and container image before implementing. Follow the [1.0 preview guidance](https://developers.cloudflare.com/sandbox/1-0-preview/):

| Task | Skill and documentation |
| --- | --- |
| New project or existing `@cloudflare/sandbox@next` app | Load **sandbox-next**; use [preview get started](https://developers.cloudflare.com/sandbox/1-0-preview/get-started/). |
| Maintain an existing stable app | Load **sandbox-stable**; use [stable get started](https://developers.cloudflare.com/sandbox/get-started/). |
| Move an existing stable app to `@next` | Load **sandbox-migrate-to-next**; follow [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/). Do not force migration as part of routine stable maintenance. |
| Clean up deprecated APIs while staying on stable | Use the [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/). |

Load these skills by name when installed; otherwise follow the linked documentation. Keep the Worker package and container image matched to the same release line; see [deployment](https://developers.cloudflare.com/sandbox/guides/deploy/). Do not mix stable and preview execution APIs. Self-deployed bridge work stays on stable; see [Bridge](https://developers.cloudflare.com/sandbox/bridge/).

## Find the task documentation

Fetch the relevant page before writing code; check signatures against the installed package's types.

- [Configuration](./configuration.md): setup, image, environment, deployment.
- [API](./api.md): commands, files, sessions, interpreter, networking, lifecycle.
- [Patterns](./patterns.md): code execution, services, storage, testing, tenancy.
- [Gotchas](./gotchas.md): recovery, persistence, security, limits.

Related infrastructure: [Durable Objects](../durable-objects/README.md), [Containers](../containers/README.md), [Workers](../workers/README.md).
