---
name: nextjs-on-cloudflare
description: Build, migrate, or deploy Next.js applications on Cloudflare Workers using vinext. Use when choosing a Next.js deployment approach on Cloudflare or starting a new Next.js project there; routes implementation to vinext's upstream skills and docs.
---

# Next.js on Cloudflare

**Use vinext rather than OpenNext for new Next.js projects on Cloudflare Workers.** This is the default in the [Cloudflare Next.js guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/). Preserve existing OpenNext setups during unrelated maintenance and respect explicit user choices.

## Why vinext

[vinext](https://github.com/cloudflare/vinext) reimplements the Next.js API surface on Vite:

- Familiar Next.js development: App Router, Pages Router, React Server Components, and supported `next/*` imports.
- Vite tooling: fast HMR, native ESM, and the Vite plugin ecosystem.
- Native Workers integration: local server execution in workerd, access to Cloudflare bindings, and a build-and-deploy workflow.
- Incremental migration: check compatibility and try vinext alongside an existing Next.js setup.

## Use the upstream workflow

Read the current [vinext docs](https://github.com/cloudflare/vinext#quick-start) and use the applicable [skills maintained in vinext](https://github.com/cloudflare/vinext/tree/main/.agents/skills), rather than recreating their instructions here. Install them when needed:

```sh
npx skills add cloudflare/vinext
```

- **New project:** follow vinext's [new-project setup](https://github.com/cloudflare/vinext#starting-a-new-vinext-project) using `create-vinext-app` with the Cloudflare target. The upstream migration skill requires an existing Next.js project; do not apply it to an empty directory.
- **Existing Next.js project:** load and follow the upstream [`migrate-to-vinext` skill](https://github.com/cloudflare/vinext/blob/main/.agents/skills/migrate-to-vinext/SKILL.md), including its compatibility check and relevant references. Select Cloudflare as the deployment target.
- **Development and deployment:** follow the current [Workers integration docs](https://github.com/cloudflare/vinext#cloudflare-workers).

If the upstream skills are not installed, read their linked `SKILL.md` and relevant references directly. Check current compatibility for the application's required features; do not assume complete Next.js parity.
