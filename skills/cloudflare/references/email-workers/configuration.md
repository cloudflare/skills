# Email Workers Configuration

An incoming routing rule connects an address to a Worker. Add an outbound sending binding when the application needs the sending API.

| Task | Documentation |
| --- | --- |
| Create, deploy, and connect an email-processing Worker | [Route emails](https://developers.cloudflare.com/email-service/get-started/route-emails/index.md) |
| Verify destinations, configure rules, or check DNS | [Email Routing configuration](../email-routing/configuration.md) |
| Configure outbound sending and address restrictions | [Sending Workers API](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/index.md) and [send bindings](https://developers.cloudflare.com/email-service/configuration/send-bindings/index.md) |
| Simulate incoming messages | [Local routing development](https://developers.cloudflare.com/email-service/local-development/routing/index.md) |
| Test outbound messages and attachment behavior | [Local sending development](https://developers.cloudflare.com/email-service/local-development/sending/index.md) |
| Configure KV, R2, D1, variables, or environments | [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md) |
| Generate runtime and binding types | [Workers TypeScript](https://developers.cloudflare.com/workers/languages/typescript/index.md) |
| Store credentials | [Workers secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |

Follow the handler docs for MIME library requirements. Local sending simulation and remote sending have different effects: remote bindings deliver real email.
