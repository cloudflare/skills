---
name: frameworks-on-cloudflare
description: Build, migrate, and deploy web-framework applications on Cloudflare Workers. Use when a framework project such as Astro, SvelteKit, React Router, TanStack Start, Nuxt, Hono, or a React or Vue SPA targets Cloudflare, or when a framework repository contains Workers deployment configuration.
---

# Build with frameworks on Cloudflare

Use the framework as the primary development interface and Cloudflare Workers as the deployment target. Serve static sites and SPA output with [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/index.md). Do not select Pages templates, Pages deployment commands, or Pages-specific presets for new applications. Preserve existing Pages deployments during unrelated maintenance.

## Route the project

1. Inspect the repository before changing it. Identify the framework, installed version, package manager, rendering mode, existing adapter, and Cloudflare configuration: `cloudflare.config.ts`, or `wrangler.jsonc`, `wrangler.json`, or `wrangler.toml`.
2. Preserve the user's framework choice. Determine whether the task starts a new project, adapts an existing project, or changes only application code.
3. Read only the matching row below, its Workers framework guide, and the framework's own agent guidance.
4. Set up the project for its state:
   - **New project:** follow the framework's Workers guide for project creation. The guides currently create the project with C3 and configure it for Wrangler; this is an exception to the `cloudflare` skill's default of `cf` for new projects, because the `cf` docs do not yet cover creating framework projects. After creation, the project has Wrangler configuration, so the next bullet applies.
   - **Existing project with Wrangler configuration:** keep Wrangler and load the `wrangler` skill. Follow the framework guide for adapter and configuration changes. Do not run `cf init .`, `cf dev`, `cf build`, or `cf deploy` in it.
   - **Existing project with no Cloudflare configuration:** use `cf`, which detects supported frameworks and configures them; see [Start from an existing project](https://developers.cloudflare.com/cf/get-started/first-worker/index.md#start-from-an-existing-project) and the `cf-cli` skill. Detection does not mean the project builds. If the build fails or the framework is not supported, follow the framework guide's manual setup.
5. Change only the adapter, runtime, build, and deployment configuration the integration requires. Inspect generated package scripts, run the framework's checks and build, then verify the Worker locally before deployment.

| Framework | Workers setup | Official upstream agent guidance |
| --- | --- | --- |
| Next.js | Load the `nextjs-on-cloudflare` skill. | Listed in that skill. |
| TanStack Start | Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/tanstack-start/index.md), which uses the Cloudflare Vite plugin. Distinguish Start from standalone TanStack Router. | Use [TanStack Intent](https://tanstack.com/intent/latest/docs/getting-started/quick-start-consumers) to discover and load installed package skills, including [Start's deployment guidance](https://github.com/TanStack/router/blob/main/packages/start-client-core/skills/start-core/deployment/SKILL.md). |
| React Router | Identify Framework, Data, or Declarative mode. Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/react-router/index.md) for full-stack setup. SPA mode is not supported with the Cloudflare Vite plugin, and prerendering has version requirements; check the guide before choosing either. | Load the official [React Router skill](https://github.com/remix-run/react-router/blob/main/.agents/skills/react-router/SKILL.md), its matching mode reference, and installed package docs when available. |
| SvelteKit | Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/sveltekit/index.md), which uses `@sveltejs/adapter-cloudflare`. | Use [Svelte's official skills](https://svelte.dev/docs/ai/skills) and [AI setup guidance](https://svelte.dev/docs/ai/instructions). |
| Hono | Choose an API-only Worker or a frontend plus API. The [Cloudflare guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/hono/index.md) covers Hono with a React SPA; use [Hono's Workers guide](https://hono.dev/docs/getting-started/cloudflare-workers) for an API-only app. | Load the application skill from [honojs/skills](https://github.com/honojs/skills). |
| Astro | Distinguish fully prerendered output from on-demand rendering: a static site deploys as static assets, and on-demand rendering uses `@astrojs/cloudflare`. Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/astro/index.md). | Use Astro's [official AI guidance and docs MCP](https://docs.astro.build/en/guides/build-with-ai/). |
| Nuxt | Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/nuxt/index.md) for the current Nitro integration and bindings. | Use the [Nuxt docs MCP](https://nuxt.com/docs/4.x/guide/ai/mcp); load the [Nuxt UI skill](https://ui.nuxt.com/getting-started/ai/mcp) only when using Nuxt UI. |
| React or Vue SPA | Follow the [React + Vite](https://developers.cloudflare.com/workers/framework-guides/web-apps/react/index.md) or [Vue](https://developers.cloudflare.com/workers/framework-guides/web-apps/vue/index.md) Workers guide. Distinguish a client-only SPA from a full-stack framework. | Use the chosen framework's official guidance for application development. |

For other frameworks, start from the [framework guides index](https://developers.cloudflare.com/workers/framework-guides/index.md).

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
