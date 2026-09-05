# Cloudflare Static Assets Skill Reference

Expert guidance for deploying and configuring static assets with Cloudflare Workers. This skill covers configuration patterns, routing architectures, asset binding usage, and best practices for SPAs, SSG sites, and full-stack applications.

## Quick Start

```jsonc
// wrangler.jsonc
{
  "name": "my-app",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "assets": {
    "directory": "./dist"
  }
}
```

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return env.ASSETS.fetch(request);
  }
};
```

Deploy: `wrangler deploy`

## When to Use Workers Static Assets

Workers Static Assets is the recommended path for new static sites, SPAs, SSG
sites, and full-stack applications. A purely static site only needs an
`assets.directory`; no Worker script is required. Add a Worker entry point when
the application needs APIs, bindings, or custom routing.

**Decision tree:**

- Pure static site or SSG? → Workers Static Assets
- SPA or framework application? → Workers Static Assets
- API routes or custom routing? → Workers Static Assets with a Worker entry point
- Existing Pages project? → Keep it on Pages or migrate to Workers

## Reading Order

1. **configuration.md** - Setup, wrangler.jsonc options, routing patterns
2. **api.md** - ASSETS binding API, request/response handling
3. **patterns.md** - Common patterns (SPA, API routes, auth, A/B testing)
4. **gotchas.md** - Limits, errors, performance tips

## In This Reference

- **[configuration.md](configuration.md)** - Setup, deployment, configuration
- **[api.md](api.md)** - API endpoints, methods, interfaces
- **[patterns.md](patterns.md)** - Common patterns, use cases, examples
- **[gotchas.md](gotchas.md)** - Troubleshooting, best practices, limitations

## See Also

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Static Assets Docs](https://developers.cloudflare.com/workers/static-assets/)
- [Migrate from Pages](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)
- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
