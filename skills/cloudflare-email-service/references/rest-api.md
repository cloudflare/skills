# Sending Emails — REST API

This reference covers sending emails via HTTP requests from applications not running on Cloudflare Workers. Cloudflare provides official SDKs for TypeScript, Python, and Go — the examples below use those languages plus curl.

If your app runs on Cloudflare Workers, use the [Workers binding](sending.md) instead. The binding is simpler (no API keys, no HTTP calls, no auth setup) and more performant (no network hop to the API). The REST API is the right choice when your backend runs elsewhere — a standalone Node.js server, a Django app, a Go microservice, etc.

## Table of Contents

- [Endpoint](#endpoint)
- [Authentication](#authentication)
- [Request Format](#request-format)
- [Language Examples](#language-examples)
- [Batch Sending](#batch-sending)
- [Attachments](#attachments)
- [Custom Headers](#custom-headers)
- [Error Handling](#error-handling)
- [Rate Limits & Retries](#rate-limits--retries)

## Endpoint

```
POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send
```

Replace `{account_id}` with your [Cloudflare account ID](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/). For the full OpenAPI specification, refer to the [Email Sending API reference](https://developers.cloudflare.com/api/resources/email_sending/methods/send).

## Authentication

Create a Cloudflare API token with permission to send emails:

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) > **My Profile** > **API Tokens**
2. Select **Create Token**
3. Choose a template or create a custom token with Email Service permissions
4. Copy the token — you won't see it again

Include it in every request:

```
Authorization: Bearer <API_TOKEN>
```

Store the token in an environment variable. Never hardcode tokens in source code — they get committed and leaked.

```bash
export CLOUDFLARE_API_TOKEN=your-token-here
export CLOUDFLARE_ACCOUNT_ID=your-account-id
```

## Request Format

```json
{
  "to": "user@example.com",
  "from": "welcome@yourdomain.com",
  "subject": "Welcome!",
  "html": "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
  "text": "Welcome! Thanks for signing up."
}
```

### Fields

**IMPORTANT:** The REST API uses different field names than the Workers binding in some cases.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to` | string or string[] | Yes | Recipient(s), max 50 combined with cc/bcc |
| `from` | string or `{address, name}` | Yes | Sender address — must be on an onboarded domain. **Uses `address` not `email` for object form** |
| `subject` | string | Yes | Email subject line |
| `html` | string | No* | HTML body |
| `text` | string | No* | Plain text body |
| `cc` | string or string[] | No | CC recipients |
| `bcc` | string or string[] | No | BCC recipients |
| `reply_to` | string or `{address, name}` | No | Reply-to address. **Uses snake_case `reply_to`**, not camelCase |
| `attachments` | array | No | File attachments (see [Attachments](#attachments)) |
| `headers` | object | No | Custom email headers (see [Custom Headers](#custom-headers)) |

*At least one of `html` or `text` is required. Include both for best deliverability — some email clients only display plain text.

**Key differences from Workers binding:**
- `from` object uses `address` key (REST) vs `email` key (Workers)
- `reply_to` snake_case (REST) vs `replyTo` camelCase (Workers)
- Errors use numeric codes (REST) vs string `E_*` codes (Workers)

### Success Response

A successful response returns the delivery status for each recipient:

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

- `delivered` — Email addresses to which the message was delivered immediately.
- `permanent_bounces` — Email addresses that permanently bounced.
- `queued` — Email addresses for which delivery was queued for later.

### Error Response

The REST API returns standard Cloudflare API error responses with **numeric error codes** (not the `E_*` string codes used by the Workers binding):

```json
{
  "success": false,
  "errors": [
    {
      "code": 1000,
      "message": "Sender domain not verified"
    }
  ],
  "messages": [],
  "result": null
}
```

## Language Examples

### curl

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "user@example.com",
    "from": "welcome@yourdomain.com",
    "subject": "Welcome!",
    "html": "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
    "text": "Welcome! Thanks for signing up."
  }'
```

With named sender and multiple recipients:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "to": ["user1@example.com", "user2@example.com"],
    "from": { "address": "newsletter@yourdomain.com", "name": "Newsletter Team" },
    "subject": "Monthly Newsletter",
    "html": "<h1>This month'\''s updates</h1>",
    "text": "This month'\''s updates"
  }'
```

With CC, BCC, and reply_to:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "customer@example.com",
    "cc": ["manager@company.com"],
    "bcc": ["archive@company.com"],
    "from": "orders@yourdomain.com",
    "reply_to": "support@yourdomain.com",
    "subject": "Order Confirmation #12345",
    "html": "<h1>Your order is confirmed</h1>",
    "text": "Your order is confirmed"
  }'
```

### Node.js (fetch)

```typescript
const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID;
const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;

async function sendEmail(to: string, subject: string, html: string, text: string) {
  const response = await fetch(
    `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/email/sending/send`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${API_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to,
        from: { address: "noreply@yourdomain.com", name: "My App" },
        subject,
        html,
        text,
      }),
    }
  );

  const data = await response.json();

  if (!data.success) {
    const err = data.errors?.[0];
    throw new Error(`Email failed: ${err?.code} - ${err?.message}`);
  }

  return data.result; // { delivered: [], permanent_bounces: [], queued: [] }
}
```

### Python (requests)

```python
import os
import requests

ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]

def send_email(to: str, subject: str, html: str, text: str) -> dict:
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/email/sending/send",
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "to": to,
            "from": {"address": "noreply@yourdomain.com", "name": "My App"},
            "subject": subject,
            "html": html,
            "text": text,
        },
    )

    data = response.json()
    if not data.get("success"):
        err = data.get("errors", [{}])[0]
        raise Exception(f"Email failed: {err.get('code')} - {err.get('message')}")

    return data["result"]  # { delivered: [], permanent_bounces: [], queued: [] }
```

### Go (net/http)

```go
package email

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type EmailRequest struct {
	To      string `json:"to"`
	From    From   `json:"from"`
	Subject string `json:"subject"`
	HTML    string `json:"html"`
	Text    string `json:"text"`
}

type From struct {
	Address string `json:"address"`
	Name    string `json:"name"`
}

type SendResult struct {
	Delivered       []string `json:"delivered"`
	PermanentBounces []string `json:"permanent_bounces"`
	Queued          []string `json:"queued"`
}

func SendEmail(to, subject, html, text string) (*SendResult, error) {
	accountID := os.Getenv("CLOUDFLARE_ACCOUNT_ID")
	apiToken := os.Getenv("CLOUDFLARE_API_TOKEN")

	body, err := json.Marshal(EmailRequest{
		To:      to,
		From:    From{Address: "noreply@yourdomain.com", Name: "My App"},
		Subject: subject,
		HTML:    html,
		Text:    text,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST",
		fmt.Sprintf("https://api.cloudflare.com/client/v4/accounts/%s/email/sending/send", accountID),
		bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+apiToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Success bool       `json:"success"`
		Result  SendResult `json:"result"`
		Errors  []struct {
			Code    int    `json:"code"`
			Message string `json:"message"`
		} `json:"errors"`
	}
	json.NewDecoder(resp.Body).Decode(&result)

	if !result.Success {
		return nil, fmt.Errorf("email failed: %d - %s", result.Errors[0].Code, result.Errors[0].Message)
	}
	return &result.Result, nil
}
```

The API is a standard REST endpoint — any language with an HTTP client can call it. For languages without examples above, use the curl example as a reference for the request/response format.

## Multiple Recipients

The REST API accepts arrays in the `to` field for multiple recipients on a single email (max 50 combined across to, cc, bcc). For sending different emails to different people, make separate API calls.

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "to": ["user1@example.com", "user2@example.com"],
    "from": {"address": "team@yourdomain.com", "name": "Team"},
    "subject": "Team Update",
    "html": "<h1>Team Update</h1><p>Here is this week'\''s update.</p>",
    "text": "Team Update - Here is this week'\''s update."
  }'
```

## Attachments

Include base64-encoded files in the `attachments` array:

```json
{
  "to": "customer@example.com",
  "from": "invoices@yourdomain.com",
  "subject": "Your Invoice",
  "html": "<h1>Invoice attached</h1>",
  "text": "Invoice attached",
  "attachments": [
    {
      "content": "JVBERi0xLjQKJeLjz9MK...",
      "filename": "invoice-12345.pdf",
      "type": "application/pdf",
      "disposition": "attachment"
    }
  ]
}
```

For inline images, use `"disposition": "inline"` and reference via `contentId` in HTML:

```json
{
  "html": "<img src=\"cid:logo\" alt=\"Logo\" />",
  "attachments": [
    {
      "content": "iVBORw0KGgo...",
      "filename": "logo.png",
      "type": "image/png",
      "disposition": "inline",
      "contentId": "logo"
    }
  ]
}
```

Total email size including attachments cannot exceed 25 MB.

## Custom Headers

```json
{
  "headers": {
    "In-Reply-To": "<original-message-id@yourdomain.com>",
    "References": "<original-message-id@yourdomain.com>",
    "List-Unsubscribe": "<https://yourdomain.com/unsubscribe?id=abc>",
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    "X-Custom-Tracking": "campaign-123"
  }
}
```

See the [Cloudflare docs headers reference](https://developers.cloudflare.com/email-service/reference/headers/) for the full list of allowed headers.

## Error Handling

The REST API returns standard Cloudflare API error responses with **numeric error codes** (not the `E_*` string codes used by the Workers binding). Refer to the [Workers API error codes table](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/#error-codes) for the string error codes.

### HTTP Status Codes

| Status | Meaning | Retry? |
|--------|---------|--------|
| 200 | Success | N/A |
| 400 | Bad request (validation error) | No — fix the request |
| 401 | Invalid API token | No — check your token |
| 403 | Forbidden (insufficient permissions) | No — check token permissions |
| 429 | Rate limited | Yes — exponential backoff |
| 500 | Server error | Yes — exponential backoff |

### Retry Strategy

Only retry on 429 and 500. Validation errors (400) won't succeed on retry — fix the request instead.

```typescript
async function sendWithRetry(payload: object, maxRetries = 3): Promise<object> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(
      `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/email/sending/send`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${API_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    if (response.ok) {
      const data = await response.json();
      return data.result; // { delivered, permanent_bounces, queued }
    }

    // Only retry rate limits and server errors
    if (response.status !== 429 && response.status !== 500) {
      const data = await response.json();
      throw new Error(`Email failed (${response.status}): ${JSON.stringify(data.errors)}`);
    }

    if (attempt < maxRetries) {
      await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
    }
  }
  throw new Error("Email failed after max retries");
}
```

## Custom Headers

Set custom headers for threading, list management, or tracking. Refer to the [email headers reference](https://developers.cloudflare.com/email-service/reference/headers/) for the full list of allowed headers.

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
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

## Rate Limits & Retries

Email Service enforces rate and daily sending limits. Exact limits depend on your plan and account standing. When you hit a limit, the API returns an error indicating rate limit or daily limit exceeded.

For high-volume transactional email, consider:
- Moving to a Workers-based architecture with the binding (better performance, no API key management)
- Using Cloudflare Queues to buffer emails and send at a controlled rate
- Contacting Cloudflare support for limit increases on paid plans
