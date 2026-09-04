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

## When to Use Workers Static Assets vs Pages

| Factor | Workers Static Assets | Cloudflare Pages |
|--------|----------------------|------------------|
| **Use case** | Recommended for new static, SPA, SSG, SSR, and full-stack apps | Existing Pages apps and Pages-only workflows |
| **Worker control** | Assets-only or full Worker control, including asset-first and selective Worker-first routing | Native Pages Functions and file-based routing |
| **CI/CD** | Workers Builds with Git integration, caching, deploy hooks, and preview URLs | Git integration plus richer branch controls and custom branch aliases |
| **Frameworks** | Primary target for current Cloudflare framework adapters | Maintain existing Pages adapters; static framework output remains supported |
| **Distinct capabilities** | Broader runtime, observability, bindings, and deployment features | External-zone custom domains, native Pages Plugins, and separate preview bindings |

**Decision tree:**

- New static site, SSG, SPA, or full-stack app? → Workers Static Assets
- API routes or custom routing? → Workers Static Assets
- Framework app? → Follow the framework's Workers guide; for full-stack Next.js use vinext, and for Remix migrate to React Router on Workers
- Existing Pages project? → Keep Pages if it is working, or follow the Pages-to-Workers migration guide
- Need a Pages-only workflow from the compatibility matrix? → Pages

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
- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
