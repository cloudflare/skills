# C3 (create-cloudflare)

Official CLI for scaffolding Cloudflare Workers and, when explicitly requested, Pages projects with framework-aware setup and deployment.

## Quick Start

```bash
# Interactive (recommended for first-time)
npm create cloudflare@latest -- my-app

# Worker (recommended for new static, framework, full-stack, and API projects)
npm create cloudflare@latest -- my-api --type=hello-world --lang=ts

# Framework app on Workers
npm create cloudflare@latest -- my-site --framework=astro

# Existing/intentional Pages workflow
npm create cloudflare@latest -- --platform=pages
```

## Platform Decision Tree

```
What are you building?

├─ New static site / SPA / SSG / documentation
│   └─ Workers Static Assets (default)

├─ New full-stack or framework app
│   └─ Workers (default) - follow the framework's Workers guide
│       ├─ Next.js → vinext on Workers
│       └─ Remix → React Router on Workers

├─ API / WebSocket / Cron / Email handler
│   └─ Workers (default)

├─ Existing Pages project or confirmed Pages-only requirement
│   └─ Pages - explicitly add --platform=pages

└─ Clone an existing deployed Worker
    └─ npm create cloudflare@latest -- . --type=pre-existing --existing-script=my-worker
```

**Default to Workers for new projects.** Workers supports Git integration and branch preview URLs through Workers Builds. Use `--platform=pages` only when the customer deliberately needs Pages; omitting it correctly creates a Workers project.

## Interactive Flow

C3 prompts for the inputs required by the selected starter. Expect a project directory, a Worker starter or framework, framework-specific questions, Git initialization, and optional deployment. Prompts vary as C3 and third-party framework CLIs evolve, so do not depend on a fixed order.

Workers is the default target. C3 enters its Pages flow only when `--platform=pages` is explicitly supplied.

## Installation Methods

```bash
# NPM
npm create cloudflare@latest

# Yarn
yarn create cloudflare

# PNPM
pnpm create cloudflare@latest
```

## In This Reference

| File | Purpose | Use When |
|------|---------|----------|
| **api.md** | Complete CLI flag reference | Scripting, CI/CD, advanced usage |
| **configuration.md** | Generated files, bindings, types | Understanding output, customization |
| **patterns.md** | Workflows, CI/CD, monorepos | Real-world integration |
| **gotchas.md** | Troubleshooting failures | Deployment blocked, errors |

## Reading Order

| Task | Read |
|------|------|
| Create first project | README only |
| Set up CI/CD | README → api → patterns |
| Debug failed deploy | gotchas |
| Understand generated files | configuration |
| Full CLI reference | api |
| Create custom template | patterns → configuration |
| Convert existing project | README → patterns |

## Post-Creation

```bash
cd my-app

# Local dev with hot reload
npm run dev

# Generate TypeScript types for bindings
npm run cf-typegen

# Deploy to Cloudflare
npm run deploy
```

## See Also

- **workers/README.md** - Workers runtime, bindings, APIs
- **workers-ai/README.md** - AI/ML models
- **pages/README.md** - Pages-specific features
- **wrangler/README.md** - Wrangler CLI beyond initial setup
- **d1/README.md** - SQLite database
- **r2/README.md** - Object storage
