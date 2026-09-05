---
name: cloudflare-ai-gateway
description: Integrate or migrate AI provider calls through Cloudflare AI Gateway, preserving SDK behavior while configuring authentication, provider credentials, routing, caching, and request observability. Use for gateway setup, provider migration, fallbacks, or troubleshooting gateway requests.
---

# Cloudflare AI Gateway

Connect the application's AI calls to the intended gateway and verify both the application response and gateway behavior. Keep the existing framework, SDK, model capabilities, and streaming contract unless changing them is part of the request.

## Choose the request path first

Inspect the calling runtime, installed SDK versions, current endpoint, required API shape, and provider credentials. Distinguish a migration from Vercel AI Gateway from use of the Vercel AI SDK: the SDK can remain in an application using Cloudflare AI Gateway.

Read the relevant current guide before writing requests or configuration:

| Need | Documentation and decision |
| --- | --- |
| New single-model HTTP or compatible SDK calls | [REST API](https://developers.cloudflare.com/ai-gateway/usage/rest-api/): choose the endpoint matching the request schema and model capabilities. |
| Calls inside a Worker | [Workers bindings](https://developers.cloudflare.com/ai-gateway/usage/worker-binding-methods/): inspect the project's binding and generated types, and select the intended gateway. |
| Preserve provider-specific API behavior | [Provider-native guides](https://developers.cloudflare.com/ai-gateway/usage/providers/): retain the provider's request shape rather than assuming all features translate to chat completions. |
| Keep Vercel AI SDK application code | [AI SDK integration](https://developers.cloudflare.com/ai-gateway/integrations/vercel-ai-sdk/): select an adapter compatible with the installed SDK and chosen request path. |
| Gateway-controlled model selection or fallbacks | [Dynamic routing](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/) and [route invocation](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/usage/): verify route prerequisites and deployed version. |

The legacy Unified compatibility endpoint is deprecated for ordinary single-model calls, but **dynamic routes still require it**; the REST inference endpoint does not support dynamic routes. Do not apply a single-model endpoint migration to a route. Check newer endpoint guidance against older integration examples before adopting them.

## Separate gateway access from provider credentials

Confirm the account and gateway, then use the selected endpoint's authentication instructions. The [REST authentication section](https://developers.cloudflare.com/ai-gateway/usage/rest-api/#authentication) defines inference token permissions; [Authenticated Gateway](https://developers.cloudflare.com/ai-gateway/configuration/authentication/) covers provider-native gateway access and binding authentication. An AI Gateway management token is not interchangeable with a REST inference token.

Choose and preserve the intended upstream credential and billing source using [BYOK](https://developers.cloudflare.com/ai-gateway/configuration/bring-your-own-keys/) and [Unified Billing](https://developers.cloudflare.com/ai-gateway/features/unified-billing/). Check credential precedence and alias support for the actual request path before removing provider headers or changing SDK keys. A successful request can otherwise charge a different billing source than intended. Keep credentials on the server; do not ship an account token to browser clients.

Make gateway or stored-key changes only within the requested account and scope. Use [gateway management](https://developers.cloudflare.com/ai-gateway/configuration/manage-gateway/) for setup rather than inventing CLI commands or assuming an existing gateway's settings.

## Apply only the requested controls

- Coordinate SDK retries, gateway [request handling](https://developers.cloudflare.com/ai-gateway/configuration/request-handling/), and route fallbacks. Bound the overall operation in the application: gateway response-start timeouts are not a deadline for the entire stream. Preserve cancellation and avoid multiplying retry layers.
- Use [dynamic routing](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/) when selection, quotas, or traffic splits belong in the gateway. Check each fallback's required schema and capabilities; a fallback that returns incompatible tool calls or structured output is not equivalent success.
- Read [caching](https://developers.cloudflare.com/ai-gateway/features/caching/) before enabling it or supplying a custom key. Include the context that determines who may receive a response; do not collapse personalized responses into one shared key.
- Inspect [logging settings](https://developers.cloudflare.com/ai-gateway/observability/logging/) before sending application payloads. Decide whether to retain full payloads or only request metadata; gateway log settings do not establish the upstream provider's retention policy.

For additional controls or troubleshooting, the bundled [AI Gateway references](../cloudflare/references/ai-gateway/README.md) route to the relevant docs when available. This skill can also be used independently through the direct documentation links above.

## Verify the request through the gateway

Run the project's relevant checks and exercise the changed call with a small non-sensitive input when credentials and scope permit. Verify the application's actual contract: completion, stream termination, tool calls, structured output, or error handling as applicable. A mock can validate request construction, but cannot prove remote gateway authentication or routing.

Correlate the response with the intended gateway's [request log](https://developers.cloudflare.com/ai-gateway/observability/logging/) or the binding's documented log identifier. Check provider/model, status, latency, usage, and the expected cache or route metadata. For a changed fallback or policy, exercise that branch in a test configuration; do not deliberately disrupt a production provider to trigger it.

If logs are missing, inspect collection settings and storage limits before concluding the gateway was bypassed. Diagnose gateway authentication, provider credentials, request schema, and policy failures separately using [troubleshooting](https://developers.cloudflare.com/ai-gateway/reference/troubleshooting/). Apply its provider-native header advice only to that request path; the REST endpoint's authentication section takes precedence for REST calls. Report what was exercised and any remote behavior that remains unverified.
