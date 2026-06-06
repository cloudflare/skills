---
name: agent-ready
description: Make a Cloudflare-hosted site discoverable and usable by AI agents — publish the agent-discovery signals (RFC 8288 Link headers, RFC 9727 api-catalog, MCP Server Card, A2A Agent Card, agent-skills index, llms.txt, security.txt, AIPREF Content-Signal, Markdown for Agents, OAuth/OIDC discovery, and DNS-AID SVCB records + DNSSEC). Load when a user asks to "make my site agent-ready", "pass isitagentready", "add agent discovery", "publish an api-catalog / MCP server card / A2A agent card / llms.txt", "expose tools to agents (WebMCP)", or fix any of those signals on a site fronted by Cloudflare.
references:
  - dedicated-discovery-worker
  - dns-aid
  - troubleshooting
---

# Agent-ready skill

Turns "make my site discoverable to AI agents" into the concrete set of HTTP, DNS, and well-known signals that agent crawlers (e.g. isitagentready.com) and autonomous agents look for — implemented the Cloudflare-native way so you never have to redeploy or risk the main application.

You are the agent. Implement the signals the user is missing, then **verify each one over the wire** with `curl`/`dig` before reporting success. Most failures are not code bugs — they are routing, auth-gate, caching, or commit-email problems specific to how the site is served on Cloudflare. The "Gotchas" section is the most valuable part of this skill; read it before you touch anything.

## When to load this skill

Load when the user mentions any of:
- "agent-ready", "isitagentready", "agent discovery", "discoverable by agents"
- a specific signal: "Link header", "api-catalog", "MCP server card", "A2A agent card", "agent-skills index", "llms.txt", "security.txt", "Content-Signal", "Markdown for Agents", "OAuth discovery", "DNS-AID", "WebMCP"
- the site is behind Cloudflare (Workers, Pages, or just Cloudflare DNS/proxy)

## The signals (what to publish, and where)

| Signal | Path / location | Content-Type | Spec |
|--------|-----------------|--------------|------|
| Link headers | response header on `/` (all pages) | — | RFC 8288 |
| API Catalog | `/.well-known/api-catalog` | `application/linkset+json` | RFC 9727 / 9264 |
| MCP Server Card | `/.well-known/mcp/server-card.json` | `application/json` | SEP-1649 |
| A2A Agent Card | `/.well-known/agent-card.json` | `application/json` | a2a-protocol.org |
| Agent Skills index | `/.well-known/agent-skills/index.json` | `application/json` | agentskills.io v0.2.0 |
| llms.txt | `/llms.txt` | `text/plain` | llmstxt.org |
| security.txt | `/.well-known/security.txt` | `text/plain` | RFC 9116 |
| Content-Signal | `/robots.txt` (`Content-Signal:` line) | `text/plain` | AIPREF / contentsignals.org |
| Markdown for Agents | content-negotiated on every HTML page | `text/markdown` | Cloudflare zone setting |
| OAuth discovery | `/.well-known/oauth-authorization-server` + `/.well-known/oauth-protected-resource` | `application/json` | RFC 8414 / 9728 |
| DNS-AID | `_index._agents`, `_mcp._agents`, `_a2a._agents` SVCB records + DNSSEC | DNS | draft-mozleywilliams-dnsop-dnsaid + RFC 9460 |
| WebMCP | `navigator.modelContext.provideContext()` client JS | — | webmachinelearning.github.io/webmcp |

## Recommended architecture (read this first)

**Do NOT add these routes to the user's main application worker** unless that is the only option. On most real sites the main worker is large, gated behind auth middleware, or diverged from its git source — touching it is risky and slow. Instead:

1. **A dedicated "discovery" Worker on more-specific routes.** Serve every JSON/markdown well-known document from one small Worker bound to *specific* routes (`example.com/.well-known/api-catalog`, `.../agent-card.json`, `/llms.txt`, …). Cloudflare routes the most-specific match first, so these win over the main `example.com/*` worker and the main app is never modified. See `references/dedicated-discovery-worker.md`.
2. **Response headers via a Transform Rule, not code.** The homepage `Link` header is best set with a zone `http_response_headers_transform` rule — no worker, no redeploy, applies regardless of which worker serves the page.
3. **`Content-Signal` / `robots.txt`** can also be served from the discovery worker (more-specific `/robots.txt` route) so you don't redeploy the main app just to add one line.
4. **Markdown for Agents** is a native zone setting — flip it, no code: `PATCH /zones/{zone}/settings/content_converter {"value":"on"}`.
5. **DNS-AID** is DNS records + DNSSEC on the zone. See `references/dns-aid.md`.
6. **WebMCP** is the one signal that *must* live in the page's client JS (the main app), because it registers tools on `navigator.modelContext` at page load. Ship it as a small, feature-detected client component.

This split means ~11 of the 12 signals ship without ever redeploying the user's application.

## Flow

1. **Auth + scope.** You need a Cloudflare API token with the right scopes for what you'll touch: **Workers Scripts:Edit** (discovery worker), **Zone:Edit / Zone Settings:Edit** (Transform Rule, content_converter), **DNS:Edit** + **DNSSEC** (DNS-AID). `wrangler`'s OAuth token is usually `zone:read` only — get a real API token. Never write the token to a shared file or print it.
2. **Measure first.** Run `scripts/audit.sh <host>` (or curl each path) to see which signals already pass. Many "failures" reported by a scanner are stale — re-measure live before building.
3. **Build the missing signals** using the dedicated-worker + Transform-Rule approach. Author real content (don't ship empty arrays): the api-catalog should list the site's real APIs; the agent-skills index entries need a real `sha256` (compute it with `crypto.subtle` over the served document at request time).
4. **Verify every signal over the wire** — status code AND content-type AND a content sanity check. A `200 text/html` on a `.json` path means the route detached and fell through to the app (see Gotchas).
5. **DNSSEC** can be *enabled* at Cloudflare by you, but it only validates once the **DS record is published at the registrar** — which the user must do if the domain isn't registered at Cloudflare. Surface the DS record; don't claim DNSSEC is done while it's `pending`.
6. **Report** per-signal: live status + the one or two items that need the user (registrar DS, a mailbox for security.txt, a main-app deploy for WebMCP).

## Gotchas (hard-won — these are why your fix "isn't working")

- **A `.json` well-known path returns `200 text/html`** → your route detached and the request fell through to the main app, which served its gate/login HTML. Re-deploy the discovery worker to re-attach routes; confirm with `curl -sI` that the content-type is JSON. Discovery-worker routes can silently detach on some account/route changes — a redeploy is the idempotent fix.
- **A well-known path returns `307`/redirect** → it's hitting the main app's auth gate. Serve it from the discovery worker on a more-specific route, OR add the path to the app's public allowlist. Well-known URIs (RFC 8615) must be public.
- **`Link` header present in `curl` but the scanner says missing** → the scan was taken before your change (scanners cache), OR you used `rel=token` unquoted and the parser wants quotes. Prefer `rel="api-catalog"`. (When setting via a Transform Rule, escape the quotes in the JSON body, or the API rejects it.)
- **OAuth/oauth-protected-resource fails with "origin mismatch"** → the doc hardcodes one host but the scanner hit the other (`www` vs apex). Build `resource`/`issuer` per-request from the request origin so both hosts validate.
- **Edge-cached discovery docs read stale after an edit** → they're `Cache-Control: public, max-age=...`. Either wait out the TTL or purge cache (needs a token with **Cache Purge** scope).
- **DNS-AID records "found" but DNSSEC "not validated"** → DNSSEC is `pending` because the **DS record isn't at the registrar**. If the domain is registered at Cloudflare it auto-activates; otherwise the user must paste the DS at their registrar (e.g. Squarespace, GoDaddy).
- **Vercel/CI "No GitHub account matching commit author email" / "Deployment blocked"** → the *commit author email* isn't a verified email on a GitHub account — not a code error. Use a recognized author email (the account's verified email or the GitHub `noreply`), or add the email under GitHub → Settings → Emails.
- **WebMCP "no tools detected"** → it must be registered in client JS at page load and is a Chrome origin-trial API. Feature-detect `navigator.modelContext` and no-op where absent; it only "passes" in a browser that supports it.

## Things you must NOT do
- Don't gate the discovery documents behind auth — they must be publicly fetchable.
- Don't ship empty/placeholder catalogs or skills arrays just to make a scanner pass; advertise the site's real, reachable resources.
- Don't enable DNSSEC and report it "done" while status is `pending` and no DS is at the registrar.
- Don't modify the main application worker for header/well-known signals when a dedicated worker + Transform Rule will do it without a redeploy.
- Don't write API tokens to shared files or print them in output.
