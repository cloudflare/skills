---
name: cloudflare-app-bootstrap
description: Set up a new or checked-out application for local development on Cloudflare Workers, connecting framework configuration, bindings, secrets, and initial data through a verified request. Use for app setup or onboarding, rather than isolated CLI commands or release management.
---

# Cloudflare App Bootstrap

Take the project from its current state to a working local request that exercises the requested application behavior. Preserve the user's framework, package manager, and existing services. Read the relevant current documentation before choosing configuration or commands; check support against installed versions using local CLI help and schemas. Use the `wrangler` skill when available for command details.

## Start from the project

Inspect the app directory, lockfile, scripts, framework and adapter versions, Wrangler configuration, and existing setup instructions. In a monorepo, identify the application root before installing or generating files. Reuse the existing dependency and configuration conventions.

- **Existing app without Workers configuration:** Check [automatic configuration](https://developers.cloudflare.com/workers/framework-guides/automatic-configuration/) for framework and Wrangler version support. Use the project's Wrangler to run `wrangler setup --dry-run` when useful, then `wrangler setup` to configure without deploying. Review adapter, script, and config changes against the existing app.
- **Already configured app:** Install from its lockfile and resolve missing setup steps. Identify the source of any framework-generated Wrangler config and edit that source.
- **New app:** Use [C3](https://developers.cloudflare.com/workers/get-started/guide/) and the appropriate [framework guide](https://developers.cloudflare.com/workers/framework-guides/). Choose the requested framework or a minimal Worker template appropriate to the app. Keep scaffolding within the requested directory and skip deployment when the task is local setup.

If automatic configuration cannot support the existing project, follow its framework guide. Do not replace a working app with a starter to resolve a configuration problem.

## Connect only the resources the app needs

Identify each binding used by application code and map it to an existing resource or a new local resource. Keep names consistent across code and configuration. Retain existing resource identifiers: removing an ID can create a different resource on a later deploy.

Read [automatic provisioning](https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning) before manually creating supported resources. Local development can create persistent local resources; deployment can provision remote resources and write identifiers back to config. Check current feature and version support instead of assuming every binding supports this workflow. Establish the account, environment, and resource before any required remote creation.

Choose the dev command from the app's scripts and [local development guide](https://developers.cloudflare.com/workers/local-development/). A local Worker can use remote bindings: identify which resources are simulated and which calls reach real services before exercising writes. Use the framework's supported Workers dev integration; a frontend-only dev server does not establish that server bindings work.

For data-backed features, initialize only the state needed for the first meaningful request. Preserve existing migration tooling; for D1, follow [migrations](https://developers.cloudflare.com/d1/reference/migrations/) and explicitly target the selected development database. Use local migrations for simulated D1; these do not initialize remote bindings. Apply remote migrations only when the requested setup includes that database change. For Durable Objects, check current [class export configuration](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/) rather than treating it as a D1 SQL migration.

## Resolve configuration and secrets

Classify required values by consumer: build process, browser bundle, or Worker runtime. Keep private runtime credentials out of public client configuration. Use [Workers secrets](https://developers.cloudflare.com/workers/configuration/secrets/) for runtime secrets; configure values needed by the build in its [build environment](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/#environment-variables).

Follow [local secret loading](https://developers.cloudflare.com/workers/local-development/environment-variables/) for file location, environment precedence, and required-secret declarations. Reuse the project's chosen local secret file, ensure actual values are ignored by Git, and provide names and safe placeholders for missing values. Local secrets are not automatically installed on a deployed Worker. Authenticate when the selected workflow needs account access; do not make login or deployment a blanket prerequisite for local setup.

## Verify the first application request

Regenerate [binding and runtime types](https://developers.cloudflare.com/workers/languages/typescript/) with the project's `wrangler types` script after changing configuration; do not hand-edit generated declarations. Run relevant existing build and type checks.

Start the actual development workflow and exercise a representative route or UI action, including its binding access when applicable. Check the response and intended state change, not just that a server started. For missing credentials or unsupported local services, report precisely what remains unverified instead of claiming the app works.

Leave reproducible install, initialization, and dev commands in the project's appropriate setup documentation. Report the tested URL or action, resource mode, required values still missing, and any remaining remote setup. Continue to deployment only when it is part of the user's task.
