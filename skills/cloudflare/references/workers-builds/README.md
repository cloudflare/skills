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

Prefer the Builds REST API so an agent can complete and verify setup:

1. Create or deploy the Worker with Wrangler, including an assets-only Worker
   for a static site. Confirm its name matches the Wrangler configuration.
2. Retrieve the current Builds API guide and resolve the Worker tag.
3. List existing repository connections and build tokens. Reuse an authorized
   GitHub or GitLab connection when available.
4. Create or update the production trigger with the repository, branch, root
   directory, build command, deploy command, build token, and watch paths.
5. Create or update the preview trigger when the project needs non-production
   builds.
6. Read both triggers back, start a test build, and inspect its commit, status,
   logs, deployment, and Git check.

If the account has no authorized connection for the Git provider, ask the user
to complete that provider's one-time app authorization. Resume API setup after
authorization instead of asking the user to configure triggers in the dashboard.

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
