# Wrangler Troubleshooting

Capture the failing command, installed version, selected config/environment, and error before changing the setup. Retrieve the relevant source instead of applying a generic remote-mode or authentication reset.

| Symptom | Source and decision |
| --- | --- |
| Command or API is missing | Project-local command help; [commands](https://developers.cloudflare.com/workers/wrangler/commands/) and [API reference](https://developers.cloudflare.com/workers/wrangler/api/) for version support and deprecations |
| Binding or variable is unavailable | [Configuration](./configuration.md): check environment inheritance, resource identity, and generated config |
| Local behavior differs from deployment | [Supported bindings per development mode](https://developers.cloudflare.com/workers/local-development/bindings-per-env/): identify the actual runtime and data target |
| Local secrets are missing | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/): check local file precedence and required declarations |
| Authentication or account selection fails | [General commands](https://developers.cloudflare.com/workers/wrangler/commands/general/) |
| Runtime, compatibility, or startup errors | [Errors and exceptions](https://developers.cloudflare.com/workers/observability/errors/) and [Node.js compatibility](https://developers.cloudflare.com/workers/runtime-apis/nodejs/) |
| Static assets return unexpected responses | [Static assets routing](https://developers.cloudflare.com/workers/static-assets/routing/) |
| Placement does not improve latency | [Placement](https://developers.cloudflare.com/workers/configuration/placement/) |
| A resource or deployment hits a limit | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) and [static assets limits](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/); follow the specific product docs for resource limits |
| Tests hang or bindings behave differently | [API and testing](./api.md): check runtime choice, isolation, and teardown |
