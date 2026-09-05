---
name: wrangler
description: Use Cloudflare Wrangler to inspect, develop, configure, deploy, or manage Workers resources. Apply when a task requires Wrangler commands or configuration; verify syntax against the project's installed version instead of relying on memorized flags.
---

# Wrangler CLI

Use Wrangler in a way that is compatible with the project, safe for the named Cloudflare account and environment, and verified in proportion to the change.

## Establish the local contract

Before choosing commands or configuration:

- Inspect `package.json`, the lockfile, existing Wrangler config, and repository conventions.
- Prefer the project's pinned, package-manager-resolved Wrangler binary. Check its version when version-specific behavior matters.
- Preserve the project's supported config format and conventions unless the user asks for a migration or a required feature demands one.
- Do not install or upgrade Wrangler merely because it is unavailable globally. Add or change the dependency only when that is part of the requested work, and use the project's package manager.

## Verify uncertain details

Wrangler changes frequently. Use the cheapest authoritative source that answers the question:

1. The installed package and `node_modules/wrangler/config-schema.json` for the project's accepted configuration.
2. `<project invocation> wrangler <command> --help` for commands and flags supported by the pinned version.
3. The official [Wrangler documentation](https://developers.cloudflare.com/workers/wrangler/) for current behavior, platform concepts, or features not present locally.

Retrieve only what the task needs. If current documentation and the pinned version differ, implement for the pinned version or explicitly include an upgrade in scope.

## Make changes safely

- Identify the target account, Worker, environment, and resource before a remote mutation. Do not infer production when the target is ambiguous.
- Inspect existing state before destructive or difficult-to-reverse operations. Use a supported dry run or preview when it provides meaningful evidence.
- Treat deploys, deletes, migrations, namespace changes, secret changes, and production data operations as remote side effects; perform only those authorized by the request.
- Never place secret values in source, Wrangler config, command arguments that may be logged, or chat output. Use Wrangler's secret mechanism or the project's existing secret workflow.
- Preserve unrelated configuration, bindings, environments, and user changes.
- Prefer generated binding types when the project already uses Wrangler type generation; regenerate them after relevant config changes.

## Validate the outcome

Choose checks based on risk and scope. Useful evidence may include config-schema validation, generated types, a dry-run build, focused tests, local development, resource inspection, or post-deploy health and logs.

Report the Wrangler version and target environment when they affect reproducibility. State which remote actions ran and distinguish verified results from commands the user still needs to execute.
