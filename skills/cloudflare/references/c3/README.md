# C3 (create-cloudflare)

Use C3 to scaffold Cloudflare Workers projects. **Target Workers for static sites, SPAs, and full-stack apps.** Static output belongs on Workers Static Assets.

## Framework Setup

Read [Frameworks on Workers](../frameworks.md) first. Follow the selected framework's current Workers guide for its setup command, adapter, and upstream agent guidance. Some frameworks use their own setup tool. C3 defaults to Workers; keep that target.

For a basic Worker, follow [Get started with the CLI](https://developers.cloudflare.com/workers/get-started/guide/). For an existing framework app, follow [Deploy an existing project](https://developers.cloudflare.com/workers/framework-guides/automatic-configuration/) and the framework-specific guide.

## References

- [CLI options](api.md) — retrieve current arguments before scripting C3.
- [Generated configuration](configuration.md) — Worker configuration and bindings; framework output varies, so follow the selected guide.
- [Usage patterns](patterns.md) — CI/CD and project workflows.
- [Troubleshooting](gotchas.md) — setup and deployment failures.

After scaffolding, inspect the generated package scripts, run the development server, and verify the build before deployment. For Git integration and previews, use [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/).
