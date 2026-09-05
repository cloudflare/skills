# Channel setup

Read only the selected channel. Fetch adapter documentation for exact configuration and follow its linked provider documentation for permissions, installation, verification, and acknowledgment rules. Translate framework-specific examples to the existing Worker entry point; preserve the chosen authentication setup.

| Channel | Sources | Decisions to resolve |
| --- | --- | --- |
| Slack | [Cloudflare Slack guide](https://developers.cloudflare.com/agents/examples/slack-agent/), [Chat SDK Slack adapter](https://chat-sdk.dev/adapters/official/slack.md), [Slack request verification](https://docs.slack.dev/authentication/verifying-requests-from-slack/) | Single installation or multi-workspace OAuth; mentions, DMs, or subscribed threads; signed Events API and interactive requests; installation-specific tokens |
| Discord | [Chat SDK Discord adapter](https://chat-sdk.dev/adapters/official/discord.md) | HTTP Interactions or Gateway events; required permissions/intents, public-key verification, and deferred replies. HTTP interaction setup alone does not receive all Gateway message events; validate the requested transport on Workers |
| Telegram | [Think messengers](https://developers.cloudflare.com/agents/harnesses/think/messengers/), [Chat SDK Telegram adapter](https://chat-sdk.dev/adapters/official/telegram.md) | Webhooks or polling; webhook secret-token verification; group/DM behavior and bot identity. For Think, use its documented Telegram helper and state export |

For another channel, start with the selected SDK's adapter documentation and [Cloudflare's Chat SDK state integration](https://developers.cloudflare.com/agents/runtime/communication/chat-sdk/). Verify the required runtime and event types before choosing an adapter. Think's generic messenger helper does not imply a built-in helper for every provider; follow its custom-adapter verification contract when needed.
