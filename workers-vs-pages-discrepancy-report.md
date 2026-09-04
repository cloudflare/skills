# Workers versus Pages skill audit

Audit date: 4 September 2026

Remediation status: completed on 4 September 2026. “How it is described” records the pre-remediation wording; the linked skill files now contain the corrected guidance.

## Executive summary

The repository's guidance is materially behind Cloudflare's current product positioning. The recurring old model is:

- Pages for static sites, frameworks, Git deployments, and branch previews.
- Workers for APIs, advanced routing, and Workers-only features.

The live documentation now says:

- **Use Workers Static Assets for new static sites, SPAs, and full-stack applications.** Workers is Cloudflare's primary application platform; Pages remains supported, but new features and optimizations are focused on Workers.
- Workers now has GitHub/GitLab integration through Workers Builds and supports per-commit and stable per-branch preview URLs.
- Pages still has a few advantages: richer branch deploy controls, custom branch aliases, native Pages Functions file-based routing and plugins, separate production/preview bindings, and custom domains outside Cloudflare-managed zones.
- Workers has the broader feature set, including the Vite plugin, gradual deployments, remote development, richer observability, Cron Triggers, direct Durable Object support, queue consumers, and more bindings.

I screened all 35 Markdown files containing both the exact words `Workers` and `Pages`, plus `skills/cloudflare/references/c3/patterns.md` and `skills/cloudflare/references/pages/patterns.md`, which contain actual platform choices despite not matching that exact-word intersection. Seventeen files contain material discrepancies. The other 20 files contain incidental mentions, valid Pages commands, dashboard labels, integration examples, or generic uses of “pages”; they do not make a Workers-versus-Pages claim.

## Canonical wording the skills should use

> For new projects, use Cloudflare Workers with Static Assets for static sites, SPAs, SSG, and full-stack applications. Workers Builds provides Git integration and preview deployments. Continue using Pages for existing Pages projects or when a Pages-only capability is required, such as custom branch aliases, richer branch deploy controls, native Pages Functions file-based routing/plugins, independently configured preview bindings, or a custom domain outside a Cloudflare-managed zone.

## Discrepancies

### 1. Top-level product routing sends full-stack Git projects to Pages

Affected file:

- [`skills/cloudflare/SKILL.md:48`](skills/cloudflare/SKILL.md#L48)

How it is described:

> Full-stack web app with Git deploys → pages/

How it should be described:

> New static, SPA, SSG, or full-stack application → Workers with Static Assets. For Git-based CI/CD, use Workers Builds and preview URLs. Route to Pages only for an existing Pages project or a specifically identified Pages-only capability.

Why: Workers is now the primary platform, and Git deployments no longer distinguish Pages from Workers.

### 2. The Pages overview preserves a false Pages/frontend versus Workers/backend split

Affected file:

- [`skills/cloudflare/references/pages/README.md:3`](skills/cloudflare/references/pages/README.md#L3)
- [`skills/cloudflare/references/pages/README.md:31`](skills/cloudflare/references/pages/README.md#L31)

How it is described:

- Pages is the JAMstack/full-stack/framework/Git platform.
- Workers is for “pure APIs, complex routing, WebSockets, scheduled tasks, email handlers.”

How it should be described:

- Pages is a supported platform primarily relevant to existing Pages projects and its remaining unique workflow features.
- Workers supports static-only, SPA, SSG, full-stack, SSR, and API workloads; it is not merely the backend/API choice.
- Add a prominent “start new projects with Workers” warning and summarize the remaining Pages-only gaps from the compatibility matrix.

### 3. The Static Assets decision table recommends Pages for the workloads now recommended for Workers

Affected file:

- [`skills/cloudflare/references/static-assets/README.md:30`](skills/cloudflare/references/static-assets/README.md#L30)

How it is described:

- Pure static site or SSG → Pages.
- Framework (Next, Nuxt, Remix) → Pages.
- Workers Static Assets is mainly for hybrid apps and custom routing.
- Git-based configuration and preview workflows are presented as Pages differentiators.

How it should be described:

- Static sites, SSG, SPAs, frameworks, and hybrid/full-stack apps should default to Workers Static Assets for new projects.
- Workers supports assets-only deployments without a Worker script, so “pure static” is not a reason to choose Pages.
- Workers Builds supplies Git integration, build caching, deploy hooks, and preview URLs.
- Pages should be the exception when its remaining workflow/domain features are required.

### 4. C3 product-selection guidance sends new static and full-stack apps to Pages

Affected files:

- [`skills/cloudflare/references/c3/README.md:14`](skills/cloudflare/references/c3/README.md#L14)
- [`skills/cloudflare/references/c3/README.md:18`](skills/cloudflare/references/c3/README.md#L18)
- [`skills/cloudflare/references/c3/gotchas.md:23`](skills/cloudflare/references/c3/gotchas.md#L23)
- [`skills/cloudflare/references/c3/api.md:57`](skills/cloudflare/references/c3/api.md#L57)
- [`skills/cloudflare/references/c3/patterns.md:10`](skills/cloudflare/references/c3/patterns.md#L10)

How it is described:

- Static/SSG/documentation → Pages.
- Full-stack without a Workers-only feature → Pages for Git integration and branch previews.
- Next.js and Astro examples explicitly target Pages.

How it should be described:

- C3's default Workers target is the correct default for new static, framework, and full-stack projects.
- `--platform=pages` remains the correct syntax only when deliberately creating a Pages project; it should not be presented as the normal framework/static path.
- Git integration and branch preview URLs are available on Workers.
- Next.js full-stack guidance should target vinext on Workers; static Next.js exports can still run on Pages, but Workers is the default for a new deployment.
- Astro, Nuxt, SvelteKit, React Router, and other supported frameworks should use their Workers guides/adapters for new projects.

Related CLI drift: the references rely on old `--type=web-app` and `--ts` patterns. The live Pages C3 reference uses `--framework` (which ignores `--type`) and marks `--ts` deprecated in favor of `--lang=ts`.

### 5. C3's feature table overstates what requires Workers and understates Pages/Workers parity

Affected file:

- [`skills/cloudflare/references/c3/gotchas.md:25`](skills/cloudflare/references/c3/gotchas.md#L25)

How it is described:

> Durable Objects, D1, Queues → Workers

How it should be described:

- D1 is supported on both Workers and Pages.
- Queue producers are supported on both; queue consumers require Workers.
- Durable Objects are directly supported and recommended on Workers. Pages can use a Durable Object only through a binding to a separate Worker, configured for production and preview.
- Git integration and preview URLs are supported by both. Pages retains richer branch controls and custom branch aliases; Workers requires enabling non-production branch builds for the comparable branch-preview workflow.

### 6. Pages Functions guidance recommends moving Workers in the wrong direction

Affected files:

- [`skills/cloudflare/references/pages-functions/README.md:17`](skills/cloudflare/references/pages-functions/README.md#L17)
- [`skills/cloudflare/references/pages-functions/gotchas.md:76`](skills/cloudflare/references/pages-functions/gotchas.md#L76)

How it is described:

- A static site needing backend code → Pages Functions.
- An existing Worker with simple routes → migrate to `/functions`.
- A dedicated “Workers → Pages Functions” migration recipe is provided.

How it should be described:

- For a new static site with backend code, use a Worker plus Static Assets.
- Do not migrate an existing Worker to Pages Functions merely to obtain file routing.
- Frame Pages Functions as maintenance guidance for existing Pages projects.
- Make Pages → Workers the primary migration direction. A `functions/` folder can be compiled with `wrangler pages functions build`, though a Workers-native framework/router is preferred for new work.

The key-features list should also qualify Durable Objects: Pages Functions can reach them only through a binding to a separate Worker; Workers can define them directly.

### 7. Framework status and migration advice is stale and sometimes directly wrong

Affected files:

- [`skills/cloudflare/references/pages/api.md:190`](skills/cloudflare/references/pages/api.md#L190)
- [`skills/cloudflare/references/pages/patterns.md:188`](skills/cloudflare/references/pages/patterns.md#L188)
- [`skills/cloudflare/references/pages/gotchas.md:59`](skills/cloudflare/references/pages/gotchas.md#L59)

How it is described:

- Next.js on Workers is a “custom adapter” that is complex and unsupported; Vercel is recommended.
- Remix users should migrate to SvelteKit/Astro or keep an unsupported Pages adapter.
- SvelteKit, Astro, Nuxt, Qwik, and Solid Start are presented as the supported Pages destination set.

How it should be described:

- Full-stack Next.js: Cloudflare currently recommends vinext on Workers. Pages remains documented for static Next.js exports.
- Remix: the framework itself is no longer recommended for new projects by its authors. Migrate existing Remix applications to React Router and use Cloudflare's React Router Workers guide.
- Workers has production framework paths for React Router, Astro, Nuxt, SvelteKit, and more. Existing Pages adapters may continue to work, but they should not be presented as the recommended Cloudflare target for new applications.

### 8. Pages remote-development instructions document an unsupported mode

Affected files:

- [`skills/cloudflare/references/pages/configuration.md:140`](skills/cloudflare/references/pages/configuration.md#L140)
- [`skills/cloudflare/references/pages/gotchas.md:140`](skills/cloudflare/references/pages/gotchas.md#L140)

How it is described:

- `wrangler pages dev --remote` is shown as a valid development mode.
- Failure is treated as an authentication problem with suggested retries.

How it should be described:

- The current compatibility matrix marks remote development as supported for Workers and unsupported for Pages.
- For Pages, use local `wrangler pages dev`. For remote development, migrate to/use Workers and `wrangler dev --remote`.
- Do not diagnose Pages remote mode as merely an authentication issue.

### 9. Smart Placement guidance confuses Pages with Workers Static Assets and asserts unsupported performance numbers

Affected files:

- [`skills/cloudflare/references/smart-placement/README.md:24`](skills/cloudflare/references/smart-placement/README.md#L24)
- [`skills/cloudflare/references/smart-placement/configuration.md:152`](skills/cloudflare/references/smart-placement/configuration.md#L152)
- [`skills/cloudflare/references/smart-placement/gotchas.md:43`](skills/cloudflare/references/smart-placement/gotchas.md#L43)
- [`skills/cloudflare/references/smart-placement/api.md:113`](skills/cloudflare/references/smart-placement/api.md#L113)

How it is described:

- `assets.run_worker_first` is discussed as a Pages/Assets Workers or “Pages project” setting.
- Smart Placement is said to route all static assets away from the edge and cause a specific 2–5× slowdown.
- The prescribed response is to disable Smart Placement or always split Workers.

How it should be described:

- `assets.run_worker_first` is a Workers Static Assets setting, not a Pages project setting. Pages and Workers both support Smart Placement, but this particular interaction belongs to Workers Static Assets.
- Use the live docs' narrower caution: because the entire Worker script is placed as one unit, combining Smart Placement with `run_worker_first` may produce placement decisions that do not reflect the desired edge-first versus placed-compute split.
- Remove the unsupported 2–5× number and the claim that degradation is guaranteed.
- Recommend measuring the workload and, where necessary, using asset-first/selective routing or separating placed backend compute. Do not state that Smart Placement must always be disabled.

## Remaining Pages advantages that revised guidance must preserve

The update should not collapse the products into “Workers has everything.” The live compatibility matrix identifies these meaningful Pages advantages or Workers gaps:

- Custom branch aliases: Pages supported; Workers marked coming soon.
- Branch deploy controls: Pages has richer native controls; Workers has a workaround through non-production branch builds.
- Native Pages Functions file-based routing and Pages Plugins: Workers requires a framework/router, direct Worker code, or compilation of an existing `functions/` folder.
- Separate production and preview bindings: Pages supports them natively; Workers currently needs environments/build configuration.
- Custom domains outside Cloudflare-managed zones: Pages supports them; Workers does not.
- Early Hints is native on Pages; Workers requires the zone setting and appropriate `Link` headers.

Conversely, Workers-only or materially stronger areas include the Cloudflare Vite plugin, gradual deployments, remote development, the dashboard editor, richer observability, direct Durable Objects, Cron Triggers, Email Workers, Image Resizing, queue consumers, Rate Limiting bindings, and non-root routes.

## Mentions reviewed with no Workers-versus-Pages discrepancy

These files either make no platform-choice claim or describe a valid existing-Pages operation:

- `README.md`
- `skills/cloudflare/references/browser-rendering/gotchas.md` (generic browser “pages,” not Cloudflare Pages)
- `skills/cloudflare/references/cron-triggers/patterns.md`
- `skills/cloudflare/references/graphql-api/README.md`
- `skills/cloudflare/references/pages-functions/configuration.md`
- `skills/cloudflare/references/pulumi/README.md`
- `skills/cloudflare/references/pulumi/configuration.md`
- `skills/cloudflare/references/pulumi/gotchas.md`
- `skills/cloudflare/references/stream/README.md`
- `skills/cloudflare/references/stream/configuration.md`
- `skills/cloudflare/references/stream/patterns.md`
- `skills/cloudflare/references/terraform/README.md`
- `skills/cloudflare/references/terraform/configuration.md`
- `skills/cloudflare/references/terraform/patterns.md`
- `skills/cloudflare/references/turnstile/patterns.md`
- `skills/cloudflare/references/web-analytics/README.md` (generic web pages)
- `skills/cloudflare/references/workers-ai/README.md`
- `skills/cloudflare/references/wrangler/README.md`
- `skills/wrangler/SKILL.md`
- `skills/turnstile-spin/SKILL.md` — its Pages Plugin advice is valid for an existing Pages project; a future edit could add that new applications should generally use a Worker and direct Siteverify validation.

## Live documentation used

Primary sources, all read from the live Cloudflare documentation site on the audit date:

1. [Workers Best Practices — “Use Workers Static Assets for new projects”](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
2. [Cloudflare Pages](https://developers.cloudflare.com/pages/)
3. [Migrate from Pages to Workers and compatibility matrix](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)
4. [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)
5. [Workers preview URLs](https://developers.cloudflare.com/workers/versions-and-deployments/preview-urls/)
6. [Pages C3 CLI](https://developers.cloudflare.com/pages/get-started/c3/)
7. [Next.js on Workers](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/)
8. [Next.js on Pages](https://developers.cloudflare.com/pages/framework-guides/nextjs/)
9. [React Router on Workers](https://developers.cloudflare.com/workers/framework-guides/web-apps/react-router/)
10. [Remix on Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-a-remix-site/)
11. [Workers Static Assets: Worker script and `run_worker_first`](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/)
12. [Turnstile Pages Plugin](https://developers.cloudflare.com/pages/functions/plugins/turnstile/)

## Remediation applied

1. Updated `skills/cloudflare/SKILL.md`, `pages/README.md`, and `static-assets/README.md` so Workers controls initial product selection for new applications.
2. Rewrote C3 and framework guidance so Workers is the default for new applications.
3. Reversed Pages Functions migration guidance to Pages → Workers.
4. Corrected remote-development and Smart Placement statements.
5. Added the remaining Pages exceptions explicitly so the guidance stays precise.
