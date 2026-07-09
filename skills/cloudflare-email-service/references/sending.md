# Sending Emails — Workers Binding & Agents SDK

Send emails from Cloudflare Workers using the native binding, or from AI agents using the Agents SDK. If your app is NOT on Workers, use the [REST API](rest-api.md) instead.

## Workers Binding

### Configuration

```jsonc
// wrangler.jsonc
{
  "send_email": [
    { "name": "EMAIL" }
  ]
}
```

For local development, add `"remote": true` so email sends are proxied to the real service:

```jsonc
{ "send_email": [{ "name": "EMAIL", "remote": true }] }
```

Run `npx wrangler types` to auto-generate the `Env` interface with your `EMAIL` binding. This produces a `worker-configuration.d.ts` with the real `SendEmail`, `EmailAttachment`, `EmailAddress`, and related types from the workerd runtime. Always use these generated types — do not define them manually.

**Note:** Workers binding uses `email` in the from object (`EmailAddress` type). REST API uses `address`. See [rest-api.md](rest-api.md).

## send()

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

Multiple recipients (max 50 combined to + cc + bcc):

```typescript
const response = await env.EMAIL.send({
  to: ["user1@example.com", "user2@example.com"],
  cc: ["manager@company.com"],
  bcc: ["archive@company.com"],
  from: { email: "orders@yourdomain.com", name: "Orders" },
  replyTo: "support@yourdomain.com",
  subject: "Order Confirmation #12345",
  html: "<h1>Your order is confirmed</h1>",
  text: "Your order is confirmed",
});
```

## Attachments

**Important:** The Workers binding and REST API handle attachment content differently:
- **Workers binding:** `content` accepts `string | ArrayBuffer | ArrayBufferView`. Strings are treated as **raw content** (not base64). For text files, pass the raw string. For binary files (images, PDFs), pass an `ArrayBuffer`. Note: `ArrayBuffer` does not work with `"remote": true` in local dev — deploy to test binary attachments.
- **REST API:** `content` is always a **base64-encoded string**. See [rest-api.md](rest-api.md).

```typescript
// Text file attachment — pass raw string content
const response = await env.EMAIL.send({
  to: "customer@example.com",
  from: "invoices@yourdomain.com",
  subject: "Your Report",
  html: "<h1>Report attached</h1>",
  text: "Report attached.",
  attachments: [{
    content: "Name,Amount\nWidget A,100\nWidget B,250", // Raw text, NOT base64
    filename: "report.csv",
    type: "text/csv",
    disposition: "attachment",
  }],
});

// Binary file attachment — use ArrayBuffer
const pdfBytes = await fetchPdfFromSomewhere(); // Returns ArrayBuffer
const response = await env.EMAIL.send({
  to: "customer@example.com",
  from: "invoices@yourdomain.com",
  subject: "Your Invoice",
  html: "<h1>Invoice attached</h1>",
  text: "Invoice attached.",
  attachments: [{
    content: pdfBytes,
    filename: "invoice-12345.pdf",
    type: "application/pdf",
    disposition: "attachment",
  }],
});

// Inline image — reference in HTML with cid:<contentId>
const imageBytes = await fetchImageFromSomewhere(); // Returns ArrayBuffer
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "marketing@yourdomain.com",
  subject: "New Product",
  html: '<img src="cid:product-hero" alt="Product" />',
  attachments: [{
    content: imageBytes,
    filename: "product.png",
    type: "image/png",
    disposition: "inline",
    contentId: "product-hero",
  }],
});
```

Total email size (body + attachments) cannot exceed 25 MiB.

## Custom Headers

Only whitelisted headers allowed. See the [headers reference](https://developers.cloudflare.com/email-service/reference/headers/).

```typescript
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "notifications@yourdomain.com",
  subject: "Your weekly digest",
  html: "<h1>Weekly Digest</h1>",
  headers: {
    "In-Reply-To": "<original-message-id@yourdomain.com>",
    "List-Unsubscribe": "<https://yourdomain.com/unsubscribe?id=abc123>",
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    "X-Campaign-ID": "weekly-digest-2026-03",
  },
});
```

## Legacy EmailMessage API

The `EmailMessage` API remains supported. Uses raw MIME via `mimetext`:

```typescript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

const msg = createMimeMessage();
msg.setSender({ name: "Sender", addr: "sender@yourdomain.com" });
msg.setRecipient("recipient@example.com");
msg.setSubject("Hello");
msg.addMessage({ contentType: "text/html", data: "<h1>Hello</h1>" });

await env.EMAIL.send(new EmailMessage("sender@yourdomain.com", "recipient@example.com", msg.asRaw()));
```

Requires `npm install mimetext` and `"nodejs_compat"` in compatibility flags.

## Agents SDK Email

Agents can receive and reply to emails natively via the Agents SDK.

```jsonc
// wrangler.jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "EmailAgent", "class_name": "EmailAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["EmailAgent"] }],
  "send_email": [{ "name": "EMAIL", "destination_address": "reply@yourdomain.com" }]
}
```

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

Route emails to agents with resolvers:

```typescript
import { routeAgentEmail } from "agents";
import { createAddressBasedEmailResolver } from "agents/email";

export default {
  async email(message, env) {
    await routeAgentEmail(message, env, {
      resolver: createAddressBasedEmailResolver("EmailAgent"),
    });
  },
};
```

Resolver types: `createAddressBasedEmailResolver` (recipient → instance name), `createSecureReplyEmailResolver(secret)` (HMAC-signed replies), `createCatchAllEmailResolver("Agent", "default")` (single inbox). Use `isAutoReplyEmail(email.headers)` to skip vacation responders.

## Error Handling

```typescript
try {
  const response = await env.EMAIL.send({ /* ... */ });
} catch (error) {
  // error.code is one of the E_* error codes
  console.error(`Failed: ${error.code} - ${error.message}`);
}
```

These error codes are for the **Workers binding** (thrown as Error objects with `.code` and `.message`). The **REST API** returns standard Cloudflare API numeric error codes instead — see [rest-api.md](rest-api.md).

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

## Restricted Bindings

Restrict which `from` addresses a binding can use:

```jsonc
{
  "send_email": [{
    "name": "RESTRICTED_EMAIL",
    "allowed_sender_addresses": ["noreply@yourdomain.com", "support@yourdomain.com"]
  }]
}
```
