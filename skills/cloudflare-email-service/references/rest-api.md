# Sending Emails — REST API

Send emails via HTTP requests from any application. If your app runs on Cloudflare Workers, use the [Workers binding](sending.md) instead — simpler and more performant.

For the full OpenAPI specification, refer to the [Email Sending API reference](https://developers.cloudflare.com/api/resources/email_sending/methods/send).

## Endpoint

```
POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send
```

## Authentication

Authenticate with a [Cloudflare API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) that has email sending permission:

```
Authorization: Bearer <API_TOKEN>
```

## Request Fields

**IMPORTANT:** The REST API uses different field names than the Workers binding in some cases.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to` | string or string[] | Yes | Recipient(s), max 50 combined with cc/bcc |
| `from` | string or `{address, name}` | Yes | Sender — **uses `address` not `email`** for object form |
| `subject` | string | Yes | Email subject line |
| `html` | string | No* | HTML body |
| `text` | string | No* | Plain text body |
| `cc` | string or string[] | No | CC recipients |
| `bcc` | string or string[] | No | BCC recipients |
| `reply_to` | string or `{address, name}` | No | **Snake_case**, not camelCase |
| `attachments` | array | No | File attachments and inline images |
| `headers` | object | No | Custom email headers |

*At least one of `html` or `text` required. Include both for best deliverability.

**Key differences from Workers binding:** `from` uses `address` (REST) vs `email` (Workers), `reply_to` (REST) vs `replyTo` (Workers), `content_id` (REST) vs `contentId` (Workers) for inline attachments, errors use numeric codes (REST) vs string `E_*` codes (Workers), and responses return delivery status (`delivered`/`permanent_bounces`/`queued`) instead of just `messageId`.

## Examples

Simple send:

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

Multiple recipients with CC/BCC:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "to": ["user1@example.com", "user2@example.com"],
    "cc": ["manager@company.com"],
    "bcc": ["archive@company.com"],
    "from": { "address": "orders@yourdomain.com", "name": "Orders" },
    "reply_to": "support@yourdomain.com",
    "subject": "Order Confirmation",
    "html": "<h1>Your order is confirmed</h1>",
    "text": "Your order is confirmed"
  }'
```

With attachments:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "customer@example.com",
    "from": "invoices@yourdomain.com",
    "subject": "Your Invoice",
    "html": "<h1>Invoice attached</h1>",
    "attachments": [
      {
        "content": "JVBERi0xLjQKJeLjz9MK...",
        "filename": "invoice.pdf",
        "type": "application/pdf",
        "disposition": "attachment"
      }
    ]
  }'
```

With inline images (embedded via `cid:` URI):

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "user@example.com",
    "from": "newsletter@yourdomain.com",
    "subject": "Check this out",
    "html": "<h1>Hello!</h1><img src=\"cid:logo\">",
    "attachments": [
      {
        "content": "iVBORw0KGgoAAAANSUhEUg...",
        "filename": "logo.png",
        "type": "image/png",
        "disposition": "inline",
        "content_id": "logo"
      }
    ]
  }'
```

Attachment fields differ by type:
- **Regular attachment**: `content` (base64), `filename`, `type` (MIME), `disposition: "attachment"`
- **Inline image**: `content` (base64), `filename`, `type` (MIME), `disposition: "inline"`, `content_id` (referenced in HTML as `cid:<content_id>`)

With custom headers:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "user@example.com",
    "from": "notifications@yourdomain.com",
    "subject": "Your weekly digest",
    "html": "<h1>Weekly Digest</h1>",
    "headers": {
      "List-Unsubscribe": "<https://yourdomain.com/unsubscribe?id=abc123>",
      "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
      "X-Campaign-ID": "weekly-digest-2026-03"
    }
  }'
```

See the [email headers reference](https://developers.cloudflare.com/email-service/reference/headers/) for the full list of allowed headers.

## Response

Success:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "delivered": ["recipient@example.com"],
    "permanent_bounces": [],
    "queued": []
  }
}
```

Error (numeric codes, not `E_*` string codes like Workers):

```json
{
  "success": false,
  "errors": [{ "code": 1000, "message": "Sender domain not verified" }],
  "result": null
}
```

## Error Handling

| Status | Meaning | Retry? |
|--------|---------|--------|
| 200 | Success | N/A |
| 400 | Validation error | No — fix the request |
| 401 | Invalid API token | No — check your token |
| 429 | Rate limited | Yes — exponential backoff |
| 500 | Server error | Yes — exponential backoff |

Only retry on 429 and 500. Validation errors (400) won't succeed on retry.
