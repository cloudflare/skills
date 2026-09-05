---
name: workers-ai
description: Build or troubleshoot application AI features with Cloudflare Workers AI, including text streaming, structured extraction, embeddings, and image or speech inference. Use for model selection and integration through Workers bindings, REST, or an existing AI SDK; stateful agent orchestration belongs to the Agents SDK.
---

# Build application features with Workers AI

Implement the requested inference feature in the application's existing architecture. Ordinary generation, extraction, and embeddings do not require an agent framework. Preserve the user's chosen integration and model unless a verified capability gap requires a change.

Fetch the relevant current documentation before implementing. Use the [documentation index](https://developers.cloudflare.com/workers-ai/llms.txt) when the task is not covered below; keep changing model schemas and SDK examples in the docs rather than copying a fixed catalog into the project.

## Choose a model and integration

Inspect the existing request handler, consumer, dependencies, and Worker configuration. Establish the expected output, whether it must stream, and the task's quality, latency, and cost constraints. Open the selected model's page in the [catalog](https://developers.cloudflare.com/workers-ai/models/) and check its exact identifier, input/output schema, context budget, and feature support. A tutorial's example model is not a universal default.

| Application context | Documentation and decision |
| --- | --- |
| Worker without an SDK abstraction | Use the [native AI binding](https://developers.cloudflare.com/workers-ai/configuration/bindings/); configure it in the environment actually being run. |
| Existing Vercel AI SDK application | Preserve its SDK and client protocol; consult the [Workers AI provider integration](https://developers.cloudflare.com/workers-ai/configuration/ai-sdk/) and check installed SDK/provider versions before adapting examples. |
| External service or script | Follow [REST setup and authentication](https://developers.cloudflare.com/workers-ai/get-started/rest-api/); keep the account token server-side. |
| Existing OpenAI client | Check [compatible endpoints](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/) for the requested operation and model; compatibility is not a promise that every API or parameter works. |

For local development, follow [Workers and Wrangler setup](https://developers.cloudflare.com/workers-ai/get-started/workers-wrangler/). The Worker can execute locally while inference accesses the Cloudflare account and consumes usage. Do not require remote execution of the entire Worker or describe inference as offline. Distinguish mocked tests from real inference in validation results.

## Implement the requested output

- **Text and streaming:** use the selected model's schema and the chosen integration's response format. Native binding SSE, an SDK text stream, and an SDK UI stream are different contracts; match the actual consumer. Preserve incremental delivery rather than buffering the entire response before returning it.
- **Extraction and structured output:** read [JSON mode](https://developers.cloudflare.com/workers-ai/features/json-mode/) for supported models, schema format, and streaming restrictions. Validate output against the application's schema and handle failure to satisfy it; prompting for JSON alone does not establish a validated application contract. Do not silently drop the schema to make streaming work.
- **Embeddings:** inspect the model's dimensions and input limits before connecting an index. Keep query and document embeddings compatible; equal dimensions alone do not make different models interchangeable. A model change may require re-embedding existing content.
- **Images and audio:** use the task-specific model page for accepted media inputs, encoding, output format, and supported streaming. Do not parse all inference responses as text JSON or assume every speech model supports real-time use.

Keep retrieval and orchestration proportional to the task. Add retrieval when answers need grounding in a corpus, and stateful agents when the application actually needs coordinated state or agent behavior. Gateway request controls are a separate concern; retain any existing Gateway integration.

## Verify the feature

Run the project's relevant type/build checks, then exercise representative inputs through the actual response consumer when inference is available within the task's scope. Verify the behavior that matters: incremental rendering for streams, valid and invalid extraction results for structured output, retrieval compatibility for embeddings, or usable media with the expected content type for image/audio output. Judge model quality on the user's examples, not just a successful HTTP response.

Use [error codes](https://developers.cloudflare.com/workers-ai/platform/errors/) to distinguish configuration or schema failures from transient inference failures. Check [limits](https://developers.cloudflare.com/workers-ai/platform/limits/) and [pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) for the selected workload before making throughput or cost claims. Bound any retries and retain the original failure when retrying cannot fix it.

Report the integration and model chosen, observed behavior, and which checks used mocks or real inference. If account access prevents inference, finish the local checks and identify that remaining validation explicitly.
