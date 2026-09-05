# Workers Builds Troubleshooting

Diagnose the failed phase before changing application code.

## Evidence to Collect

- Account and Worker name, kept private where appropriate
- Build UUID and trigger
- Branch and commit SHA
- Timestamp and last successful build
- Last log line and failed phase
- Root directory, install, build, and deploy commands
- Runtime and package-manager versions
- Whether production or preview ran
- Whether the same commit succeeds locally or in external CI

## Queued

1. Check Cloudflare status and whether multiple Workers or accounts are
   affected.
2. Check current concurrency and queue limits in the docs.
3. Confirm no older build is blocking the trigger.
4. Check whether a newer queued build superseded this one.
5. Avoid repeated retries while an incident or capacity issue is active.

## Initializing

If the build fails before cloning, focus on control-plane state rather than
source code:

- Build token validity, ownership, permissions, and trigger association
- Account access and product entitlement
- Repository connection state
- Platform incident or runner allocation

Generic token recreation may not repair a stale trigger association. Verify the
effective trigger after rotation.

## Cloning

- Confirm the Git application is installed for the correct user or organization.
- Confirm it can access the selected repository and branch.
- Check whether the repository was transferred, renamed, or reinstalled.
- Verify submodule and private dependency access separately.
- Reconnect only when evidence points to the connection, then verify the new
  connection instead of retrying blindly.

## Installing

- Confirm the detected runtime and package-manager versions.
- Preserve the lockfile for the package manager the project actually uses.
- In a monorepo, determine whether installation covers the full workspace even
  when commands run from a project root.
- Reproduce with the same frozen-lockfile behavior locally.
- Do not delete lockfiles or force-clear caches as a default fix.

## Building

- Run the same commit and command with matching versions outside Workers Builds.
- Separate framework compilation from Wrangler deployment.
- Compare phase duration, memory use, CPU behavior, and output size.
- Disable build caching for one controlled comparison when stale output is
  plausible; do not make cache deletion the first response.
- If only the managed build hangs, collect the comparison for escalation.

## Deploying and Static Assets

- Confirm the deploy command completed and the intended Worker version exists.
- Separate asset discovery, hashing, deduplication, upload, and verification.
- For a large asset set, record the last uploaded count and duration.
- Do not treat a successful build label as proof that every intended artifact
  is live; verify the deployment and a representative asset.

## Production Works but Preview Fails

Inspect the preview trigger independently:

- Branch includes and excludes
- Build and preview deploy commands
- Root directory and watch paths
- Build variables and secrets
- Build token
- Preview URL support for the Worker's bindings

Saved production settings may not explain preview behavior. Verify which
trigger the build used before retrying.

## Git Feedback Is Stale or Noisy

Compare the terminal build state in Cloudflare with the Git check and
pull-request comment. In a monorepo, identify which Worker and trigger owns each
check. Retrieve current controls before promising that comments, checks, or
automatic configuration pull requests can be disabled independently.

## Escalate When

- A build cannot reach cloning despite a valid connection and token.
- The same commit and environment consistently succeed outside Workers Builds.
- The dashboard and trigger API disagree.
- A deleted token or repository connection remains effective after verified
  replacement.
- The build reports success without the expected deployment or assets.
- Multiple independent projects fail in the same phase at the same time.

## Documentation

- https://developers.cloudflare.com/workers/ci-cd/builds/troubleshoot/
- https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/
- https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/
