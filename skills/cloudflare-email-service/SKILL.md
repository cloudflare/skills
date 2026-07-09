---
name: cloudflare-email-service
description: Send and receive transactional emails with Cloudflare Email Service (Email Sending + Email Routing). Use when building email sending (Workers binding or REST API), email routing, Agents SDK email handling, or integrating email into any app — Workers, Node.js, Python, Go, etc. Also use for email deliverability, SPF/DKIM/DMARC, wrangler email setup, MCP email tools, or when a coding agent needs to send emails. Even for simple requests like "add email to my Worker" — this skill has critical config details.
---

# Cloudflare Email Service

Your knowledge of the Cloudflare Email Service, Email Routing or Email Sending may be outdated. **Prefer retrieval over pre-training** for any Cloudflare Email Service task.

Cloudflare Email Service lets you send transactional emails and route incoming emails, all within the Cloudflare platform. Your knowledge of this product may be outdated — it launched in 2025 and is evolving rapidly. **Prefer retrieval over pre-training** for any Email Service task.

**If there is any discrepancy between this skill and the sources below, always trust the original source.** The Cloudflare docs, REST API spec, `@cloudflare/workers-types`, and Agents SDK repo are the source of truth. This skill is a convenience guide — it may lag behind the latest changes. When in doubt, retrieve from the sources below and use what they say.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Cloudflare docs | `cloudflare-docs` search tool or URL `https://developers.cloudflare.com/email-service/` | API reference, limits, pricing, latest features |
| REST API spec | `https://developers.cloudflare.com/api/resources/email_sending` | OpenAPI spec for the Email Sending REST API |
| Workers types | `https://www.npmjs.com/package/@cloudflare/workers-types` | Type signatures, binding shapes |
| Agents SDK docs | Fetch `docs/email.md` from `https://github.com/cloudflare/agents/tree/main/docs` | Email handling in Agents SDK |

## FIRST: Check Prerequisites

Before writing any email code, verify the basics are in place:

1. **Domain onboarded?** Run `npx wrangler email sending list` to see which domains have email sending enabled. If the domain isn't listed, run `npx wrangler email sending enable userdomain.com` or see [cli-and-mcp.md](references/cli-and-mcp.md) for full setup instructions.
2. **Binding configured?** Look for `send_email` in `wrangler.jsonc` (for Workers)
3. **postal-mime installed?** Run `npm ls postal-mime` (only needed for receiving/parsing emails)

## What Do You Need?

Start here. Find your situation, then follow the link for full details.

| I want to... | Path | Reference |
|--------------|------|-----------|
| **Send emails from a Cloudflare Worker** | Workers binding (no API keys needed) | [sending.md](references/sending.md) |
| **Send emails from an AI agent built with [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/)** | `onEmail()` + `replyToEmail()` in Agent class | [sending.md](references/sending.md) |
| **Send emails from an external app or agent** (Node.js, Go, Python, etc.) | REST API with Bearer token | [rest-api.md](references/rest-api.md) |
| **Send emails from a coding agent** (Claude Code, Cursor, Copilot, etc.) | MCP tools, wrangler CLI, or REST API | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **Receive and process incoming emails** (Email Routing) | Workers `email()` handler | [routing.md](references/routing.md) |
| **Set up Email Sending or Email Routing** | `wrangler email sending enable` / `wrangler email routing enable`, or Dashboard | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **Improve deliverability, avoid spam folders** | Authentication, content, compliance | [deliverability.md](references/deliverability.md) |

## Quick Start — Workers Binding

Add the binding to `wrangler.jsonc`, then call `env.EMAIL.send()`. The `from` domain must be onboarded via `npx wrangler email sending enable yourdomain.com`.

```jsonc
// wrangler.jsonc
{ "send_email": [{ "name": "EMAIL" }] }
```

```typescript
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: { email: "welcome@yourdomain.com", name: "My App" },
  subject: "Welcome!",
  html: "<h1>Welcome!</h1>",
  text: "Welcome!",
});
```

The binding is recommended for Workers — no API keys needed. If a user specifically requests the REST API from within a Worker (e.g., they already have an API token workflow), that works too — see [rest-api.md](references/rest-api.md).

See [sending.md](references/sending.md) for the full API, batch sends, attachments, custom headers, restricted bindings, and Agents SDK integration.

## Quick Start — REST API

For apps outside Workers, or within Workers if the user explicitly requests it. Key differences from the Workers binding:

- Endpoint: `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send`
- `from` object uses `address` (not `email`): `{ "address": "...", "name": "..." }`
- `replyTo` is `reply_to` (snake_case)
- Response returns `{ delivered: [], permanent_bounces: [], queued: [] }` (not `messageId`)

See [rest-api.md](references/rest-api.md) for curl examples, response format, and error handling.

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Forgetting `send_email` binding in wrangler config | Email Service uses a binding, not an API key | Add `"send_email": [{ "name": "EMAIL" }]` to wrangler.jsonc |
| Sending from an unverified domain | Domain must be onboarded onto Email Sending before first send | Run `wrangler email sending enable yourdomain.com` or onboard in Dashboard |
| Reading `message.raw` twice in email handler | The raw stream is single-use — second read returns empty | Buffer first: `const raw = await new Response(message.raw).arrayBuffer()` |
| Missing `text` field (HTML only) | Some email clients only show plain text; also helps spam scores | Always include both `html` and `text` versions |
| Using email for marketing/bulk sends | Email Service is for transactional email only | Use a dedicated marketing email platform for newsletters and campaigns |
| Forwarding to unverified destinations | `message.forward()` only works with verified addresses | Run `wrangler email routing addresses create user@gmail.com` or add in Dashboard |
| Testing with fake addresses | Bounces from non-existent addresses hurt sender reputation | Use real addresses you control during development |
| Hardcoding API tokens in source code | Tokens in code get committed and leaked | Use environment variables or Cloudflare secrets |
| Ignoring the `from` domain requirement | The `from` address must use a domain onboarded to Email Service | Verify the domain first, then send from `anything@that-domain.com` |
| Using `email` key in REST API `from` object | REST API uses `address` not `email` for `from` object | Use `{ "address": "...", "name": "..." }` for REST, `{ "email": "...", "name": "..." }` for Workers |
| Using `replyTo` in REST API | REST API uses snake_case field names | Use `reply_to` for REST API, `replyTo` for Workers binding |

## References

Read the reference that matches your situation. You don't need all of them.

- **[references/sending.md](references/sending.md)** — Workers binding API, attachments, Agents SDK email. For Workers or Agents SDK.
- **[references/rest-api.md](references/rest-api.md)** — REST endpoint, curl examples, error handling. For apps NOT on Workers.
- **[references/routing.md](references/routing.md)** — Inbound `email()` handler, forwarding, replying, parsing. For receiving emails.
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)** — Domain setup, wrangler commands, MCP tools. For first-time setup.
- **[references/deliverability.md](references/deliverability.md)** — SPF/DKIM/DMARC, bounces, suppressions, best practices.
