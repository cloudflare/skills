# Wrangler Workflows

Retrieve the guide for the requested workflow and adapt it to the project's package manager, scripts, and installed versions.

| Task | Source |
| --- | --- |
| Scaffold a Worker | [CLI getting started](https://developers.cloudflare.com/workers/get-started/guide/) |
| Develop locally or select remote bindings | [Local development](https://developers.cloudflare.com/workers/local-development/) and [bindings by development mode](https://developers.cloudflare.com/workers/local-development/bindings-per-env/) |
| Connect Workers during development | [Developing with multiple Workers](https://developers.cloudflare.com/workers/local-development/multi-workers/) |
| Add tests, mocks, or integration testing | [API and testing](./api.md) |
| Manage KV, D1 migrations, R2, or other resources | [Wrangler command index](https://developers.cloudflare.com/workers/wrangler/commands/), then the relevant product's command page |
| Stage or deploy versions | [Versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/) |
| Roll back a deployment | [Rollback workflow and limitations](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/) |
| Inspect logs | [Real-time logs](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/) |

A locally running Worker can access real resources through remote bindings; choose the data target before testing writes. Rollbacks do not restore connected resource data. Validate deployment changes with the project's build and supported dry-run workflow for the intended config/environment, then use task-specific runtime checks; packaging success alone does not verify remote behavior.
