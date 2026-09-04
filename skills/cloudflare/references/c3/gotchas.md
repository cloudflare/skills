# C3 Troubleshooting

## Deployment Issues

### Placeholder IDs

**Error:** "Invalid namespace ID"  
**Fix:** Replace placeholders in wrangler.jsonc with real IDs:
```bash
npx wrangler kv namespace create MY_KV  # Get real ID
```

### Authentication

**Error:** "Not authenticated"  
**Fix:** `npx wrangler login` or set `CLOUDFLARE_API_TOKEN`

### Name Conflict

**Error:** "Worker already exists"  
**Fix:** Change `name` in wrangler.jsonc

## Platform Selection

| Need | Platform |
|------|----------|
| New static, SPA, SSG, framework, or full-stack app | Workers (default) |
| Git integration and preview URLs | Workers Builds (default); Pages also supports these |
| Direct Durable Objects, Cron Triggers, queue consumers, richer observability | Workers (default) |
| D1 or queue producer | Workers or Pages |
| Existing Pages app or required Pages-only workflow | `--platform=pages` |

Pages has richer branch deploy controls, custom branch aliases, native Pages Functions routing/plugins, separate preview bindings, and support for external-zone custom domains. If none is required, prefer Workers for new projects. For an existing Pages project, use the [Pages-to-Workers migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) instead of blindly recreating it.

## TypeScript Issues

**"Cannot find name 'KVNamespace'"**
```bash
npm run cf-typegen  # Regenerate types
# Restart TS server in editor
```

**Missing types after config change:** Re-run `npm run cf-typegen`

## Package Manager

**Multiple lockfiles causing issues:**
```bash
rm pnpm-lock.yaml  # If using npm
rm package-lock.json  # If using pnpm
```

## CI/CD

**CI hangs on prompts:**
```bash
npm create cloudflare@latest -- my-app \
  --type=hello-world --lang=ts --no-git --no-deploy
```

**Auth in CI:**
```yaml
env:
  CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
  CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

## Framework-Specific

| Framework | Issue | Fix |
|-----------|-------|-----|
| Next.js | create-next-app failed | `npm cache clean --force`, retry |
| Astro | Adapter missing | Install `@astrojs/cloudflare` |
| Remix | Module errors | Update `@remix-run/cloudflare*` |

## Compatibility Date

**"Feature X requires compatibility_date >= ..."**  
**Fix:** Update `compatibility_date` in wrangler.jsonc to today's date

## Node.js Version

**"Node.js version not supported"**  
**Fix:** Install Node.js 18+ (`nvm install 20`)

## Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| Invalid namespace ID | Placeholder binding | Create resource, update config |
| Not authenticated | No login | `npx wrangler login` |
| Cannot find KVNamespace | Missing types | `npm run cf-typegen` |
| Worker already exists | Name conflict | Change `name` |
| CI hangs | Missing flags | Add --type, --lang, --no-deploy |
| Template not found | Bad name | Check cloudflare/templates |
