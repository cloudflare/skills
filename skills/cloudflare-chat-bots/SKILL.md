---
name: cloudflare-chat-bots
description: Build or troubleshoot Slack, Discord, Telegram, and other messaging-platform bots on Cloudflare Workers, including channel setup, verified webhooks, conversation routing, durable state, and replies. Use for external chat channels rather than browser chat UI alone.
---

# Chat bots on Cloudflare

Preserve the user's channel, SDK, model provider, and existing deployment. Retrieve the relevant current documentation before implementing; read only the selected integration and channel below.

## Choose the integration

| Existing stack or requirement | Read first |
| --- | --- |
| Chat SDK on Workers, including multiple channels | [Cloudflare Chat SDK integration](https://developers.cloudflare.com/agents/runtime/communication/chat-sdk/) for `agents/chat-sdk`, durable state, exports, and configuration |
| Think agent receiving messenger events | [Think messengers](https://developers.cloudflare.com/agents/harnesses/think/messengers/) for native ingress, conversation targets, and reply recovery |
| Slack-specific Agents SDK app | [Slack channel](https://developers.cloudflare.com/agents/communication-channels/slack/) and [Slack agent walkthrough](https://developers.cloudflare.com/agents/examples/slack-agent/) for installation, OAuth, and workspace isolation |
| Existing custom webhook implementation | [Agents webhooks](https://developers.cloudflare.com/agents/communication-channels/webhooks/) for verified ingress and identity-based routing |

For a new Chat SDK app, use the documented Cloudflare state integration. `createChatSdkState()` belongs in an Agent context; export `ChatSdkStateAgent` as documented so state sub-agents resolve. Do not replace this with process-local state or an invented adapter. Think has its own documented state export and routing; follow that path when Think is already selected.

Read [channel setup](references/channels.md) for the selected provider's onboarding and protocol. Adapter availability does not establish that every transport or feature works on Workers. Confirm the installed package's runtime requirements, especially persistent Gateway connections or polling. Report missing Cloudflare guidance instead of presenting an unverified integration as supported.

## Connect ingress to the right conversation

- Configure the selected app's required permissions, events, callback URLs, and credentials from its documentation. Separate installations when serving multiple workspaces; resolve the correct installation token for each outbound reply.
- Verify incoming requests before processing messages or trusting routing identities. Preserve the original body for the adapter's verifier. For custom verification, read the raw body once, verify it, then parse that same value; clone before reading if forwarding the original Request. Provider signatures and replay checks are protocol-specific.
- Derive tenant and conversation identities from verified provider data and trusted installation records. Scope conversation state by installation, channel, and thread as required; an arbitrary URL or header must not select another tenant. Follow the selected SDK's thread semantics instead of flattening group chats and DMs into one conversation.
- Reuse the SDK's durable subscriptions, locks, deduplication, and queues. Review state sharding when multiple installations or bot identities share an ingress Agent. Duplicate delivery and concurrent events must not produce duplicate application effects; state persistence alone does not guarantee exactly-once outbound delivery.

## Acknowledge and deliver

Read the provider's acknowledgment and retry rules before wiring handlers. Separate its timely acknowledgment from slow model or tool work. Use the selected SDK's documented reply lifecycle; The Think messenger integration already supplies managed reply fibers and recovery behavior.

For manual Worker ingress, read [execution context](https://developers.cloudflare.com/workers/runtime-apis/context/#waituntil): `ctx.waitUntil()` extends a Worker request for bounded background work, but is not durable job execution. Use durable execution when work must survive interruption. Do not apply Worker request-lifetime assumptions to an Agent's Durable Object or add a second queue around an SDK-managed lifecycle without a requirement.

Handle provider rate limits and reply failures through the selected adapter's error behavior. Keep internal exceptions and credentials out of external messages. Preserve reply targets and supported threading/streaming behavior.

## Verify the channel workflow

Use local fixtures and mocked outbound APIs before live channel testing. Check observable behavior relevant to the change:

- A valid event reaches the intended conversation and reply target; challenge or handshake requests receive the provider's required response.
- Invalid verification data, stale signed requests where applicable, and tenant mismatches produce no message processing or outbound reply.
- Duplicate delivery and concurrent events respect the chosen ordering and deduplication behavior, including after state reload.
- Two installations or conversations cannot read each other's context or use each other's credentials.
- Slow processing acknowledges on time; interruption and outbound failure follow the selected SDK's recovery contract without silently claiming delivery.

Report which provider paths were exercised, what remained mocked, and any adapter or runtime compatibility gaps. Live messages and installation changes require authorization within the user's task scope.
