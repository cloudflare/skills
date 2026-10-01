# Email Workers Patterns

Fetch the workflow page, then adapt it to the application's routing and storage requirements.

| Task | Documentation |
| --- | --- |
| Route by recipient or subject, forward to multiple destinations, or reject | [Email handler actions](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md) |
| Parse MIME bodies and attachments | [Email handler parsing guidance](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md) |
| Filter incoming mail | [Spam filtering](https://developers.cloudflare.com/email-service/examples/email-routing/spam-filtering/index.md) |
| Reply within the incoming event with threading | [Reply requirements and examples](https://developers.cloudflare.com/email-service/api/route-emails/email-handler/index.md) |
| Archive metadata in KV or enqueue mail for later processing | [Email storage and processing](https://developers.cloudflare.com/email-service/examples/email-routing/email-storage/index.md) |
| Store raw mail or extracted attachment bytes in R2 | [R2 Workers API](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/index.md) |
| Notify a webhook or schedule work within the invocation lifetime | [Fetch](https://developers.cloudflare.com/workers/runtime-apis/fetch/index.md) and [execution context](https://developers.cloudflare.com/workers/runtime-apis/context/index.md) |
| Send a later response or new outbound attachment | [Sending Workers API](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/index.md) and [attachment examples](https://developers.cloudflare.com/email-service/examples/email-sending/email-attachments/index.md) |

Plan a single read of raw content when both parsing and storage need it. A queue consumer or later request sends through the outbound API because the original incoming email event is no longer available.
