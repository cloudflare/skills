# Dedicated discovery Worker

Serve every well-known / discovery document from one small Worker bound to **more-specific routes**, so Cloudflare routes them before the main `example.com/*` worker and the main application is never modified.

## wrangler.toml

```toml
name = "site-agent-discovery"
main = "src/index.js"
compatibility_date = "2026-01-01"

routes = [
  { pattern = "example.com/.well-known/api-catalog",              zone_name = "example.com" },
  { pattern = "example.com/.well-known/agent-card.json",          zone_name = "example.com" },
  { pattern = "example.com/.well-known/mcp/server-card.json",     zone_name = "example.com" },
  { pattern = "example.com/.well-known/agent-skills/index.json",  zone_name = "example.com" },
  { pattern = "example.com/.well-known/oauth-authorization-server", zone_name = "example.com" },
  { pattern = "example.com/.well-known/oauth-protected-resource", zone_name = "example.com" },
  { pattern = "example.com/.well-known/security.txt",             zone_name = "example.com" },
  { pattern = "example.com/llms.txt",                             zone_name = "example.com" },
  { pattern = "example.com/robots.txt",                           zone_name = "example.com" },
  # repeat each for www. (and apex) so both hosts are covered
]
```

Add `www.` (and apex) variants of every route — scanners hit both, and per-host coverage avoids the origin-mismatch failure.

## src/index.js (shape)

```js
const json = (obj, ct = "application/json; charset=utf-8") =>
  new Response(JSON.stringify(obj, null, 2), {
    headers: { "content-type": ct, "cache-control": "public, max-age=3600", "access-control-allow-origin": "*" },
  });

// sha256 for the agent-skills index entries (computed at request time)
async function sha256hex(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(request) {
    const { pathname, origin } = new URL(request.url);          // origin = www OR apex → build docs per-request
    if (pathname === "/.well-known/api-catalog")
      return json(catalog(origin), 'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"');
    if (pathname === "/.well-known/agent-card.json")     return json(agentCard(origin));
    if (pathname === "/.well-known/mcp/server-card.json") return json(mcpCard(origin));
    if (pathname === "/.well-known/agent-skills/index.json") return json(await skills(origin));
    if (pathname === "/.well-known/oauth-protected-resource") return json(protectedResource(origin));
    if (pathname === "/.well-known/oauth-authorization-server") return json(authServer(origin));
    if (pathname === "/.well-known/security.txt") return new Response(securityTxt, { headers: { "content-type": "text/plain; charset=utf-8" } });
    if (pathname === "/llms.txt")  return new Response(llms, { headers: { "content-type": "text/plain; charset=utf-8" } });
    if (pathname === "/robots.txt") return new Response(robots(origin), { headers: { "content-type": "text/plain; charset=utf-8" } });
    return new Response("Not found", { status: 404 });
  },
};
```

Key points:
- Build `resource`/`issuer`/anchors from the **request origin** so `www` and apex both validate (no hardcoded host → no origin-mismatch failure).
- The API Catalog (RFC 9727) is an RFC 9264 **linkset**: `{ "linkset": [ { "anchor": "<origin>/", "service-desc": [{ href, type }], "related": [...] } ] }`.
- If `/llms.txt` or `/robots.txt` already exists in the (gated) main app, you can **proxy** it from the discovery worker with a pre-provisioned service key to un-gate it, instead of duplicating the content.

## Link header — Transform Rule (no worker)

```bash
curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE/rulesets/phases/http_response_headers_transform/entrypoint" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" --data '{
    "rules": [{
      "action": "rewrite",
      "action_parameters": { "headers": { "Link": { "operation": "set",
        "value": "</.well-known/api-catalog>; rel=\"api-catalog\", </.well-known/mcp/server-card.json>; rel=\"mcp-server\"" } } },
      "expression": "(http.host in {\"example.com\" \"www.example.com\"} and http.request.uri.path eq \"/\")",
      "description": "RFC 8288 Link header for agent discovery"
    }]
  }'
```

`PUT .../entrypoint` creates the phase ruleset if absent. GET it first and merge if other response-header rules already exist.

## Markdown for Agents (zone setting, no code)

```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE/settings/content_converter" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" --data '{"value":"on"}'
```
Requests with `Accept: text/markdown` then receive a markdown rendering; browsers still get HTML.
