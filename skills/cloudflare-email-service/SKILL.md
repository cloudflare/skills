---
name: cloudflare-email-service
description: Send and receive transactional emails with Cloudflare Email Service (Email Sending + Email Routing). Use when building email sending (Workers binding or REST API), email routing, Agents SDK email handling, or integrating email into any app — Workers, Node.js, Python, Go, etc. Also use for email deliverability, SPF/DKIM/DMARC, wrangler email setup, MCP email tools, React Email templates, or when a coding agent needs to send emails. Even for simple requests like "add email to my Worker" — this skill has critical config details and gotchas.
---

# Cloudflare Email Service

> **Public Beta** — Email Service is currently in public beta. Known limitations: domain must use Cloudflare DNS, email templates are not yet available.

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

1. **Domain onboarded?** Run `npx wrangler email sending list` to see which domains have email sending enabled. If the domain isn't listed, run `npx wrangler email sending enable yourdomain.com` or see [cli-and-mcp.md](references/cli-and-mcp.md) for full setup instructions.
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
| **Build a full-stack email app** (send + receive) | Combined patterns with R2, Queues, AI | [examples.md](references/examples.md) |

## Quick Send — Workers Binding

The fastest path. No API keys — the binding handles authentication. This is the recommended approach for any app running on Cloudflare Workers.

The `from` address must use a domain that has been onboarded onto Email Sending (via `npx wrangler email sending enable yourdomain.com` or the Dashboard). You can use any local part (`anything@yourdomain.com`), but the domain must be onboarded. Sending from a non-onboarded domain fails with `E_SENDER_NOT_VERIFIED`.

```jsonc
// wrangler.jsonc
{
  "send_email": [
    { "name": "EMAIL" }
  ]
}
```

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response = await env.EMAIL.send({
      to: "user@example.com",
      from: { email: "welcome@yourdomain.com", name: "My App" },
      subject: "Welcome!",
      html: "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
      text: "Welcome! Thanks for signing up.",
    });

    return new Response(`Sent: ${response.messageId}`);
  },
} satisfies ExportedHandler<Env>;
```

See [sending.md](references/sending.md) for batch sends, attachments, Agents SDK, and React Email integration.

## Quick Send — REST API

For apps not running on Workers. Works from any language or platform.

**IMPORTANT:** The REST API uses a different endpoint and slightly different field names than the Workers binding:
- Endpoint: `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send`
- `from` object uses `address` key (not `email`): `{ "address": "...", "name": "..." }`
- `replyTo` is `reply_to` (snake_case)
- Response returns `{ delivered: [], permanent_bounces: [], queued: [] }` (not `messageId`)
- Errors use numeric codes, not string codes like Workers

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "user@example.com",
    "from": "welcome@yourdomain.com",
    "subject": "Welcome!",
    "html": "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
    "text": "Welcome! Thanks for signing up."
  }'
```

See [rest-api.md](references/rest-api.md) for more examples and error handling.

## Quick Receive — Email Routing

Process incoming emails with an `email()` handler. Incoming emails arrive via Cloudflare Email Routing and are delivered to your Worker.

```typescript
import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx): Promise<void> {
    // Buffer the raw stream — it can only be read once
    const raw = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(raw);

    console.log(`From: ${message.from}, Subject: ${parsed.subject}`);

    // Forward, reply, or reject
    await message.forward("team@company.com");
  },
} satisfies ExportedHandler<Env>;
```

See [routing.md](references/routing.md) for forwarding, replying, parsing attachments, and integration patterns.

## Quick Send — Agents SDK

If you're building an AI agent with the Cloudflare Agents SDK, agents can receive and reply to emails natively.

```typescript
import { Agent } from "agents";
import { type AgentEmail } from "agents/email";
import PostalMime from "postal-mime";

export class EmailAgent extends Agent<Env, State> {
  async onEmail(email: AgentEmail) {
    const parsed = await PostalMime.parse(await email.getRaw());

    await this.replyToEmail(email, {
      fromName: "My Agent",
      subject: `Re: ${parsed.subject}`,
      body: "Thanks for your email! I'll look into this.",
    });
  }
}
```

See [sending.md](references/sending.md) for email resolvers, secure reply routing, and combining with Workers.

## Wrangler Configuration

### Email Sending Binding

```jsonc
// wrangler.jsonc
{
  "send_email": [
    {
      "name": "EMAIL"                    // Binding name, accessed as env.EMAIL
    },
    {
      "name": "RESTRICTED_EMAIL",        // Optional: restrict who can send
      "allowed_sender_addresses": [
        "noreply@yourdomain.com",
        "support@yourdomain.com"
      ]
    }
  ]
}
```

### Email Routing (Inbound)

Email Routing is configured via Dashboard routing rules or the wrangler CLI (`wrangler email routing rules create`). No special wrangler binding is needed for receiving — just export an `email()` handler in your Worker and point a routing rule at it.

### Local Development

Add `"remote": true` to the `send_email` binding in `wrangler.jsonc`, then run `npx wrangler dev`. Your Worker runs locally but email sends are proxied to the real Email Service. Emails are actually sent, so use verified test addresses during development.

```jsonc
// wrangler.jsonc — for local development
{ "send_email": [{ "name": "EMAIL", "remote": true }] }
```

## Error Codes

These error codes are for the **Workers binding** (thrown as Error objects with `.code` and `.message`). The **REST API** returns standard Cloudflare API numeric error codes instead — see [rest-api.md](references/rest-api.md).

| Error Code | What It Means | What to Do |
|------------|---------------|------------|
| `E_VALIDATION_ERROR` | Invalid payload | Check email format, required fields |
| `E_FIELD_MISSING` | Required field missing | Add `to`, `from`, or `subject` |
| `E_TOO_MANY_RECIPIENTS` | Combined to/cc/bcc exceeds 50 | Split into multiple sends |
| `E_SENDER_NOT_VERIFIED` | Domain not onboarded | Run `wrangler email sending enable yourdomain.com` or onboard in Dashboard |
| `E_RECIPIENT_NOT_ALLOWED` | Recipient not in allowed list | Add to `allowed_destination_addresses` |
| `E_RECIPIENT_SUPPRESSED` | Address bounced or reported spam | Remove from your list; check suppression list in Dashboard |
| `E_SENDER_DOMAIN_NOT_AVAILABLE` | Domain not available for sending | Complete domain onboarding |
| `E_CONTENT_TOO_LARGE` | Content exceeds 25 MiB | Reduce attachments or body |
| `E_RATE_LIMIT_EXCEEDED` | Rate limit hit | Retry with exponential backoff |
| `E_DAILY_LIMIT_EXCEEDED` | Daily quota reached | Wait or request limit increase |
| `E_DELIVERY_FAILED` | SMTP delivery failure | Check recipient address, retry if transient |
| `E_INTERNAL_SERVER_ERROR` | Service temporarily unavailable | Retry with exponential backoff |
| `E_HEADER_NOT_ALLOWED` | Header not on whitelist | Use an allowed header; see [headers reference](https://developers.cloudflare.com/email-service/reference/headers/) |
| `E_HEADER_USE_API_FIELD` | Must use API field instead | Set `From`, `To`, etc. via the dedicated API fields, not `headers` |
| `E_HEADER_VALUE_INVALID` | Header value is malformed or empty | Fix the value format (e.g., List-Unsubscribe needs angle-bracket URIs) |
| `E_HEADER_VALUE_TOO_LONG` | Header value exceeds 2,048 bytes | Shorten the header value |
| `E_HEADER_NAME_INVALID` | Invalid header name | Fix characters or keep under 100 bytes |
| `E_HEADERS_TOO_LARGE` | Total headers exceed 16 KB | Reduce number or size of custom headers |
| `E_HEADERS_TOO_MANY` | More than 20 non-X headers | Reduce to 20 or fewer whitelisted headers |

For `E_RATE_LIMIT_EXCEEDED` and `E_DELIVERY_FAILED`, retry with exponential backoff. For validation errors (`E_VALIDATION_ERROR`, `E_FIELD_MISSING`, `E_SENDER_NOT_VERIFIED`), fix the request — retrying won't help.

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

## Platform Limits

| Component | Limit | Notes |
|-----------|-------|-------|
| Recipients (to, cc, bcc) | 50 per email | Combined across all recipient fields |
| Subject line | 998 characters | RFC 5322 compliant |
| Total message size | 25 MiB | Including attachments |
| Header size | 16 KB | All custom headers combined |
| Workers CPU time | 50ms per request | Standard Workers CPU limit |
| Workers subrequests | 50 per request | Includes email send operations |
| Workers memory | 128MB | Standard Workers memory limit |

## Prerequisites

- **Cloudflare account**
- **Domain on Cloudflare DNS** — Email Service requires Cloudflare as the authoritative nameserver
- **Domain onboarded to Email Sending** — run `wrangler email sending enable yourdomain.com` (auto-configures SPF and DKIM records)
- **For REST API**: a Cloudflare API token with email sending permission

## References

Read the reference that matches your situation. You don't need all of them.

- **[references/sending.md](references/sending.md)** — Workers binding API, attachments, Agents SDK email. For Workers or Agents SDK.
- **[references/rest-api.md](references/rest-api.md)** — REST endpoint, curl examples, error handling. For apps NOT on Workers.
- **[references/routing.md](references/routing.md)** — Inbound `email()` handler, forwarding, replying, parsing. For receiving emails.
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)** — Domain setup, wrangler commands, MCP tools. For first-time setup.
- **[references/deliverability.md](references/deliverability.md)** — SPF/DKIM/DMARC, bounces, suppressions, best practices.
- **[references/examples.md](references/examples.md)** — Full-stack patterns: signup flows, support inboxes, Queues integration.
