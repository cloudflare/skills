# turnstile-siteverify (Worker template)

The managed siteverify Worker template that ships inside the [Turnstile Spin](https://developers.cloudflare.com/turnstile/spin/) skill. The Spin agent deploys this template into the user's Cloudflare account as the backend for `siteverify` token validation.

You are reading this either because the Spin skill copied it into your project directory, or because you navigated to `cloudflare/skills/skills/turnstile-spin/templates/worker/` directly.

## Manual deploy

If you have this directory on disk and want to deploy it yourself:

```sh
npm install

# Set your Turnstile secret as a Worker secret (never commit this).
npx wrangler secret put TURNSTILE_SECRET_KEY

# Deploy.
npx wrangler deploy
```

Wrangler prints the deployed URL. Point your frontend's form `action` (or `fetch` target) at it. Confirm the integration with a curl:

```sh
curl -sf https://<your-worker-url>/health
# {"ok":true,"version":"1.0.0"}
```

## Endpoints

| Method | Path           | Purpose                                                                |
| ------ | -------------- | ---------------------------------------------------------------------- |
| POST   | `/`            | Siteverify proxy. Accepts JSON or form-encoded body.                   |
| POST   | `/siteverify`  | Alias of `POST /`.                                                     |
| GET    | `/health`      | Health check. Returns `{"ok": true, "version": "..."}`.                |
| GET    | `/`            | Same as `/health`.                                                     |

### Request

JSON body:

```json
{
	"token": "TURNSTILE_TOKEN_FROM_WIDGET",
	"remoteip": "1.2.3.4",
	"idempotency_key": "optional-uuid"
}
```

Form-encoded body:

```
token=...&remoteip=1.2.3.4
```

`cf-turnstile-response` is accepted as an alias for `token` in both body types, so a `<form>` posting directly to the Worker works without any client-side JavaScript.

### Response

```json
{
	"success": true,
	"challenge_ts": "2026-05-29T12:00:00Z",
	"hostname": "example.com",
	"action": "turnstile-spin-v1",
	"error-codes": [],
	"_worker": {
		"duration_ms": 87,
		"worker_version": "1.0.0"
	}
}
```

On validation failure, `success` is `false` and `error-codes` lists the reasons. The HTTP status is `200` regardless of validation outcome (callers should check `response.success`). On Worker-level failures, the HTTP status reflects the error class (400 for bad input, 415 for unsupported content type, 500 for missing secret, 502/504 for upstream issues).

#### Error codes

| Code                       | Meaning                                                             |
| -------------------------- | ------------------------------------------------------------------- |
| `missing-input-secret`     | `TURNSTILE_SECRET_KEY` not set                                      |
| `invalid-input-secret`     | Secret rejected by upstream                                         |
| `missing-token`            | No token in the request body                                        |
| `invalid-input-response`   | Token rejected by upstream                                          |
| `timeout-or-duplicate`     | Token expired (>5min) or already validated                          |
| `invalid-content-type`     | Body content-type was not JSON or form-encoded                      |
| `upstream-unreachable`     | Could not reach `challenges.cloudflare.com`                         |
| `upstream-timeout`         | Upstream took longer than 5 seconds                                 |
| `hostname-mismatch`        | `EXPECTED_HOSTNAME` is set and the response hostname did not match  |
| `bad-request`              | Generic catch-all for malformed input                               |
| `internal-error`           | Unhandled error in the Worker                                       |

## Configuration

| Variable                | Type    | Default   | Purpose                                                             |
| ----------------------- | ------- | --------- | ------------------------------------------------------------------- |
| `TURNSTILE_SECRET_KEY`  | secret  | (required)| Widget secret. Set via `wrangler secret put TURNSTILE_SECRET_KEY`.  |
| `ALLOWED_ORIGIN`        | var     | `*`       | CORS allowed origin. Lock down to your customer-facing domain.      |
| `EXPECTED_HOSTNAME`     | var     | (unset)   | If set, reject siteverify responses where `hostname` differs.       |
| `LOG_LEVEL`             | var     | `info`    | One of `debug`, `info`, `warn`, `error`. Filters structured logs.   |

Set vars in `wrangler.toml` (`[vars]` block) or via `wrangler deploy --var KEY:value`. Secrets only via `wrangler secret put`.

## Frontend snippet

The minimum HTML that works against this Worker:

```html
<script
	src="https://challenges.cloudflare.com/turnstile/v0/api.js"
	async
	defer
></script>

<form action="https://YOUR_WORKER_URL/" method="POST">
	<input name="email" type="email" required />
	<div
		class="cf-turnstile"
		data-sitekey="YOUR_SITEKEY"
		data-action="turnstile-spin-v1"
	></div>
	<button type="submit">Submit</button>
</form>
```

The `data-action="turnstile-spin-v1"` attribute is the Spin telemetry marker. Cloudflare uses it to measure activation rates for Spin-deployed widgets. It is account-level and aggregate; no PII. See [the docs page](https://developers.cloudflare.com/turnstile/spin/#telemetry-marker).

For React, SvelteKit, Astro, Hugo, and other framework examples, see [`developers.cloudflare.com/turnstile/spin`](https://developers.cloudflare.com/turnstile/spin/#code-examples).

## Production hardening

After the first deploy, before pointing real traffic:

| Step                                                           | Why                                                                 |
| -------------------------------------------------------------- | ------------------------------------------------------------------- |
| Set `ALLOWED_ORIGIN` to your real domain in `wrangler.toml`    | Locks CORS so other sites cannot proxy through your Worker          |
| Set `EXPECTED_HOSTNAME` if your widget is single-domain        | Defends against cross-site token replay                             |
| Configure Workers Observability alerts on error rate > 1%      | Catches upstream outages or secret-misconfig events                 |
| Rotate `TURNSTILE_SECRET_KEY` periodically                     | Standard secret hygiene                                             |
| Add a [Workers rate limit](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/) if abuse warrants | Defends the Worker itself                       |

## Testing

```sh
npm test                   # unit tests, mocks fetch
npm run test:integration   # hits real siteverify with test secrets
npm run typecheck
npm run openapi:lint
```

Cloudflare's documented test secrets:

| Secret                                  | Behavior                                  |
| --------------------------------------- | ----------------------------------------- |
| `1x0000000000000000000000000000000AA`   | Always succeeds                           |
| `2x0000000000000000000000000000000AA`   | Always fails                              |
| `3x0000000000000000000000000000000AA`   | Returns `timeout-or-duplicate`            |

## Project layout

```
src/
├── index.ts          # Fetch handler, routing, CORS, body parsing
├── validate.ts       # siteverify call with retry + timeout
├── observability.ts  # Structured log emission
├── errors.ts         # SiteverifyError + response shaping
└── types.ts          # Request/response types, error codes
test/
├── unit.test.ts          # Mocked siteverify
├── integration.test.ts   # Real network, test secrets
├── deploy.test.ts        # Deploy-to-clean-account speed assertion
└── validation.test.ts    # Validation surface (health, hostname, structured errors)
public/
└── post-deploy.html  # Post-deploy form for the Deploy button path
openapi.yaml          # OpenAPI 3.1 spec
wrangler.toml         # Worker config
```

## Contributing

Two rules:

1. Keep the request/response contract stable. Customers will deploy this Worker as-is.
2. Do not add features that require additional secrets or external services. The point is "drop in, set one secret, you are done."

PRs welcome.

## License

MIT. See [LICENSE](./LICENSE).

## Related

- [Turnstile Spin docs](https://developers.cloudflare.com/turnstile/spin/): the canonical setup flow
- [Cloudflare Turnstile docs](https://developers.cloudflare.com/turnstile/): product overview
- [Server-side validation reference](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/): siteverify API
- [Cloudflare Skills repo](https://github.com/cloudflare/skills): agent skill bundles including `turnstile-spin/`
- [Pages Plugin for Turnstile](https://developers.cloudflare.com/pages/functions/plugins/turnstile/): for sites hosted on Cloudflare Pages
