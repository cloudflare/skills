---
description: Inspect Cloudflare Worker deployment status or diagnostics without changing resources
argument-hint: [worker-or-diagnostic-question]
allowed-tools: [Read, Glob, Grep, Bash, WebFetch]
---

# Inspect Worker Status

The user invoked this command with: $ARGUMENTS

1. Read [Wrangler](../skills/wrangler/SKILL.md), resolving the path relative to this command file, for project inspection and documentation retrieval. Keep this command read-only: do not install, configure, deploy, or change resources.
2. Scope inspection to the requested Worker, environment, and question. Fetch only the relevant [Wrangler command reference](https://developers.cloudflare.com/workers/wrangler/commands/) for authentication or resource inspection, or [versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/) for deployment state.
3. When the question concerns runtime behavior, fetch the relevant [observability guide](https://developers.cloudflare.com/workers/observability/) and inspect available logs or metrics. Report unavailable access or telemetry without enabling it.
4. Report the target, observed state, evidence, and any checks that could not be performed. Deployment state alone does not establish application health.
