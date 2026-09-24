---
name: frameworks-on-cloudflare
description: Build, migrate, and deploy web-framework applications on Cloudflare Workers. Use when a framework project such as Next.js, Astro, SvelteKit, React Router, or Nuxt targets Cloudflare, or when a framework repository contains Workers deployment configuration. Use the framework's native tooling and official Workers integration.
---

# Build with frameworks on Cloudflare

Use the framework as the primary development interface and Cloudflare Workers as the deployment target. **Do not route framework setup through C3.** Use the framework's native setup or migration tooling and its official Workers integration.

Serve static sites and SPA output with [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/). Do not select Pages templates, Pages deployment commands, or Pages-specific presets for new applications. Preserve existing Pages deployments during unrelated maintenance.

## Route the project

1. Inspect the repository before changing it. Identify the framework, installed version, package manager, rendering mode, existing adapter, and current deployment target.
2. Preserve the user's framework choice. Determine whether the task starts a new project, adapts an existing project, or changes only application code.
3. Read only the matching row below. Load applicable upstream skills or agent documentation and the current Workers framework guide.
4. For an existing supported app without Wrangler configuration, read [Deploy an existing project](https://developers.cloudflare.com/workers/framework-guides/automatic-configuration/) and prefer `wrangler setup` before manually installing adapters or writing configuration. Use `wrangler setup --dry-run` to preview, verify support against the installed Wrangler version, then inspect the generated changes and run the build.
5. For a new project, use the setup tool recommended by the framework's Workers guide. For an existing project that is not supported by automatic configuration, use the guide's manual or migration path.
6. Keep Workers as the deployment target while following upstream framework guidance. Add or change only the adapter, runtime, build, and deployment configuration the selected integration requires.
7. Inspect generated package scripts, run the framework's checks and build, then verify the Worker locally before deployment.

| Framework | Workers setup | Official upstream agent guidance |
| --- | --- | --- |
| Next.js | Use vinext rather than OpenNext for new projects. Follow the [Next.js Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/) and load `nextjs-on-cloudflare` when available. | [vinext skills](https://github.com/cloudflare/vinext/tree/main/.agents/skills); the migration skill requires an existing Next.js app. Use [vinext's new-project setup](https://github.com/cloudflare/vinext#starting-a-new-vinext-project) for a new app. |
| TanStack Start | Use the [Cloudflare Vite plugin setup](https://developers.cloudflare.com/workers/framework-guides/web-apps/tanstack-start/). Distinguish Start from standalone TanStack Router. | Use [TanStack Intent](https://tanstack.com/intent/latest/docs/getting-started/quick-start-consumers) to discover and load installed package skills, including [Start's deployment guidance](https://github.com/TanStack/router/blob/main/packages/start-client-core/skills/start-core/deployment/SKILL.md). |
| React Router | Identify Framework, Data, or Declarative mode. Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/react-router/) for full-stack setup; check its rendering limitations before choosing SPA or prerendering. | Load the official [React Router skill](https://github.com/remix-run/react-router/blob/main/.agents/skills/react-router/SKILL.md), its matching mode reference, and installed package docs when available. |
| SvelteKit | Use the [Workers setup](https://developers.cloudflare.com/workers/framework-guides/web-apps/sveltekit/) with `@sveltejs/adapter-cloudflare`. | Use [Svelte's official skills](https://svelte.dev/docs/ai/skills) and [AI setup guidance](https://svelte.dev/docs/ai/instructions). |
| Hono | Choose an API-only Worker or a frontend plus API. The [Cloudflare guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/hono/) covers Hono with a React SPA; use [Hono's Workers guide](https://hono.dev/docs/getting-started/cloudflare-workers) for an API-only app. | Load the application skill from [honojs/skills](https://github.com/honojs/skills). |
| Astro | Distinguish static output from on-demand rendering: static sites need no Cloudflare adapter; server rendering uses it. Follow the [Workers guide](https://developers.cloudflare.com/workers/framework-guides/web-apps/astro/). | Use Astro's [official AI guidance and docs MCP](https://docs.astro.build/en/guides/build-with-ai/). |
| Nuxt | Follow the [Workers setup](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/nuxt/) for the current Nitro integration and bindings. | Use the [Nuxt docs MCP](https://nuxt.com/docs/4.x/guide/ai/mcp); load the [Nuxt UI skill](https://ui.nuxt.com/getting-started/ai/mcp) only when using Nuxt UI. |
| React or Vue SPA | Follow the [React + Vite](https://developers.cloudflare.com/workers/framework-guides/web-apps/react/) or [Vue](https://developers.cloudflare.com/workers/framework-guides/web-apps/vue/) Workers guide. Distinguish a client-only SPA from a full-stack framework. | Use the chosen framework's official guidance for application development. |
