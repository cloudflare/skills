# Cloudflare Pages Functions

Serverless functions for existing Cloudflare Pages projects using the Workers runtime and file-based routing.

> **Starting a new application?** Use a Worker with Static Assets. Workers is Cloudflare's primary application platform and supports static, SPA, SSG, SSR, API, and full-stack workloads. Use this reference to maintain or migrate an existing Pages Functions project.

## Quick Navigation

**Need to...**
| Task | Go to |
|------|-------|
| Set up TypeScript types | [configuration.md](./configuration.md) - TypeScript Setup |
| Configure bindings (KV, D1, R2) | [configuration.md](./configuration.md) - wrangler.jsonc |
| Access request/env/params | [api.md](./api.md) - EventContext |
| Add middleware or auth | [patterns.md](./patterns.md) - Middleware, Auth |
| Background tasks (waitUntil) | [patterns.md](./patterns.md) - Background Tasks |
| Debug errors or check limits | [gotchas.md](./gotchas.md) - Common Errors, Limits |

## Decision Tree: Is This Pages Functions?

```
Need serverless backend? 
├─ New static/full-stack app or standalone API → Workers + Static Assets
├─ Existing Pages project → Pages Functions
└─ Existing Pages static site with no backend → Pages (no functions)

Have existing Worker?
└─ Keep it on Workers; do not migrate to Pages solely for file routing

Have existing Pages Functions?
├─ Keep Pages → Use /functions or _worker.js (Advanced Mode)
└─ Migrate to Workers → Use a Workers-native framework/router or compile /functions

Framework-based?
├─ New framework app → Use the framework's Workers guide
├─ Existing full-stack Next.js → Migrate to vinext on Workers
├─ Existing Remix → Migrate to React Router on Workers
└─ Existing Pages adapter → Follow its output/routing conventions
```

## File-Based Routing

```
/functions
  ├── index.js              → /
  ├── api.js                → /api
  ├── users/
  │   ├── index.js          → /users/
  │   ├── [user].js         → /users/:user
  │   └── [[catchall]].js   → /users/*
  └── _middleware.js        → runs on all routes
```

**Rules:**
- `index.js` → directory root
- Trailing slash optional
- Specific routes precede catch-alls
- Falls back to static if no match

## Dynamic Routes

**Single segment** `[param]` → string:
```js
// /functions/users/[user].js
export function onRequest(context) {
  return new Response(`Hello ${context.params.user}`);
}
// Matches: /users/nevi
```

**Multi-segment** `[[param]]` → array:
```js
// /functions/users/[[catchall]].js
export function onRequest(context) {
  return new Response(JSON.stringify(context.params.catchall));
}
// Matches: /users/nevi/foobar → ["nevi", "foobar"]
```

## Key Features

- **Method handlers:** `onRequestGet`, `onRequestPost`, etc.
- **Middleware:** `_middleware.js` for cross-cutting concerns
- **Bindings:** KV, D1, R2, Workers AI, and Service bindings. Durable Objects require a binding to a separate Worker; define them directly when migrating to Workers.
- **TypeScript:** Full type support via `wrangler types` command
- **Advanced mode:** Use `_worker.js` for custom routing logic

## Reading Order

**New to Pages Functions?** Start here:
1. [README.md](./README.md) - Overview, routing, decision tree (you are here)
2. [configuration.md](./configuration.md) - TypeScript setup, wrangler.jsonc, bindings
3. [api.md](./api.md) - EventContext, handlers, bindings reference
4. [patterns.md](./patterns.md) - Middleware, auth, CORS, rate limiting, caching
5. [gotchas.md](./gotchas.md) - Common errors, debugging, limits

**Quick reference lookup:**
- Bindings table → [api.md](./api.md)
- Error diagnosis → [gotchas.md](./gotchas.md)
- TypeScript setup → [configuration.md](./configuration.md)

## See Also
- [pages](../pages/) - Pages platform overview and static site deployment
- [workers](../workers/) - Workers runtime API reference
- [d1](../d1/) - D1 database integration with Pages Functions
