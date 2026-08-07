---
name: sandbox-2026-deprecation
description: Use when cleaning up a Cloudflare Sandbox SDK app that stays on the current stable package—HTTP/WebSocket transports, exposePort, default sessions, stream-specific helpers, or other APIs deprecated on stable. Not for full migration to @next (use sandbox-v1-migration).
---

# Sandbox SDK stable deprecation cleanup

For apps that **remain on the current stable** `@cloudflare/sandbox` package and must leave deprecated features. Installed via [cloudflare/skills](https://github.com/cloudflare/skills) / [Agent setup](https://developers.cloudflare.com/agent-setup/).

**Not** the path to Sandbox SDK 1.0. For `@cloudflare/sandbox@next`, use **`sandbox-v1-migration`**.

**Docs:** [Deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) · [Changelog](https://developers.cloudflare.com/changelog/sandbox/2026-06-09-deprecating-sandbox-sdk-features/)

## Checklist

1. Update `@cloudflare/sandbox` and the matching container image before changing runtime config.
2. Search:

   ```sh
   rg 'SANDBOX_TRANSPORT|transport:|exposePort\(|enableDefaultSession|execStream\(|readFileStream|writeFileStream'
   ```

3. Switch every sandbox to **RPC** (`SANDBOX_TRANSPORT=rpc` or `getSandbox(..., { transport: "rpc" })`).
4. Replace `exposePort()` with `sandbox.tunnels.get()` when tunnels fit. Keep `exposePort` + `proxyToSandbox` if the Worker must authenticate or rewrite responses.
5. Set `enableDefaultSession: false` (requires SDK **0.10.3+**). Use explicit `createSession()` when shell state must persist across commands on stable.
6. Move stream-specific file/command helpers to base `readFile` / `writeFile` / `exec` where streaming is supported (often needs RPC).
7. Desktop demo APIs are removed on recent stable lines—do not restore them; rebuild in-sandbox computer-use only if the product still needs it.
8. Deploy and smoke-test commands, files, public URLs, and any remaining explicit sessions.

## Replacements

| Deprecated | Replacement |
| ---------- | ----------- |
| HTTP / WebSocket transport | RPC |
| `exposePort()` (typical public URL) | `sandbox.tunnels.get()` |
| Default sessions | `enableDefaultSession: false` + explicit sessions or per-command `cwd`/`env` |
| Stream-only helpers | Base APIs with streaming support |

## Notes

- Tunnels and large/binary streaming expect RPC—configure transport first.
- If `cd` must carry across `exec` on **stable**, use an explicit session with `cwd` (stable-only; gone on `@next`).
- After this cleanup, plan **`sandbox-v1-migration`** when moving to 1.0.
