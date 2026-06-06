# Troubleshooting agent-discovery signals

Symptom → cause → fix. Most "it's not working" cases are routing/auth/cache/identity, not content.

| Symptom | Cause | Fix |
|---|---|---|
| `.json` well-known path returns **`200 text/html`** | route detached → request fell through to the main app, which served gate/login HTML | redeploy the discovery worker (idempotent — re-attaches routes); confirm `content-type` is JSON via `curl -sI` |
| well-known path returns **`307`/redirect** | hitting the main app's auth gate | serve it from the discovery worker (more-specific route) or add the path to the app's public allowlist; RFC 8615 well-known URIs must be public |
| `Link` header in `curl` but scanner says **missing** | scanner result is cached/pre-change, or unquoted `rel=token` not parsed | re-scan; use `rel="api-catalog"` (quoted). In a Transform Rule JSON body, escape the quotes or the API 400s |
| OAuth doc fails **"origin mismatch"** | doc hardcodes one host; scanner hit the other (`www` vs apex) | build `resource`/`issuer`/anchors from the request origin so both hosts validate |
| edited discovery doc still **reads stale** | `Cache-Control: public, max-age=…` at the edge | wait out TTL, or purge cache (token needs **Cache Purge** scope) |
| DNS-AID **"records found, DNSSEC not validated"** | DNSSEC `pending` — DS not at registrar | publish the DS at the registrar (auto if domain is on Cloudflare Registrar) |
| CI/Vercel **"No GitHub account matching commit author email"** / "Deployment blocked" | commit *author email* isn't verified on a GitHub account — not a code error | use a recognized author email, or add the email under GitHub → Settings → Emails. Note: squash-merge to the default branch usually re-authors to the account email, so the block often only affects *branch preview* builds |
| **WebMCP** "no tools detected" | must register in client JS at page load; Chrome origin-trial API | feature-detect `navigator.modelContext`, register on mount, no-op where absent |
| api-catalog/agent-skills "**returned HTML**" | same as the `307`/detached cases above | route through the discovery worker; verify JSON content-type |

## Token scopes by task

| Task | Required Cloudflare API token scope |
|---|---|
| Deploy discovery worker | Account → Workers Scripts:Edit |
| Link Transform Rule | Zone → Zone:Edit (rulesets) |
| Markdown for Agents (`content_converter`) | Zone → Zone Settings:Edit |
| DNS-AID records | Zone → DNS:Edit |
| Enable DNSSEC | Zone → DNS:Edit (DNSSEC) |
| Purge stale discovery docs | Zone → Cache Purge:Purge |

`wrangler`'s OAuth login is typically `zone:read` only — insufficient for the writes above. Create a scoped API token and pass it as `CLOUDFLARE_API_TOKEN`. Never write it to a shared file or print it.
