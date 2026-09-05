# Wrangler Programmatic API and Testing

Retrieve the [Wrangler API reference](https://developers.cloudflare.com/workers/wrangler/api/) and check installed exports and types before choosing an API or adapting an existing test suite.

| Task | Source |
| --- | --- |
| Choose a test runner and execution model | [Workers testing](https://developers.cloudflare.com/workers/testing/) |
| Test built Workers from a Node.js test runner, including multiple Workers | [Integration test harness](https://developers.cloudflare.com/workers/testing/test-harness/) |
| Mock outbound requests, seed storage, or replace bindings in harness tests | [Prepare test state](https://developers.cloudflare.com/workers/testing/test-harness/prepare-test-state/) |
| Test inside the Workers runtime with Vitest | [Vitest setup and migration guidance](https://developers.cloudflare.com/workers/testing/vitest-integration/write-your-first-test/) |
| Access emulated bindings from Node.js | [getPlatformProxy](https://developers.cloudflare.com/workers/wrangler/api/#getplatformproxy), including runtime differences and cleanup |
| Start a development server programmatically | [Cloudflare Vite plugin](https://developers.cloudflare.com/workers/vite-plugin/) and the development-server guidance in the Wrangler API reference |
| Generate binding and runtime types | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/) |

The API docs deprecate `unstable_startWorker` and `unstable_dev` in favor of `createTestHarness` for integration tests. Do not infer a stable `startWorker` export or rename imports blindly: check version support, build inputs, and test isolation before migrating. Use the chosen API's documented teardown so tests release runtime resources.
