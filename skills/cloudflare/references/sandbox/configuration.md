# Sandbox configuration documentation

[Choose the package line](./README.md#choose-the-package-line-first) before configuring the Worker or container. Use its get-started page for the initial scaffold, then fetch the relevant configuration guide.

| Task | Documentation |
| --- | --- |
| Bindings, migrations, container resources | [Wrangler configuration](https://developers.cloudflare.com/sandbox/configuration/wrangler/) |
| Image variants, additional tools, local port access | [Dockerfile reference](https://developers.cloudflare.com/sandbox/configuration/dockerfile/) |
| Package/image matching, builds, and rollout | [Deploy a Sandbox application](https://developers.cloudflare.com/sandbox/guides/deploy/); for stable-to-preview cutover, use [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/). |
| Sleep, keep-alive, startup, and logging options | [Sandbox options](https://developers.cloudflare.com/sandbox/configuration/sandbox-options/); preview callers must omit removed session/transport fields per the [preview overview](https://developers.cloudflare.com/sandbox/1-0-preview/). |
| Runtime environment | [Stable environment variables](https://developers.cloudflare.com/sandbox/configuration/environment-variables/) or [preview environment](https://developers.cloudflare.com/sandbox/1-0-preview/environment/) |
| Custom-domain preview URL routing | [Configure preview URLs on a custom domain](https://developers.cloudflare.com/sandbox/guides/preview-urls-custom-domain/) |
| Credentials and outbound requests | [Handle outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) |
