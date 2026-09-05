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

## Deployment Target

Use Workers for framework apps, static sites, and SPAs. Use [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/) for Git integration and previews. If setup produced a Pages target, consult the selected [Workers framework guide](../frameworks.md) before adjusting configuration; do not recreate the application blindly.

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
npm create cloudflare@latest my-app -- \
  --type=hello-world --lang=ts --no-git --no-deploy
```

**Auth in CI:**
```yaml
env:
  CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
  CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

## Framework-Specific

Identify the installed framework and rendering mode, then read its [Workers integration and upstream guidance](../frameworks.md). Adapter requirements differ for static and server-rendered output; do not add an adapter solely because of the framework name.

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
