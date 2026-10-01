# Email Workers Troubleshooting

| Symptom or decision | Documentation |
| --- | --- |
| Raw stream already consumed or locked | [ReadableStream](https://developers.cloudflare.com/workers/runtime-apis/streams/readablestream/index.md) and [handler parsing guidance](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md) |
| Forwarding or reply exception; unsupported forwarding headers | [Email handler actions and requirements](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md) |
| Unverified destination or disabled rule | [Routing rules and addresses](https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/index.md) |
| Sender identity or authentication failure | [Email authentication](https://developers.cloudflare.com/email-service/concepts/email-authentication/index.md) and [troubleshooting](https://developers.cloudflare.com/email-service/reference/troubleshooting/index.md) |
| Sending validation, attachment, or recipient error | [Sending API errors](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/index.md) |
| Local test or binary attachment issue | [Local routing](https://developers.cloudflare.com/email-service/local-development/routing/index.md) and [local sending](https://developers.cloudflare.com/email-service/local-development/sending/index.md) |
| CPU, memory, message-size, or reply limits | [Email limits](https://developers.cloudflare.com/email-service/platform/limits/index.md) and [Workers limits](https://developers.cloudflare.com/workers/platform/limits/index.md) |
| Background work or unhandled error | [Execution context](https://developers.cloudflare.com/workers/runtime-apis/context/index.md) and [Workers logs](https://developers.cloudflare.com/workers/observability/logs/index.md) |
| Mail accepted but missing at the destination | [Email activity logs](https://developers.cloudflare.com/email-service/observability/logs/index.md) |

Raw content is single-use: reuse buffered content if multiple operations need it, and account for memory limits. `waitUntil()` extends execution lifetime; it does not remove CPU or memory limits. Diagnose reply failures against the incoming message's requirements, not just the sending domain's DNS.
