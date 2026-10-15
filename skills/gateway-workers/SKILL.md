---
name: gateway-workers
description: Build, debug, or review Cloudflare Workers invoked by the Forward action in Gateway HTTP policies, including the GatewayMiddleware entrypoint, Gateway types, context, and continuation.
---

# Gateway Workers

Read the current [Forward guide](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/forward-traffic/index.md) before implementing a Worker. It defines how Gateway invokes Workers on permitted HTTP traffic. Retrieve the relevant page below rather than copying setup, API payloads, or limits into the project from memory.

## Workflow

1. Inspect the existing Worker and choose a [Worker template](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/worker-templates/index.md) for the required transformation, synthetic response, or background task.
2. Export a named `GatewayMiddleware` class extending `WorkerEntrypoint` from `cloudflare:workers`. Implement `handle(request, context, next)` and return a `Response`. Gateway calls this method through RPC. A default `fetch()` handler alone does not implement the Forward contract.
3. For TypeScript, follow the chosen template's current package installation and type-import instructions.
4. Use the second argument for [Gateway context](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/available-context/index.md). It describes the original request and stays unchanged when the Worker modifies the request. Keep it distinct from `this.ctx` (Workers execution context) and `this.env` (bindings).
5. Continue the user's request with `next(request)` at most once, or return a synthetic response without calling it. `next()` always targets the original destination. Changes to the destination URL or host are ignored, and it cannot redirect, retry, or fan out. Use `fetch()` to send a request to a different destination. It creates an independent subrequest that does not inherit the user's Gateway policies or egress configuration.

## Context

Use the published types and context reference for field names and availability. Treat a falsy identity (`!identity`) as anonymous and guard optional posture values. Call `await context.identity()` or `await context.devicePosture()` only when needed. Both getters can reject. Catch lookup failures separately from missing values and decide how to handle each when the Worker depends on them. Use Gateway-provided identity rather than client-supplied identity headers.

## Gateway behavior

- Only the first matching Forward policy invokes a Worker. Worker invocation does not confirm successful body inspection. Follow the Forward guide's [inspection order](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/forward-traffic/index.md#how-it-works).
- Gateway inspects the final response, including synthetic responses. Modified request bytes are not inspected again before reaching the origin.
- Review the Forward guide's [limitations](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/forward-traffic/index.md#known-limitations) before choosing traffic: HTTPS requires decryption, WebSockets bypass the Worker, and matching Workers VPC traffic is dropped. Worker invocation failures fail closed.

## Validation

Type-check against the installed Gateway types and test the named RPC entrypoint, including zero or one continuation call and the context values the Worker uses. Then test a permitted request through a scoped Gateway Forward policy. A direct request to a default `fetch()` handler does not validate the Gateway path. Follow the chosen template's test procedure and the Forward guide's troubleshooting steps.

Check the [response and streaming rules](https://developers.cloudflare.com/cloudflare-one/traffic-controls/integrate-workers/forward-traffic/index.md#known-limitations): return a final status from `200` to `599`, return no body for HEAD requests or statuses `204`, `205`, and `304`, and stream bodies rather than buffering them.

## Related skills

- [cloudflare-one](../cloudflare-one/SKILL.md): Gateway policy design, traffic paths, identity, TLS, and rollout.
- [workers-best-practices](../workers-best-practices/SKILL.md): streaming, bindings, generated environment types, background work, observability, and runtime tests.
- [CLI selection](../cloudflare/SKILL.md#choose-the-cli): choose the existing `cf-cli` or `wrangler` skill for project setup and deployment.
