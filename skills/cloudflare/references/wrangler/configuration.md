# Wrangler Configuration

Read the [configuration reference](https://developers.cloudflare.com/workers/wrangler/configuration/) for fields and binding shapes, then validate against the installed `wrangler/config-schema.json`. Identify the config actually consumed by the build or deploy script; edit source configuration rather than framework-generated output.

| Task | Source |
| --- | --- |
| Configure environments and field inheritance | [Wrangler environments](https://developers.cloudflare.com/workers/wrangler/environments/) |
| Select an environment in a Vite project | [Vite environments](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/) |
| Add secrets or diagnose local secret loading | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/) |
| Set or advance runtime compatibility | [Compatibility dates](https://developers.cloudflare.com/workers/configuration/compatibility-dates/) |
| Configure assets and routing | [Static assets configuration](https://developers.cloudflare.com/workers/static-assets/binding/) and [routes and domains](https://developers.cloudflare.com/workers/configuration/routing/) |
| Bind an existing resource or provision a new one | [Bindings and automatic provisioning](https://developers.cloudflare.com/workers/wrangler/configuration/) |

Check non-inheritable fields for each target environment; a working default config does not establish that staging has its bindings. Vite selects the environment at dev/build time, so a deployment flag cannot retarget a previously generated config. Verify resource identifiers when reusing resources, and regenerate project types after binding changes.
