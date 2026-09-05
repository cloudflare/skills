# C3 (create-cloudflare)

C3 scaffolds applications for Cloudflare Workers and, when explicitly requested, Pages. Use it for new projects, framework setup, remote templates, and cloning an existing deployed Worker.

## Choose the Platform

Default new static, full-stack, framework, and API applications to Workers. Use Pages only for an existing Pages application or a confirmed Pages-only requirement; read the [Pages-to-Workers migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) before recreating an existing project.

## Create the Project

Use the project's package manager and follow the current [C3 CLI documentation](https://developers.cloudflare.com/pages/get-started/c3/); npm requires `--` before arguments passed to C3. For framework projects, follow the relevant [Workers framework guide](https://developers.cloudflare.com/workers/framework-guides/) instead of caching framework names or setup commands here.

Before running C3, confirm the destination directory and whether it should initialize Git, deploy, or open the deployed application. Read the current [CLI arguments](https://developers.cloudflare.com/pages/get-started/c3/#cli-arguments) before scripting C3 or using it non-interactively.

## Templates and Existing Projects

For remote templates or existing projects, follow the current [Workers get-started guide](https://developers.cloudflare.com/workers/get-started/guide/) and inspect the maintained [C3 templates](https://github.com/cloudflare/workers-sdk/tree/main/packages/create-cloudflare/templates). Do not assume a cached template layout or accepted repository syntax.

## Inspect the Generated Project

Treat the generated `package.json` scripts and Wrangler configuration as the source of truth because output varies by starter and framework. Use the [Wrangler configuration docs](https://developers.cloudflare.com/workers/wrangler/configuration/) when changing bindings or other generated settings, and regenerate types when the project exposes a type-generation script.

## CI and Authentication

Make deployment and Git initialization explicit. Supply credentials through the CI secret tool, never committed files or command output, and follow the [Workers CI/CD guidance](https://developers.cloudflare.com/workers/ci-cd/external-cicd/).

## Telemetry and Troubleshooting

Use C3's documented [telemetry controls](https://developers.cloudflare.com/pages/get-started/c3/#telemetry) rather than an environment-variable implementation detail. Diagnose failures from current `--help` and command output; consult the [C3 source](https://github.com/cloudflare/workers-sdk/tree/main/packages/create-cloudflare) when exact behavior is not documented.
