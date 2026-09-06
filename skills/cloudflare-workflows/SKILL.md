---
name: cloudflare-workflows
description: Build and debug durable multi-step jobs on Cloudflare Workflows, including approval flows, scheduled pipelines, retries, and resumable business processes. Use when work must persist progress across failures or waits, even if the user does not name Workflows.
---

# Build durable jobs with Workflows

Turn the requested process into a runnable Workflow, its trigger, and evidence that success and failure paths behave correctly. Preserve the existing framework, language, storage, and deployment setup; inspect pinned dependencies and bindings before changing configuration.

## Choose the execution model

- Choose Workflows when a job must persist progress, retry individual steps, or wait for external input. For recurring instances, check [direct Workflow schedules](https://developers.cloudflare.com/workflows/build/trigger-workflows/) before adding a separate scheduled Worker.
- Choose [Queues](https://developers.cloudflare.com/queues/) for buffered asynchronous message delivery. A consumer can start a Workflow when each message requires durable orchestration.
- Choose [Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/) when the requirement is scheduled Worker execution; scheduling alone does not define a durable multi-step process.
- Choose [Durable Objects](https://developers.cloudflare.com/durable-objects/) when shared state and coordination per entity are central. Preserve an existing suitable implementation unless migration is requested.

## Implement the process

Identify the trigger, immutable input, completion result, external effects, and any approval or timeout outcome. Read the relevant current docs before writing code; keep signatures and configuration in the docs rather than copying a starter blindly.

| Decision | Read before implementing |
| --- | --- |
| Add a Workflow class and binding to the project | [First Workflow](https://developers.cloudflare.com/workflows/get-started/guide/); [Workers API](https://developers.cloudflare.com/workflows/build/workers-api/) |
| Start from HTTP, a queue, another Worker, or a schedule | [Trigger Workflows](https://developers.cloudflare.com/workflows/build/trigger-workflows/) |
| Retry transient failures, stop permanent failures, or delay work | [Sleeping and retrying](https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/) |
| Wait for approval or a callback | [Events and parameters](https://developers.cloudflare.com/workflows/build/events-and-parameters/) |
| Inspect or manage a failed instance | [Wrangler commands](https://developers.cloudflare.com/workflows/reference/wrangler-commands/); [metrics and analytics](https://developers.cloudflare.com/workflows/observability/metrics-analytics/) |

Read [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/) before choosing step boundaries:

- Split independently retryable effects into steps. Persist state through step returns; do not rely on mutated input or in-memory accumulators surviving replay.
- Keep step names and branching deterministic from input or persisted results. Await step operations; consult the rules before introducing parallel or racing steps.
- Make repeated external effects safe using the destination's idempotency guarantees. A successful external write followed by an interrupted step can be attempted again. Check-then-write alone is not an atomic deduplication guarantee.

Configure retries and per-attempt timeouts for the downstream operation. Use the documented non-retryable error mechanism for permanent failures; define an eventual failure outcome rather than retrying indefinitely. Use durable sleep APIs for delays.

For events, distinguish creation parameters from later input. Match the target instance and event type, validate the callback at the application's existing trust boundary, and implement an explicit event-timeout outcome. Return the instance identifier from a trigger and expose status through the existing application interface; successful creation is not successful completion. Consult current creation and retention semantics before treating an instance ID as permanent deduplication.

## Verify and investigate

Use [local development](https://developers.cloudflare.com/workflows/build/local-development/) with the project's supported Wrangler or Vite tooling. Local Explorer can inspect instance status and step history, trigger runs, and send events. Check its version requirements before relying on it. Local Workflows do not support remote bindings or remote development mode.

For automated checks, read the [Workflow test APIs](https://developers.cloudflare.com/workers/testing/vitest-integration/test-apis/#workflows). Configure introspection before triggering instances, await the expected status or step result, and dispose introspectors. Exercise the relevant cases:

- Successful execution and the actual output or persisted effect.
- A transient failure followed by recovery, and exhausted or permanent failure with useful error evidence.
- Approval arrival and timeout when events are used.
- Repeated input or a retried external write without duplicate business effects.

Mock external services when testing retries; replacing the entire effect step with a successful result cannot establish its idempotency. Inspect the failed instance and step before changing limits or restarting work. Restart only when requested or already authorized and the repeated effects are understood. Report what ran locally, what failed, and any hosted behavior still unverified.

For additional examples, capacity, and configuration routes, use the bundled [Workflows documentation map](../cloudflare/references/workflows/README.md) when available, or the [official index](https://developers.cloudflare.com/workflows/llms.txt). Fetch current limits when payload size, concurrency, or retention matters.
