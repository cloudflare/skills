# Cloudflare Tunnel API

Retrieve the current [Cloudflare Tunnel API documentation](https://developers.cloudflare.com/api/resources/zero_trust/subresources/tunnels/) before changing Tunnel resources.

## Authentication

Base URL: `https://api.cloudflare.com/client/v4`

Use an API token with Cloudflare Tunnel write access:

```http
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

Never print or persist connector tokens.

## TypeScript SDK

Install the current SDK:

```bash
npm install cloudflare
```

```typescript
import Cloudflare from 'cloudflare';

const cf = new Cloudflare({
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
});

const accountId = process.env.CLOUDFLARE_ACCOUNT_ID!;
```

Cloudflared tunnels are under `zeroTrust.tunnels.cloudflared`, not directly under `zeroTrust.tunnels`.

## Tunnel lifecycle

### Create a remotely managed tunnel

```http
POST /accounts/{account_id}/cfd_tunnel
```

```json
{
  "name": "my-tunnel",
  "config_src": "cloudflare"
}
```

```typescript
const tunnel = await cf.zeroTrust.tunnels.cloudflared.create({
  account_id: accountId,
  name: 'my-tunnel',
  config_src: 'cloudflare',
});
```

Use `config_src: "cloudflare"` for token-based, remotely managed tunnels. Use `config_src: "local"` and provide a base64-encoded `tunnel_secret` for locally managed tunnels.

### List tunnels

```http
GET /accounts/{account_id}/cfd_tunnel?is_deleted=false
```

```typescript
for await (const tunnel of cf.zeroTrust.tunnels.cloudflared.list({
  account_id: accountId,
  is_deleted: false,
})) {
  console.log(`${tunnel.name}: ${tunnel.id}`);
}
```

Useful response fields include `id`, `name`, `config_src`, `status`, `conns_active_at`, and `conns_inactive_at`.

### Get or delete a tunnel

```http
GET /accounts/{account_id}/cfd_tunnel/{tunnel_id}
DELETE /accounts/{account_id}/cfd_tunnel/{tunnel_id}
```

```typescript
const tunnel = await cf.zeroTrust.tunnels.cloudflared.get(tunnelId, {
  account_id: accountId,
});

await cf.zeroTrust.tunnels.cloudflared.delete(tunnelId, {
  account_id: accountId,
});
```

## Remote configuration

### Set ingress rules

```http
PUT /accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations
```

```json
{
  "config": {
    "ingress": [
      {
        "hostname": "app.example.com",
        "service": "http://origin:8000"
      },
      {
        "service": "http_status:404"
      }
    ]
  }
}
```

Always include a final catch-all ingress rule.

### Retrieve the connector token

```http
GET /accounts/{account_id}/cfd_tunnel/{tunnel_id}/token
```

```typescript
const token = await cf.zeroTrust.tunnels.cloudflared.token.get(tunnelId, {
  account_id: accountId,
});
```

The response is the secret connector token. Feed it directly into the target secret or configuration API without logging it.

Run the connector with the token:

```bash
cloudflared tunnel --no-autoupdate run --token "$TUNNEL_TOKEN"
```

## Public-hostname DNS

Public hostnames use proxied CNAME records pointing to `<tunnel_id>.cfargotunnel.com`. For a locally managed tunnel with `cert.pem` installed, create one with `cloudflared`:

```bash
cloudflared tunnel route dns my-tunnel app.example.com
```

Or use the DNS Records API:

```http
POST /zones/{zone_id}/dns_records
```

```json
{
  "type": "CNAME",
  "name": "app.example.com",
  "content": "<tunnel_id>.cfargotunnel.com",
  "proxied": true
}
```

When moving an existing hostname, update its current DNS record rather than creating a duplicate.

## Private-network routes

Private WARP routes use the account-level Teamnet API:

```http
GET /accounts/{account_id}/teamnet/routes
POST /accounts/{account_id}/teamnet/routes
PATCH /accounts/{account_id}/teamnet/routes/{route_id}
DELETE /accounts/{account_id}/teamnet/routes/{route_id}
```

Retrieve the current route schema before creating or modifying private routes.
