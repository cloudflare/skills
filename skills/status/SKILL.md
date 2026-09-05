---
name: status
description: Inspect Cloudflare Worker deployment status or diagnostics without changing resources
---

# Inspect Worker Status

1. Read [Wrangler](../wrangler/SKILL.md), resolving the path relative to this skill file, for project inspection and documentation retrieval. Keep status inspection read-only: do not install, configure, deploy, or change resources.
2. Scope inspection to the requested Worker, environment, and question. Fetch only the relevant [Wrangler command reference](https://developers.cloudflare.com/workers/wrangler/commands/) for authentication or resource inspection, or [versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/) for deployment state.
3. When the question concerns runtime behavior, fetch the relevant [observability guide](https://developers.cloudflare.com/workers/observability/) and inspect available logs or metrics. Report unavailable access or telemetry without enabling it.
4. Report the target, observed state, evidence, and any checks that could not be performed. Deployment state alone does not establish application health.
