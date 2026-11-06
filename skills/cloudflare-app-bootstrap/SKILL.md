---
name: cloudflare-app-bootstrap
description: Get a Cloudflare Workers app to a working local request by connecting its bindings, secrets, and initial data, then verifying real application behavior. Use for app setup or onboarding after the project exists; use frameworks-on-cloudflare or cf-cli to create or configure the project, and wrangler or cf-cli for isolated commands.
---

# Cloudflare App Bootstrap

Take the project from its current state to a working local request that exercises the requested application behavior. Preserve the user's framework, package manager, CLI, and existing services. Read the relevant current documentation before choosing configuration or commands, and check support against installed versions with local CLI help and schemas.

## Start from the project

Inspect the app directory, lockfile, scripts, framework and adapter versions, Cloudflare configuration (`cloudflare.config.ts`, or a Wrangler configuration file), and existing setup instructions. In a monorepo, identify the application root before installing or generating files. Install from the existing lockfile and reuse the project's dependency and configuration conventions.

If the project has no Cloudflare configuration yet, set it up first with the `frameworks-on-cloudflare` skill for a framework app, or the `cf-cli` skill otherwise. Identify the source of any framework-generated configuration and edit that source. Do not replace a working app with a starter to resolve a configuration problem.

## Connect only the resources the app needs

Identify each binding used by application code and map it to an existing resource or a new local resource. Keep names consistent across code and configuration. Keep existing resource identifiers: a binding without one is treated as a new resource to provision on the next deploy.

Read [automatic provisioning](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#automatic-provisioning) before manually creating supported resources, and check which resource types it covers. Provisioning differs by CLI:

- **Wrangler:** `wrangler dev` creates local resources that persist between runs, and `wrangler deploy` creates remote resources and writes their identifiers back to the configuration file.
- **`cf`:** `cf deploy` provisions missing resources but does not write identifiers back to `cloudflare.config.ts` ([Develop, build, and deploy](https://developers.cloudflare.com/cf/projects/index.md)). Record the identifiers it reports in the configuration.

Establish the account, environment, and resource before any required remote creation.

Choose the dev command from the app's scripts and the [local development guide](https://developers.cloudflare.com/workers/local-development/index.md). A local Worker can use remote bindings: identify which resources are simulated and which calls reach real services before exercising writes. Use the framework's supported Workers dev integration; a frontend-only dev server does not establish that server bindings work.

For data-backed features, initialize only the state needed for the first meaningful request. Preserve existing migration tooling. For D1, follow [migrations](https://developers.cloudflare.com/d1/reference/migrations/index.md) and pass `--local` or `--remote` to [`d1 migrations apply`](https://developers.cloudflare.com/workers/wrangler/commands/d1/index.md#d1-migrations-apply) explicitly. `--local` initializes only the simulated database; apply remote migrations only when the requested setup includes that database change. For Durable Objects, check the current [class migration configuration](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/index.md) rather than treating it as a D1 SQL migration.

## Resolve configuration and secrets

Classify required values by consumer: build process, browser bundle, or Worker runtime. Keep private runtime credentials out of public client configuration. Use [Workers secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) for runtime secrets, and configure values the build needs in its [build environment](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/index.md#environment-variables).

In Wrangler and Vite projects, follow [local secret loading](https://developers.cloudflare.com/workers/local-development/environment-variables/index.md) for file names, environment precedence, and required-secret declarations. In a `cf` project, find the equivalent with `cf cli search` rather than assuming the Wrangler behavior. Reuse the project's chosen local secret file, make sure files with real values are ignored by Git, and provide names and safe placeholders for missing values. Local secrets are not installed on a deployed Worker. Authenticate only when the selected workflow needs account access; do not make login or deployment a blanket prerequisite for local setup.

## Verify the first application request

After changing configuration, regenerate [binding and runtime types](https://developers.cloudflare.com/workers/languages/typescript/index.md) with the project's script: `wrangler types` in a Wrangler project, or `cf workers types` in a `cf` project. Do not hand-edit generated declarations. Run the relevant existing build and type checks.

Start the actual development workflow and exercise a representative route or UI action, including its binding access when applicable. Check the response and the intended state change, not just that a server started. For missing credentials or unsupported local services, report exactly what remains unverified instead of claiming the app works.

Leave reproducible install, initialization, and dev commands in the project's setup documentation. Report the tested URL or action, which resources are local or remote, required values still missing, and any remaining remote setup. Continue to deployment only when it is part of the user's task.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
