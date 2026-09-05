# Workers Builds Patterns

## Static Site on Workers

A static site does not require a Worker script:

```jsonc
{
  "name": "my-static-site",
  "compatibility_date": "2026-09-04",
  "assets": {
    "directory": "./dist"
  }
}
```

Set the build command to the project's static build, such as `npm run build`,
and the production deploy command to `npx wrangler deploy`. Workers is the
recommended platform for new static sites; do not choose Pages only because the
project needs Git deploys or previews.

## Production and Branch Previews

Use the production trigger for the live branch and enable non-production builds
for branch previews. Keep `npx wrangler versions upload` as the preview command
unless the application needs a documented alternative.

Do not change a production Worker's preview command to `wrangler deploy` merely
to work around preview limitations. That can update production resources. Use a
separate staging Worker or Wrangler environment when the application cannot be
represented safely by an uploaded preview version.

## Monorepo With Multiple Workers

For each Worker:

1. Set its project root directory.
2. Include its source, shared packages, workspace manifests, and lockfile in
   watch paths.
3. Exclude unrelated applications.
4. Use a package-manager filter if installation otherwise traverses every
   workspace.
5. Verify each Worker produces its own terminal Git check and expected preview.

Avoid copying the same configuration blindly across Workers. Confirm the Worker
name, production branch, deploy command, variables, and token for each trigger.

## Deploy Hooks

Use a Deploy Hook when a CMS, scheduled task, or other external system must
start a build without a Git push. Treat the hook URL as a secret. Retrieve the
current rate limits and deduplication behavior before designing a high-volume
integration.

## Build Notifications

Workers Builds emits lifecycle events that can be consumed through Event
Subscriptions. Use them to send build status to Slack, email, or another system
without polling. Include the Worker, branch, commit, build outcome, and preview
or live URL in notifications.

## Pages to Workers

For an existing Pages project:

1. Follow the current Pages-to-Workers migration guide for framework,
   configuration, bindings, headers, redirects, domains, and preview behavior.
2. Create the Worker and validate it before changing production traffic.
3. Connect the repository to Workers Builds.
4. Configure build-time variables separately from runtime variables and
   secrets.
5. Enable non-production builds and test preview behavior.
6. Disable Pages automatic deployments after Workers Builds is operating.
7. Remove the Pages project only after traffic and rollback plans are verified.

Do not delete the Pages project as the first migration step.

## External CI as a Control Experiment

When the same build hangs only in Workers Builds, run the identical commit,
runtime versions, install command, build command, and deploy dry run locally or
in existing CI. Record phase timings and resource behavior. This comparison can
separate project failures from managed build environment failures without
immediately moving the production pipeline.

## Documentation

- https://developers.cloudflare.com/workers/static-assets/get-started/
- https://developers.cloudflare.com/workers/ci-cd/builds/advanced-setups/
- https://developers.cloudflare.com/workers/ci-cd/builds/deploy-hooks/
- https://developers.cloudflare.com/queues/event-subscriptions/
- https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/
