# Receiving & Routing Inbound Email

This reference covers Email Routing — handling incoming emails sent to your domain. Emails arrive via Cloudflare Email Routing and are delivered to a Worker's `email()` handler, where you can forward, reply, reject, parse, or integrate them with other services.

## Table of Contents

- [Architecture](#architecture)
- [Email Handler](#email-handler)
- [ForwardableEmailMessage Interface](#forwardableemailmessage-interface)
- [Core Operations](#core-operations)
- [Parsing Emails](#parsing-emails)
- [Replying to Emails](#replying-to-emails)
- [Combined Send + Receive](#combined-send--receive)
- [Integration Patterns](#integration-patterns)
- [Gotchas](#gotchas)
- [Limits](#limits)

## Architecture

```
Sender → Email → Cloudflare MX → Email Routing → Worker
                                                      ↓
                                                Process + Decide
                                                      ↓
                                  ┌──────────────┬─────┴──────┐
                                  ↓              ↓            ↓
                              Forward         Reply        Reject
```

1. Email arrives at your domain (e.g., `support@yourdomain.com`)
2. Cloudflare Email Routing matches the recipient to a routing rule
3. The routing rule delivers the email to your Worker's `email()` handler
4. Your Worker processes the email and decides what to do

## Email Handler

Export an `email()` function from your Worker. This runs for every email that matches a routing rule.

```typescript
export default {
  async email(message, env, ctx): Promise<void> {
    console.log(`Email from ${message.from} to ${message.to}`);
    await message.forward("team@company.com");
  },
} satisfies ExportedHandler<Env>;
```

No special wrangler binding is needed for receiving email. A routing rule connects incoming addresses to your Worker.

### Setting Up Routing Rules

Via wrangler CLI:

```bash
# Enable Email Routing on the domain first
npx wrangler email routing enable yourdomain.com

# Create a rule that sends support@ emails to your Worker
npx wrangler email routing rules create yourdomain.com \
  --name "Support to Worker" \
  --match "support@yourdomain.com" \
  --forward "worker:my-email-processor"
```

Via Dashboard:

1. Go to **Cloudflare Dashboard** > **Compute & AI** > **Email Service** > **Email Routing**
2. Select your domain > **Routing Rules** tab
3. **Create Address**: set the custom address (e.g., `support`) and action to **Send to a Worker**, then select your deployed Worker

## ForwardableEmailMessage Interface

The `message` object your handler receives:

```typescript
interface ForwardableEmailMessage {
  readonly from: string;           // Sender email address (envelope MAIL FROM)
  readonly to: string;             // Recipient email address (envelope RCPT TO)
  readonly headers: Headers;       // Email headers (Subject, Message-ID, etc.)
  readonly raw: ReadableStream;    // Raw MIME email content stream
  readonly rawSize: number;        // Size of raw email in bytes
  readonly canBeForwarded: boolean; // Whether the message can be forwarded

  // Actions
  setReject(reason: string): void;
  forward(rcptTo: string, headers?: Headers): Promise<void>;
  reply(message: EmailMessage): Promise<void>;
}
```

| Property | Type | Description |
|----------|------|-------------|
| `message.from` | `string` | Sender's email address (SMTP envelope, trusted) |
| `message.to` | `string` | Recipient address the email was sent to |
| `message.headers` | `Headers` | Email headers — use `.get("subject")`, `.get("message-id")`, etc. |
| `message.raw` | `ReadableStream` | Raw email content (MIME format) — **single use** |
| `message.rawSize` | `number` | Size of the raw email in bytes |
| `message.canBeForwarded` | `boolean` | Whether the message can be forwarded |

**Envelope vs headers:** `message.from` is the SMTP envelope address — it's set by the sending mail server and is trustworthy for routing decisions. Header addresses (parsed from the email body) can be spoofed. Use envelope addresses for security decisions like allowlists.

## Core Operations

### Forward

Route the email to a verified destination address:

```typescript
await message.forward("team@company.com");
```

You can add custom headers when forwarding:

```typescript
await message.forward("team@company.com", new Headers({
  "X-Original-Recipient": message.to,
  "X-Forwarded-By": "email-worker",
}));
```

The destination address **must be verified** first. Add it via `npx wrangler email routing addresses create user@gmail.com` or in Dashboard > Email Routing > Destinations. Forwarding to an unverified address fails silently.

### Reject

Refuse the email with an SMTP error. The sender's mail server receives the rejection reason:

```typescript
message.setReject("Your message was blocked by our email policy");
```

Rejection happens at the SMTP level, so the sender gets a bounce notification. Use this for spam filtering or blocking known-bad senders.

### Reply

There are two ways to send replies:

**Option 1: Using `env.EMAIL.send()` (recommended)** — Uses the Email Sending binding directly. Simpler, no extra dependencies:

```typescript
async email(message, env, ctx) {
  const subject = message.headers.get("subject") || "";

  await env.EMAIL.send({
    to: message.from,
    from: message.to,  // Reply from the original recipient address
    subject: `Re: ${subject}`,
    html: "<h1>Thank you for your message</h1><p>We will respond shortly.</p>",
    text: "Thank you for your message. We will respond shortly.",
  });

  // Also forward to human team
  await message.forward("team@company.com");
}
```

**Option 2: Using `message.reply()` with MIME** — More control over the raw MIME message. Requires `mimetext`. Install it:

```bash
npm install mimetext
```

```typescript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

async email(message, env, ctx) {
  const msg = createMimeMessage();

  // Set threading headers so the reply appears in the same thread
  const messageId = message.headers.get("Message-ID");
  if (messageId) {
    msg.setHeader("In-Reply-To", messageId);
    msg.setHeader("References", messageId);
  }

  msg.setSender({ name: "Support", addr: "support@yourdomain.com" });
  msg.setRecipient(message.from);
  msg.setSubject("Re: " + (message.headers.get("subject") || "Your message"));

  msg.addMessage({
    contentType: "text/plain",
    data: "Thanks for reaching out! We received your message and will respond within 24 hours.",
  });
  msg.addMessage({
    contentType: "text/html",
    data: "<p>Thanks for reaching out! We received your message and will respond within 24 hours.</p>",
  });

  const reply = new EmailMessage(
    "support@yourdomain.com",
    message.from,
    msg.asRaw()
  );

  await message.reply(reply);
}
```

Add `"nodejs_compat"` to compatibility flags in wrangler.jsonc for `mimetext` to work:

```jsonc
{ "compatibility_flags": ["nodejs_compat"] }
```

## Parsing Emails

The `message.raw` stream contains the raw MIME content. Use [postal-mime](https://www.npmjs.com/package/postal-mime) to parse it into structured data.

```bash
npm install postal-mime
```

```typescript
import PostalMime from "postal-mime";

async email(message, env, ctx) {
  // Buffer the stream first — it can only be read once
  const rawBuffer = await new Response(message.raw).arrayBuffer();
  const parsed = await PostalMime.parse(rawBuffer);

  console.log("Subject:", parsed.subject);
  console.log("Text body:", parsed.text);
  console.log("HTML body:", parsed.html);
  console.log("Attachments:", parsed.attachments.length);

  // Process attachments
  for (const attachment of parsed.attachments) {
    console.log(`  ${attachment.filename} (${attachment.mimeType}, ${attachment.content.byteLength} bytes)`);
  }
}
```

### Parsed Email Shape

```typescript
{
  subject: string;
  from: { name?: string; address: string };
  to: { name?: string; address: string }[];
  cc?: { name?: string; address: string }[];
  text?: string;          // Plain text body
  html?: string;          // HTML body
  attachments: {
    filename: string;
    mimeType: string;
    content: ArrayBuffer;  // Raw attachment data
  }[];
}
```

For email content best practices (avoiding spam filters, proper structure), see [deliverability.md](deliverability.md).

## Combined Send + Receive

The real power of Cloudflare Email Service is combining Email Routing (inbound) with Email Sending (outbound) in a single Worker. Receive an email, process it, and reply — all without leaving the platform.

```typescript
export default {
  async email(message, env, ctx): Promise<void> {
    const rawBuffer = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(rawBuffer);

    // Send an auto-reply using the Email Sending binding
    await env.EMAIL.send({
      to: message.from,
      from: { email: "support@yourdomain.com", name: "Support" },
      subject: `Re: ${parsed.subject}`,
      html: `<p>Thanks for contacting us! Your ticket number is <strong>TK-${Date.now()}</strong>.</p>`,
      text: `Thanks for contacting us! Your ticket number is TK-${Date.now()}.`,
      headers: {
        "In-Reply-To": message.headers.get("Message-ID") || "",
      },
    });

    // Also forward to the team
    await message.forward("team@company.com");
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    return new Response("Email Service running");
  },
} satisfies ExportedHandler<Env>;
```

This requires both `send_email` binding (for sending) and a routing rule (for receiving) in your configuration.

## Integration Patterns

### Store Attachments in R2

```typescript
async email(message, env, ctx) {
  const rawBuffer = await new Response(message.raw).arrayBuffer();
  const parsed = await PostalMime.parse(rawBuffer);

  for (const attachment of parsed.attachments) {
    const key = `emails/${Date.now()}/${attachment.filename}`;
    await env.R2_BUCKET.put(key, attachment.content, {
      httpMetadata: { contentType: attachment.mimeType },
      customMetadata: { from: message.from, subject: parsed.subject },
    });
  }
}
```

### Classify with Workers AI

```typescript
async email(message, env, ctx) {
  const rawBuffer = await new Response(message.raw).arrayBuffer();
  const parsed = await PostalMime.parse(rawBuffer);

  const result = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
    messages: [{
      role: "user",
      content: `Classify this email into one of: support, billing, feedback, spam.
Subject: ${parsed.subject}
Body: ${parsed.text?.substring(0, 500)}`,
    }],
  });

  const category = result.response.toLowerCase();
  if (category.includes("spam")) {
    message.setReject("Classified as spam");
  } else {
    await message.forward("team@company.com");
  }
}
```

### Queue for Async Processing

For heavy processing, push to a Queue and handle offline:

```typescript
async email(message, env, ctx) {
  const rawBuffer = await new Response(message.raw).arrayBuffer();
  const parsed = await PostalMime.parse(rawBuffer);

  await env.EMAIL_QUEUE.send({
    from: message.from,
    to: message.to,
    subject: parsed.subject,
    text: parsed.text,
    receivedAt: new Date().toISOString(),
  });

  // The email is acknowledged — processing happens in the queue consumer
}
```

## Gotchas

### message.raw is single-use

The raw stream can only be read once. If you try to read it again, you get an empty result. Always buffer it first:

```typescript
// Buffer once, use many times
const rawBuffer = await new Response(message.raw).arrayBuffer();
const parsed = await PostalMime.parse(rawBuffer);
// rawBuffer can be used again (e.g., stored in R2)
```

### Destination addresses must be verified

`message.forward()` only works with verified destination addresses. Add them via `npx wrangler email routing addresses create user@gmail.com` or in the Dashboard before deploying your Worker.

### The email() handler must consume or forward the stream

If your handler returns without consuming `message.raw`, forwarding, or rejecting, the email is silently dropped. Always take an explicit action.

### DMARC/SPF for replies

If your Worker sends replies using `message.reply()` or the Email Sending binding, make sure your domain has proper SPF and DKIM records. Email Service auto-configures these when you onboard a domain, but if you're using Email Routing separately from Email Sending, verify the records are in place. See [deliverability.md](deliverability.md) for details on email authentication.

## Limits

| Limit | Value |
|-------|-------|
| Max message size | 25 MiB |
| Max routing rules per zone | 200 |
| Max verified destinations | 200 |
| CPU time (free Workers tier) | 10 ms |
| CPU time (paid Workers tier) | 30 s default, 5 min max |
| Max recipients for forward() | 1 verified address per call |
