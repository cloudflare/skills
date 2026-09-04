# Workers Builds API

Use the Builds REST API to manage repository connections and triggers, start or
cancel builds, inspect history, and retrieve logs. Retrieve the current API
reference before constructing requests because authentication requirements,
fields, and supported resources can change.

## Identity Model

Keep these identifiers distinct:

- **API token**: Authenticates a client calling the Builds API.
- **Build token**: Authorizes Workers Builds to deploy the Worker.
- **Worker name**: Human-readable project name.
- **Worker tag**: Immutable ID used as `external_script_id` by Builds endpoints.
- **Trigger UUID**: Identifies the production or preview trigger.
- **Build UUID**: Identifies one build and its logs.

The current API guide requires a user-scoped API token with Workers Builds
configuration permissions. Do not substitute an account-owned token without
checking current support.

## Read Before Write

Use this sequence for automation:

1. List Workers to resolve the Worker tag.
2. List repository connections and build tokens.
3. List the Worker's triggers.
4. Compare effective fields with the desired configuration.
5. Create or update only the intended production or preview trigger.
6. Read the trigger back and verify branch rules, commands, root, variables,
   token, cache, and paths.
7. Trigger a test build and inspect its source, status, and logs.

Do not assume the dashboard and trigger API contain identical state. A safe
automation flow detects drift and preserves secrets or settings it does not
intend to replace.

## Build Operations

The normal lookup chain is:

```text
Worker name -> Worker tag -> Trigger UUID -> Build UUID -> Logs
```

Manual builds require a branch, commit SHA, or both. Verify the resulting build
uses the expected commit and trigger. When canceling or retrying, record which
configuration is expected to be reused or refreshed.

## Schema Safety

Generated clients can lag live API responses. Validate the current schema
against a representative response before enforcing strict runtime validation.
When a documented enum or object shape differs from a live response, preserve
the response and report the mismatch rather than coercing it silently.

## Documentation

- https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/
- https://developers.cloudflare.com/api/resources/workers_builds/
