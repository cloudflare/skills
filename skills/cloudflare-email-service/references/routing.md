# Receiving & Routing Inbound Email

Handle incoming emails sent to your domain via a Worker's `email()` handler. Forward, reply, reject, or parse emails programmatically.

For full API details, see the [Email Routing docs](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/).

## Email Handler

Export an `email()` function from your Worker. No special wrangler binding needed — a routing rule connects incoming addresses to your Worker.

```typescript
export default {
  async email(message, env, ctx): Promise<void> {
    console.log(`Email from ${message.from} to ${message.to}`);
    await message.forward("team@company.com");
  },
} satisfies ExportedHandler<Env>;
```

Set up routing rules in **Dashboard** > **Compute & AI** > **Email Service** > **Email Routing** > **Routing Rules**, or via `wrangler email routing rules create`.

## ForwardableEmailMessage Interface

```typescript
interface ForwardableEmailMessage {
  readonly from: string;           // Sender (envelope MAIL FROM)
  readonly to: string;             // Recipient (envelope RCPT TO)
  readonly headers: Headers;       // Email headers (.get("subject"), .get("message-id"))
  readonly raw: ReadableStream;    // Raw MIME content — single use
  readonly rawSize: number;        // Size in bytes
  readonly canBeForwarded: boolean;

  setReject(reason: string): void;
  forward(rcptTo: string, headers?: Headers): Promise<void>;
  reply(message: EmailMessage): Promise<void>;
}
```

`message.from` is the SMTP envelope address (trustworthy). Header addresses can be spoofed.

## Core Operations

### Forward

```typescript
await message.forward("team@company.com");

// With custom headers
await message.forward("team@company.com", new Headers({
  "X-Original-Recipient": message.to,
}));
```

Destination must be verified first (Dashboard or `wrangler email routing addresses create`).

### Reject

```typescript
message.setReject("Your message was blocked");
```

### Reply

Using `env.EMAIL.send()` (recommended — no extra dependencies):

```typescript
async email(message, env, ctx) {
  const subject = message.headers.get("subject") || "";
  await env.EMAIL.send({
    to: message.from,
    from: message.to,
    subject: `Re: ${subject}`,
    html: "<p>Thanks! We'll respond shortly.</p>",
    text: "Thanks! We'll respond shortly.",
  });
  await message.forward("team@company.com");
}
```

Using `message.reply()` with MIME (more control, requires `mimetext` + `nodejs_compat`):

```typescript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

async email(message, env, ctx) {
  const msg = createMimeMessage();
  const messageId = message.headers.get("Message-ID");
  if (messageId) msg.setHeader("In-Reply-To", messageId);
  msg.setSender({ name: "Support", addr: "support@yourdomain.com" });
  msg.setRecipient(message.from);
  msg.setSubject("Re: " + (message.headers.get("subject") || ""));
  msg.addMessage({ contentType: "text/plain", data: "Thanks for reaching out!" });

  await message.reply(new EmailMessage("support@yourdomain.com", message.from, msg.asRaw()));
}
```

## Parsing Emails

Use [postal-mime](https://www.npmjs.com/package/postal-mime) to parse raw MIME content:

```typescript
import PostalMime from "postal-mime";

async email(message, env, ctx) {
  const rawBuffer = await new Response(message.raw).arrayBuffer();
  const parsed = await PostalMime.parse(rawBuffer);

  console.log("Subject:", parsed.subject);
  console.log("Text:", parsed.text);
  console.log("Attachments:", parsed.attachments.length);
}
```

## Gotchas

- **`message.raw` is single-use.** Buffer first: `const raw = await new Response(message.raw).arrayBuffer()`
- **Destinations must be verified.** Forwarding to unverified addresses fails silently.
- **Handler must act.** If your handler returns without consuming raw, forwarding, or rejecting, the email is dropped.
- **DMARC/SPF for replies.** If sending replies, ensure your domain has proper SPF/DKIM records (auto-configured on domain onboarding).
