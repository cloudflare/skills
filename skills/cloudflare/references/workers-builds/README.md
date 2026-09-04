# Workers Builds

Cloudflare's integrated CI/CD system for Workers. Connect a GitHub or GitLab
repository to automatically build and deploy a Worker when code is pushed.

Workers is the recommended platform for new static sites, SPAs, and full-stack
applications. Use Workers Builds when those projects need Git-based deployments
and previews.

## When to Use Workers Builds

- Deploy a Worker from GitHub or GitLab on every push
- Create preview versions for non-production branches
- Keep build and deployment status in the Cloudflare dashboard and Git provider
- Use build caching and watch paths for frameworks or monorepos
- Trigger builds from another system with Deploy Hooks

Use an external CI/CD provider when the repository is hosted elsewhere, is on a
self-hosted Git provider, or needs a pipeline that Workers Builds does not
support. Use Wrangler for local or manual deployment.

## Build Model

Workers Builds can have two triggers for a Worker:

1. The production trigger runs for the production branch and normally deploys
   with `npx wrangler deploy`.
2. The optional preview trigger runs for non-production branches and normally
   uploads a version with `npx wrangler versions upload`.

A build can run an optional build command before its deploy command. Build
configuration includes the repository, branch rules, root directory, commands,
build variables and secrets, build token, cache, and watch paths.

## Get Started

1. Create a Worker, including an assets-only Worker for a static site.
2. Make sure the dashboard Worker name matches the `name` in the Wrangler
   configuration in the selected root directory.
3. Open the Worker in the dashboard and go to **Settings > Builds**.
4. Connect a GitHub or GitLab repository.
5. Configure the production branch and commands.
6. Enable non-production builds if the project needs previews.
7. Push a commit and verify the source commit, build, deployment, and Git check.

## In This Reference

- [Configuration](./configuration.md) - Triggers, commands, variables, tokens, caching, and watch paths
- [Patterns](./patterns.md) - Static sites, previews, monorepos, hooks, and migration
- [API](./api.md) - Programmatic trigger and build management
- [Gotchas](./gotchas.md) - Phase-based troubleshooting and safe recovery

## Current Documentation

- https://developers.cloudflare.com/workers/ci-cd/builds/
- https://developers.cloudflare.com/workers/ci-cd/builds/configuration/
- https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/

Retrieve current documentation before stating limits, pricing, supported build
image versions, API fields, token support, or preview limitations.
