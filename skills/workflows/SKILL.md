---
name: workflows
description: "Build and review Cloudflare Workflows. Load for durable multi-step Worker applications, WorkflowEntrypoint classes, workflow bindings, retries, sleeps, waitForEvent, rollback, idempotent step design, instance management, Python Workflows, dynamic workflows, or Wrangler workflow commands. Retrieve current Cloudflare docs before exact APIs, limits, pricing, or compatibility dates."
---

# Cloudflare Workflows

Use Workflows for durable, multi-step processes that need persisted progress, retries, sleeps, external events, or long-running orchestration. Use Queues for simple async buffering/fanout, Durable Objects for per-entity coordination, and `ctx.waitUntil()` only for short best-effort post-response work.

## Retrieval Sources

Prefer current sources before exact APIs, limits, or pricing:

| Topic | URL |
| --- | --- |
| Overview | https://developers.cloudflare.com/workflows/ |
| Getting started | https://developers.cloudflare.com/workflows/get-started/guide/ |
| Rules of Workflows | https://developers.cloudflare.com/workflows/build/rules-of-workflows/ |
| Workers API | https://developers.cloudflare.com/workflows/build/workers-api/ |
| Trigger Workflows | https://developers.cloudflare.com/workflows/build/trigger-workflows/ |
| Events and parameters | https://developers.cloudflare.com/workflows/build/events-and-parameters/ |
| Sleeping and retrying | https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/ |
| Local development | https://developers.cloudflare.com/workflows/build/local-development/ |
| Wrangler commands | https://developers.cloudflare.com/workflows/reference/wrangler-commands/ |

## Workflow

1. Confirm the fit:
   - Multi-step durable process with retries/checkpoints: Workflows.
   - High-throughput single-step background work: Queues.
   - Per-user or per-room strongly consistent state: Durable Objects.
   - Short post-response best-effort task: `ctx.waitUntil()`.
2. Inspect `wrangler.*`, package manager, compatibility date, generated types, and existing Workflow bindings.
3. Define the Workflow class with `WorkflowEntrypoint<Env, Params>` and a `run(event, step)` method.
4. Add a `workflows` binding and run `npx wrangler types`.
5. Design steps before coding: each step should be granular, idempotent, restart-safe, and deterministically named.
6. Validate event payloads at the Worker boundary and inside the Workflow. TypeScript generics do not validate runtime input.
7. Test with the Workers runtime where possible, then smoke test deployed create/status/restart paths.

## Binding Pattern

```jsonc
{
  "workflows": [
    {
      "name": "billing-workflow",
      "binding": "BILLING_WORKFLOW",
      "class_name": "BillingWorkflow",
      "schedules": ["0 * * * *"]
    }
  ]
}
```

Use `script_name` for cross-script calls when the calling Worker binds to a Workflow defined in another Worker.

Use `schedules` on the binding for cron-started Workflow instances. Each cron run creates an instance automatically; do not add a separate Worker `scheduled()` handler unless the trigger needs custom logic.

## Implementation Rules

- Put side effects inside `step.do()` unless you are comfortable with them repeating after engine restarts.
- Make API and binding calls idempotent. For non-idempotent actions such as payment, check whether the action already completed before performing it.
- Keep steps small and self-contained. Do not wrap an entire process in one giant step.
- Do not rely on mutable state outside step returns. Workflows can hibernate and lose in-memory state.
- Do not mutate `event.payload`; return durable state from steps and pass that state forward.
- Name steps deterministically. Step names are part of cached execution identity.
- Use the `step.do()` callback context when retry-aware code needs it. Current docs expose properties such as the step name/count, attempt, and config; retrieve generated types before relying on exact names.
- Be careful with `Promise.race()` and `Promise.any()` around steps; retrieve current docs before using them.
- Create Hyperdrive or external database connections inside the step that uses them, not once across multiple steps.

## Step Outputs

- Step return values must be serializable.
- Do not return `Request`, `Response`, functions, class instances with methods, circular objects, locked streams, or already-read streams.
- For large binary step outputs, retrieve the current Workers API docs. JavaScript Workflows support fresh `ReadableStream<Uint8Array>` returns for larger binary output than normal non-stream step-result limits.
- Persist large final artifacts to R2, D1, or another durable store and return identifiers when that is more practical than returning the data.

## Instance Management

- Use `env.MY_WORKFLOW.create({ id, params })` to start an instance.
- Choose instance IDs deliberately. `create()` throws if an ID is already in use within retention; `createBatch()` is idempotent and skips existing IDs.
- Use `get(id).status()` for user-facing status and operations dashboards.
- Use `sendEvent()` to resume `step.waitForEvent()` paths. Event `type` must match the waiting step.
- Use `NonRetryableError` for validation or permanent failures that should not retry.
- Use rollback handlers for compensating actions after successful steps when later steps can fail.

## Gotchas

- Workflows are durable, not magic transactions. External systems still need idempotency keys, locks, or compensating actions.
- Long sleeps and waits are normal; design UI/status APIs for `waiting` states.
- Do not use Workflows as a replacement for every background job. Queues remain simpler for one-step async work.
- Retrieve current limits before choosing step counts, retention durations, payload sizes, or concurrency assumptions.
- Dynamic Workflows combine Workflows with Dynamic Workers; load `dynamic-workers` and retrieve both doc sets before implementing.
