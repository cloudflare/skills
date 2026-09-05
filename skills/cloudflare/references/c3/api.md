# C3 CLI Reference

## Invocation

```bash
npm create cloudflare@latest -- [name] [flags]  # NPM requires --
yarn create cloudflare [name] [flags]
pnpm create cloudflare@latest [name] [flags]
```

## Core Flags

| Flag | Values | Description |
|------|--------|-------------|
| `--category` | `hello-world`, `web-framework`, `demo`, `remote-template` | Template category |
| `--type` | `hello-world`, `hello-world-durable-object`, `common`, `scheduled`, `queues`, `openapi`, `pre-existing` | Application type; ignored when `--framework` is supplied |
| `--platform` | `pages` | Explicitly target Pages; omit for the recommended Workers default |
| `--framework` | `next`, `react-router`, `astro`, `nuxt`, `svelte`, `solid`, `qwik`, `vue`, `angular`, `hono`, and other listed frameworks | Use the framework's current setup flow |
| `--lang` | `ts`, `js`, `python` | Project language |
| `--ts` / `--no-ts` | Deprecated | Use `--lang=ts` or `--lang=js` |

## Deployment Flags

| Flag | Description |
|------|-------------|
| `--deploy` / `--no-deploy` | Deploy immediately (prompts interactive, skips in CI) |
| `--git` / `--no-git` | Initialize git (default: yes) |
| `--open` | Open browser after deploy |

## Advanced Flags

| Flag | Description |
|------|-------------|
| `--template=user/repo` | External Git repository template |
| `--existing-script=worker-name` | Clone an existing deployed Worker; coerces type to `pre-existing` |
| `--accept-defaults` / `-y` | Accept defaults; individual flags can still override them |
| `--auto-update` / `--no-auto-update` | Control automatic C3 updates |

## Environment Variables

```bash
CLOUDFLARE_API_TOKEN=xxx    # For deployment
CLOUDFLARE_ACCOUNT_ID=xxx   # Account ID
CREATE_CLOUDFLARE_TELEMETRY_DISABLED=1  # Disable telemetry
```

## Exit Codes

`0` success, `1` user abort, `2` error

## Examples

```bash
# TypeScript Worker
npm create cloudflare@latest -- my-api --type=hello-world --lang=ts --no-deploy

# Next.js on Workers (Cloudflare currently recommends vinext)
npm create cloudflare@latest -- my-app --framework=next

# Astro on Workers
npm create cloudflare@latest -- my-blog --framework=astro --deploy

# CI: non-interactive
npm create cloudflare@latest -- my-app --framework=react-router --lang=ts --no-git --no-deploy

# Intentional Pages project
npm create cloudflare@latest -- --platform=pages

# GitHub template
npm create cloudflare@latest -- --template=cloudflare/templates/worker-openapi

# Convert existing project
npm create cloudflare@latest -- . --type=pre-existing --existing-script=my-worker
```
