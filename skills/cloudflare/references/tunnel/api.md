# Tunnel API

## Cloudflare API Access

**Base URL**: `https://api.cloudflare.com/client/v4`

**Authentication**:
```bash
Authorization: Bearer ${CF_API_TOKEN}
```

## TypeScript SDK

Install: `npm install cloudflare`

```typescript
import Cloudflare from 'cloudflare';

const cf = new Cloudflare({
  apiToken: process.env.CF_API_TOKEN,
});

const accountId = process.env.CF_ACCOUNT_ID;
```

## Create Tunnel

### cURL
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "my-tunnel",
    "tunnel_secret": "<base64-secret>"
  }'
```

### TypeScript
```typescript
const tunnel = await cf.zeroTrust.tunnels.cloudflared.create({
  account_id: accountId,
  name: 'my-tunnel',
  tunnel_secret: Buffer.from(crypto.randomBytes(32)).toString('base64'),
});

console.log(`Tunnel ID: ${tunnel.id}`);
```

## List Tunnels

### cURL
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

### TypeScript
```typescript
for await (const tunnel of cf.zeroTrust.tunnels.cloudflared.list({
  account_id: accountId,
})) {
  console.log(`${tunnel.name}: ${tunnel.id}`);
}
```

## Get Tunnel Info

### cURL
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

### TypeScript
```typescript
const tunnel = await cf.zeroTrust.tunnels.cloudflared.get(tunnelId, {
  account_id: accountId,
});

console.log(`Status: ${tunnel.status}`);
console.log(`Connections: ${tunnel.connections?.length || 0}`);
```

## Update Tunnel Config

### cURL
```bash
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "config": {
      "ingress": [
        {"hostname": "app.example.com", "service": "http://localhost:8000"},
        {"service": "http_status:404"}
      ]
    }
  }'
```

### TypeScript
```typescript
const config = await cf.zeroTrust.tunnels.cloudflared.configurations.update(
  tunnelId,
  {
    account_id: accountId,
    config: {
      ingress: [
        { hostname: 'app.example.com', service: 'http://localhost:8000' },
        { service: 'http_status:404' },
      ],
    },
  }
);
```

## Delete Tunnel

### cURL
```bash
curl -X DELETE "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

### TypeScript
```typescript
await cf.zeroTrust.tunnels.cloudflared.delete(tunnelId, {
  account_id: accountId,
});
```

## Token-Based Tunnels (Config Source: Cloudflare)

Token-based tunnels store config in Cloudflare dashboard instead of local files.

### Via Dashboard
1. **Zero Trust** > **Networks** > **Tunnels**
2. **Create a tunnel** > **Cloudflared**
3. Configure routes in dashboard
4. Copy token
5. Run on origin:
```bash
cloudflared service install <TOKEN>
```

### Via Token
```bash
# Run with token (no config file needed)
cloudflared tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}

# Docker
docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
```

### Get Tunnel Token (TypeScript)
```typescript
const token = await cf.zeroTrust.tunnels.cloudflared.token.get(tunnelId, {
  account_id: accountId,
});
```

## DNS Routes API

Public hostnames use proxied CNAME records pointing to `<tunnel_id>.cfargotunnel.com`.

```bash
# Create DNS route
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "app.example.com",
    "content": "<tunnel_id>.cfargotunnel.com",
    "proxied": true
  }'

# Delete route
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

## Private Network Routes API

```bash
# Add IP route
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/teamnet/routes" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "network": "10.0.0.0/8",
    "tunnel_id": "<tunnel_id>"
  }'

# List IP routes
curl -X GET "https://api.cloudflare.com/client/v4/accounts/{account_id}/teamnet/routes" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```
