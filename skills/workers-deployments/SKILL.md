---
name: workers-deployments
description: Set up or troubleshoot Workers release workflows with Workers Builds or external CI, Workers Previews, staging resources, deployed smoke checks, gradual production rollouts, and rollbacks.
---

# Workers deployments

Take a Worker from a reviewed source revision through a verified deployment. Preserve the project's CI provider and release policy unless the task calls for changing them. For individual CLI commands and config edits, use the `wrangler` skill when installed; otherwise retrieve the relevant command documentation and check the project's installed Wrangler help and schema.

## Choose the release workflow

Read the relevant current documentation before implementing. Inspect the repository, build scripts, source revision, target account and Worker, production branch, and existing release automation. Identify which step builds, which uploads code, and which sends production traffic to it.

| Task | Read |
| --- | --- |
| Choose native Builds or an external provider | [CI/CD](https://developers.cloudflare.com/workers/ci-cd/) |
| Configure Git builds, project root, commands, and branch filters | [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/), [configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/), [build branches](https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/) |
| Use an existing CI pipeline | [External CI/CD](https://developers.cloudflare.com/workers/ci-cd/external-cicd/); follow its provider guide for authentication and deployment |
| Create branch or pull request environments | Workers Previews documentation below |
| Inspect one uploaded production Worker version | [Preview URLs](https://developers.cloudflare.com/workers/versions-and-deployments/preview-urls/); distinguish this version-based workflow from Workers Previews |
| Release production code or split traffic between versions | [Versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/), [gradual deployments](https://developers.cloudflare.com/workers/versions-and-deployments/gradual-deployments/) |
| Restore a previous production version | [Rollbacks](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/) |

Keep build variables and secrets separate from runtime configuration. Verify the branch-specific deploy command rather than assuming a setting labelled “preview” creates Workers Previews. An upload and a production deployment are different operations; a release pipeline must preserve that distinction.

## Workers Previews: documentation transition

Workers Previews are the branch/PR workflow proposed in [cloudflare-docs PR #31775](https://github.com/cloudflare/cloudflare-docs/pull/31775). The [documentation preview](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/) is pending documentation, not evidence that the feature is available in the target account or installed Wrangler version. Recheck the PR and published Workers docs before using its commands or configuration. If the preview site is unavailable, inspect the corresponding MDX changes in the PR.

Read only the relevant pending pages: [get started](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/get-started/), [configuration](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/configuration/), [resources and isolation](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/resources/), [limitations](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/limitations/), [automation](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/automation-examples/), or [test and debug](https://worker-previews-docs-2.preview.developers.cloudflare.com/workers/previews/test-and-debug/).

Establish whether the project uses Workers Previews, version-based Preview URLs, or separately deployed Wrangler environments. Do not substitute one for another silently. Published version-based Preview URL guidance does not establish branch resource isolation or support for the new Previews workflow. Where pending and published guidance disagree, identify the gap and verify the supported path rather than copying speculative syntax or automatically upgrading dependencies.

For Workers Previews, verify these boundaries against the applicable documentation and actual configuration:

- Resolve the Preview's variables, secrets, bindings, runtime settings, and configuration source before testing. A live URL alone does not establish that required bindings exist.
- Trace each binding to its backing resource. Copying configuration does not copy database rows, buckets, or other account resources. Use distinct test resources when writes must be isolated; check external service credentials and URLs as well.
- Check same-Worker versus cross-Worker Durable Object/Container bindings, service-binding destinations, Queue producers and consumers, and Cron or route invocation separately. A branch name is not proof that downstream calls and triggers stay within that branch.
- Check retention and cleanup behavior for the Preview and separately provisioned resources. Delete only resources owned by the intended Preview; do not infer ownership from a shared Worker name.

## Verify and release

Run the project's relevant build and tests, then probe the actual deployed URL. Select smoke checks that exercise the changed route and its required bindings; for a UI, check a representative rendered flow. Scope writes to the verified test resources. Inspect the deployment's [logs, traces, and metrics](https://developers.cloudflare.com/workers/observability/) when a probe fails. Stop the release at a failed check and diagnose it before retrying or shifting traffic.

A successful Preview does not prove the production configuration works. Resolve production bindings and secrets separately, record the source revision and resulting production version, and follow the documented production deployment path. Do not assume a Preview can be promoted as an unchanged production artifact.

For a gradual rollout, choose traffic increments and failure criteria appropriate to the service, observe the affected version, and check documented compatibility restrictions before changing traffic. Preserve the previous version identifier. A rollback restores code traffic, not connected resource data; verify that the previous code can still use the current schema and bindings before treating it as a recovery option.

Report the target Worker and environment, source revision, deployed URL/version, smoke-check results, production traffic state, and any documentation or validation gap. Distinguish a verified deployment from an uploaded version or a configured pipeline that has not run.
