---
name: cf
description: Use the cf CLI to deploy Workers and static sites, configure projects with cloudflare.config.ts, migrate from Wrangler, or manage any Cloudflare resource from the command line.
---

# cf CLI

`cf` is Cloudflare's CLI for the whole API, in open beta and [open source](https://github.com/cloudflare/cf). It covers 3,000+ operations generated from Cloudflare's OpenAPI schemas via [Forge](https://blog.cloudflare.com/forge-open-source-generation-pipeline), against Wrangler's ~280 hand-built commands, and prints JSON by default. See the [launch post](https://blog.cloudflare.com/cloudflare-cf-cli-launch/) for the design.

Install it globally with `npm i -g cf`, or add it as a project dependency.

`cf` is beta and newer than your training data. Treat the installed binary as the source of truth and do not reconstruct commands from memory.

## Retrieve What the Task Needs

| Task | Source |
| --- | --- |
| Find the operation for a task | `cf cli search "<describe the task and resource type, anonymously>"`, then `cf <command> --help` for flags |
| Build an API request, or list every operation | `cf schema <command path>`; `cf schema --list` |
| How `cf` works, why it exists, and the config format | [Launch post](https://blog.cloudflare.com/cloudflare-cf-cli-launch/); [source and issues](https://github.com/cloudflare/cf) |
| Configure a Worker, bindings, triggers, or environments | Types in `node_modules/@cloudflare/config` |
| Deploy a static site or a framework project | [Static assets](https://developers.cloudflare.com/workers/static-assets/); [framework guides](https://developers.cloudflare.com/workers/framework-guides/) |
| Move a legacy Pages project to Workers | [Pages to Workers migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) |
| Choose a token permission for a CI deploy | [Authorization](https://developers.cloudflare.com/workers/authorization/) |

## Choose cf or Wrangler

| Situation | Use |
| --- | --- |
| New project, or any product outside Wrangler's ~280 commands | `cf` |
| JavaScript Worker still bundling with esbuild, or Rust or Python Workers | Wrangler; `cf` delegates the build and dev server to it |
| Legacy Pages project | Wrangler, or migrate to Workers: [`cf pages deploy`](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) is refused |

The two coexist. A project must declare exactly one build or dev-server implementation in its manifest: `@cloudflare/vite-plugin` (recommended), `wrangler`, `cloudflare-rs-dev-server`, or `cloudflare-py-dev-server`. When the open beta ends, a final major Wrangler release will point users to `cf`, with 18 months of Wrangler maintenance after that.

## Configure a Project

Projects use `cloudflare.config.ts`: a TypeScript file with `defineConfig` from `cf/config`, `bindings` helpers for env vars and resource bindings, and `triggers` for routes, schedules, queues, and email. Derive environments from a `({ mode })` factory instead of copying blocks. Loading the file requires Node.js >= 22.18.0.

This format is not documented on `developers.cloudflare.com`. Follow the [launch post](https://blog.cloudflare.com/cloudflare-cf-cli-launch/) and let the editor types from `node_modules/@cloudflare/config` resolve fields; do not copy field lists from memory.

Use `cf migrate` to convert a Wrangler project, and `cf init` to set up a new or existing one. Projects already building with Vite convert automatically.

## Deploy

`cf build` builds, `cf deploy` deploys. Useful flags: `--prebuilt` to deploy an existing Build Output Specification, `--dry-run` to build and run checks without uploading, `--tag` and `--message` to annotate the version, `--secrets-file` to upload secrets. `cf deploy --dry-run` does not authenticate, so use it to validate a change before touching a remote account.

In CI, authenticate with `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` rather than an interactive login. Deploying needs `Workers Scripts: Edit` on the token; retrieve the exact permission for the operation from [authorization](https://developers.cloudflare.com/workers/authorization/).

## Static Sites and Framework Projects

`cf pages deploy` reports that legacy Pages is not supported and directs you to `cf deploy`, which targets the new Pages on Workers. Follow the [Pages to Workers migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) before switching; the new [static assets docs](https://developers.cloudflare.com/workers/static-assets/) cover routing, caching, and limits.

For framework projects, `cf` detects the framework and expects a Build Output Specification under `.cloudflare/output/`; `cf deploy --prebuilt` reads an existing one. Verify current behavior for the project's framework against the [framework guides](https://developers.cloudflare.com/workers/framework-guides/) and the [Vite plugin's static assets docs](https://developers.cloudflare.com/workers/vite-plugin/reference/static-assets/) before relying on it.
