# SMTP Submission

Use SMTP submission when an existing external app already speaks SMTP. For Workers, prefer the Email Service binding; for external HTTP automation, prefer the REST API.

## Settings

| Setting | Value |
| --- | --- |
| Host | `smtp.mx.cloudflare.net` |
| Port | `465` |
| TLS | Implicit TLS |
| AUTH | `PLAIN` or `LOGIN` |
| Username | `api_token` |
| Password | Cloudflare API token with `Email Sending:Edit` |

The API token can be account-owned or user-owned. Store it in a secret manager or environment variable, never in source code.

## Example

```bash
curl --ssl-reqd \
  --url "smtps://smtp.mx.cloudflare.net:465" \
  --user "api_token:<API_TOKEN>" \
  --mail-from "welcome@yourdomain.com" \
  --mail-rcpt "user@example.com" \
  --upload-file mail.txt
```

SMTP submissions use the same Email Service delivery pipeline as the REST API and Workers binding, including dashboard logs and domain authentication behavior. Retrieve current SMTP docs before relying on response codes, library-specific examples, or beta limitations.
