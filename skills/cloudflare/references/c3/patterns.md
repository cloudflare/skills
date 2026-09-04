# C3 Usage Patterns

## Quick Workflows

```bash
# TypeScript API Worker
npm create cloudflare@latest -- my-api --type=hello-world --lang=ts --deploy

# Next.js on Workers (recommended path)
npm create cloudflare@latest -- my-app --framework=next

# Astro static site on Workers
npm create cloudflare@latest -- my-blog --framework=astro --lang=ts
```

## CI/CD (GitHub Actions)

```yaml
- name: Deploy
  run: npm run deploy
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

**For non-interactive use, provide the choices relevant to the selected starter:**
```bash
--type=<value>       # Worker starter, or use --framework instead
--no-git             # Recommended (CI already in git)
--no-deploy          # Deploy separately with secrets
--framework=<value>  # Framework starter; --type is ignored
--lang=ts            # Language when applicable
```

## Monorepo

C3 detects workspace config (`package.json` workspaces or `pnpm-workspace.yaml`).

```bash
cd packages/
npm create cloudflare@latest -- my-worker --type=hello-world --lang=ts --no-deploy
```

## Custom Templates

```bash
# External Git repository
npm create cloudflare@latest -- --template=username/repo
npm create cloudflare@latest -- --template=cloudflare/templates/worker-openapi
```

Remote templates should contain `package.json`, a Wrangler configuration file, and a `src/` directory with the referenced Worker script. `--template` accepts repository forms such as `user/repo`, an HTTPS/SSH Git URL, a GitLab/Bitbucket URL, a subdirectory, branch, or commit.

## Existing Projects

```bash
# Clone an existing deployed Worker
npm create cloudflare@latest -- . --type=pre-existing --existing-script=my-worker

# Add Cloudflare Workers to an existing framework app
npm create cloudflare@latest -- . --framework=react-router --lang=ts --no-deploy
```

## Post-Creation Checklist

1. Review `wrangler.jsonc` - set `compatibility_date`, verify `name`
2. Create bindings: `wrangler kv namespace create`, `wrangler d1 create`, `wrangler r2 bucket create`
3. Generate types: `npm run cf-typegen`
4. Test: `npm run dev`
5. Deploy: `npm run deploy`
6. Set secrets: `wrangler secret put SECRET_NAME`
