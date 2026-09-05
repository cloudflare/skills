---
description: Deploy a Cloudflare Worker using its existing project workflow
argument-hint: [project-path-or-environment]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# Deploy a Worker

The user invoked this command with: $ARGUMENTS

1. Read [Wrangler](../skills/wrangler/SKILL.md), resolving the path relative to this command file, and follow its target selection, configuration, secrets, and validation guidance.
2. Fetch [versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/) and the relevant [Wrangler command reference](https://developers.cloudflare.com/workers/wrangler/commands/). Distinguish uploading a version from deploying it to serve traffic.
3. Run the project's build and validation workflow, then perform the requested deployment with the intended configuration and environment. Existing user authorization applies; ask only for unresolved information needed to select the target.
4. Report the target, deployment result and URL or version identifiers when available, checks performed, and any unresolved runtime validation.
