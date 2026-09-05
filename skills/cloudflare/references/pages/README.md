# Cloudflare Pages

Supported platform for existing Pages applications and Pages-specific workflows on Cloudflare's global network.

> **Starting a new project?** Use [Workers Static Assets](../static-assets/) for static sites, SPAs, SSG, SSR, and full-stack applications. Workers is Cloudflare's primary application platform; Pages continues to work, but new features and optimizations are focused on Workers.

## Key Features

- **Git-based deploys**: Auto-deploy from GitHub/GitLab
- **Preview deployments**: Unique URL per branch/PR
- **Pages Functions**: File-based serverless routing (Workers runtime)
- **Static + dynamic**: Smart asset caching + edge compute
- **Smart Placement**: Automatic function optimization based on traffic patterns
- **Framework optimized**: SvelteKit, Astro, Nuxt, Qwik, Solid Start

## Deployment Methods

### 1. Git Integration (Production)
Dashboard → Workers & Pages → Create → Connect to Git → Configure build

### 2. Direct Upload
```bash
npx wrangler pages deploy ./dist --project-name=my-project
npx wrangler pages deploy ./dist --project-name=my-project --branch=staging
```

### 3. C3 CLI
```bash
npm create cloudflare@latest -- --platform=pages
# Use only when intentionally creating a Pages project
```

## Pages vs Workers

- **Default for new applications**: Workers with Static Assets, including static-only sites, SPAs, SSG, SSR, APIs, and full-stack frameworks
- **Workers developer workflow**: Workers Builds supports GitHub/GitLab builds, deploy hooks, build caching, and preview URLs
- **Choose Pages when required**: Existing Pages projects, custom branch aliases, richer branch deploy controls, native Pages Functions file-based routing/plugins, independently configured production and preview bindings, or a custom domain outside a Cloudflare-managed zone
- **Broader Workers capabilities**: Gradual deployments, remote development, richer observability, Cron Triggers, direct Durable Objects, queue consumers, and additional bindings
- **Interoperability**: Pages Functions use the Workers runtime and can bind to a separate Worker

See the live [Pages-to-Workers compatibility matrix](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/#compatibility-matrix) before choosing between them.

## Quick Start

```bash
# Create
npm create cloudflare@latest -- --platform=pages

# Local dev
npx wrangler pages dev ./dist

# Deploy
npx wrangler pages deploy ./dist --project-name=my-project

# Types
npx wrangler types --path='./functions/types.d.ts'

# Secrets
echo "value" | npx wrangler pages secret put KEY --project-name=my-project

# Logs
npx wrangler pages deployment tail --project-name=my-project
```

## Resources

- [Pages Docs](https://developers.cloudflare.com/pages/)
- [Functions API](https://developers.cloudflare.com/pages/functions/api-reference/)
- [Framework Guides](https://developers.cloudflare.com/pages/framework-guides/)
- [Discord #functions](https://discord.com/channels/595317990191398933/910978223968518144)

## Reading Order

**Maintaining an existing Pages project?** Start here:
1. README.md (you are here) - Overview & quick start
2. [configuration.md](./configuration.md) - Project setup, wrangler.jsonc, bindings
3. [api.md](./api.md) - Functions API, routing, context
4. [patterns.md](./patterns.md) - Common implementations
5. [gotchas.md](./gotchas.md) - Troubleshooting & pitfalls

**Quick reference?** Jump to relevant file above.

## In This Reference

- [configuration.md](./configuration.md) - wrangler.jsonc, build, env vars, Smart Placement
- [api.md](./api.md) - Functions API, bindings, context, advanced mode
- [patterns.md](./patterns.md) - Full-stack patterns, framework integration
- [gotchas.md](./gotchas.md) - Build issues, limits, debugging, framework warnings

## See Also

- [pages-functions](../pages-functions/) - File-based routing, middleware
- [d1](../d1/) - SQL database for Pages Functions
- [kv](../kv/) - Key-value storage for caching/state
