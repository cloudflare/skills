---
name: sandbox-stable
description: Build or maintain Cloudflare Sandbox apps on the stable @cloudflare/sandbox package. Use sandbox-next for preview apps and sandbox-migrate-to-next for stable-to-preview migrations.
---

# Sandbox SDK — stable package

Isolated Linux environments on [Cloudflare Containers](https://developers.cloudflare.com/containers/index.md), driven from Workers.

**Prefer the main Sandbox docs and installed stable types over memory.** This skill is a gate, a contract, and a retrieval map—not a full manual.

This line is the **current stable** default npm package. The main [Sandbox documentation](https://developers.cloudflare.com/sandbox/index.md) describes it. Existing apps can stay here and keep shipping.

We recommend **new projects** on `@cloudflare/sandbox@next` with **`sandbox-next`**. When you can, plan a move with **`sandbox-migrate-to-next`** so you are ready when 1.0 becomes the stable release. Do not force that port unless the user asks.

## 1. Gate — confirm the package line

Before writing code, inspect the app:

| Check | Must match |
| ----- | ---------- |
| npm dependency | Default `@cloudflare/sandbox` (**not** `@next` / preview tags) |
| Container image | Matching **stable** image (not `cloudflare/sandbox:next`) |

| If you find… | Action |
| ------------ | ------ |
| `@cloudflare/sandbox@next` or a `next` image | **Stop.** Load **`sandbox-next`**. |
| User wants to port to 1.0 / `@next` | **Stop.** Load **`sandbox-migrate-to-next`**. Do not half-apply preview APIs on a stable package. |
| Only cleaning deprecated stable APIs | Stay here; use the [2026 deprecation guide](https://developers.cloudflare.com/sandbox/sdk/migrate/index.md). That is **not** a move to `@next`. |

Never mix a stable Worker package with an `@next` container image (or the reverse).

Skills install: [Agent setup](https://developers.cloudflare.com/agent-setup/index.md) · [cloudflare/skills](https://github.com/cloudflare/skills)

## 2. Contract — non-negotiables

- `await sandbox.exec(command)` takes a **command string** and resolves when the command **finishes**, with buffered `stdout` / `stderr` / `exitCode` (and related fields).
- Long-running and streaming work use the **stable** command APIs (`startProcess`, `execStream`, and related helpers)—not the `@next` single-handle model. Open the Commands docs; do not invent `@next` `output()` handles on stable.
- **Sessions** can preserve working directory and environment across commands (default session / `enableDefaultSession`, `createSession`). See Sessions docs when state must carry across calls.
- Interactive browser terminals often use **`sandbox.terminal(request)`** and session/xterm helpers on stable—not preview `createTerminal` unless the package is `@next`.
- Prefer **RPC** transport when using tunnels or large/binary streaming. HTTP/WebSocket transports are deprecated (cleanup guide below).
- Files, mounts, ports, tunnels, backups, lifecycle, and interpreter: use main docs for signatures; trust installed **stable** types.
- Non-secret config in sandbox env; live credentials in the Worker. Use outbound handlers when processes call external APIs.
- Production preview hostnames need wildcard DNS on a custom domain when using those URL patterns.
- Do **not** apply `@next` argv/`process.output()` APIs while the dependency is still stable.
- Self-deployed **bridge** stays on the stable package and image. [Bridge](https://developers.cloudflare.com/sandbox/sdk/bridge/index.md)

Minimal shape:

```ts
import { getSandbox, proxyToSandbox, Sandbox } from "@cloudflare/sandbox";

export { Sandbox };

const sandbox = getSandbox(env.Sandbox, "user-123");
const result = await sandbox.exec('python3 -c "print(2 + 2)"');
// result.stdout, result.exitCode, result.success
```

## 3. Retrieve — open the doc for the task

Fetch the page before implementing. Installed stable types win over guesses.

| You need to… | Open |
| ------------ | ---- |
| Orient | [Sandbox overview](https://developers.cloudflare.com/sandbox/index.md) |
| First Worker, template, Docker | [Get started](https://developers.cloudflare.com/sandbox/get-started/index.md) |
| `exec`, streaming, background processes | [Commands API](https://developers.cloudflare.com/sandbox/sdk/api/commands/index.md) · [Execute commands](https://developers.cloudflare.com/sandbox/sdk/guides/execute-commands/index.md) · [Background processes](https://developers.cloudflare.com/sandbox/sdk/guides/background-processes/index.md) · [Streaming output](https://developers.cloudflare.com/sandbox/sdk/guides/streaming-output/index.md) |
| Sessions / shell state across commands | [Sessions concept](https://developers.cloudflare.com/sandbox/sdk/concepts/sessions/index.md) · [Sessions API](https://developers.cloudflare.com/sandbox/sdk/api/sessions/index.md) |
| `getSandbox` options, sleep, destroy | [Lifecycle API](https://developers.cloudflare.com/sandbox/sdk/api/lifecycle/index.md) · [Sandbox options](https://developers.cloudflare.com/sandbox/sdk/configuration/sandbox-options/index.md) |
| Env vars | [Environment variables](https://developers.cloudflare.com/sandbox/sdk/configuration/environment-variables/index.md) |
| Files | [Files API](https://developers.cloudflare.com/sandbox/sdk/api/files/index.md) · [Manage files](https://developers.cloudflare.com/sandbox/sdk/guides/manage-files/index.md) · [File watching](https://developers.cloudflare.com/sandbox/sdk/api/file-watching/index.md) |
| Buckets / mounts | [Storage API](https://developers.cloudflare.com/sandbox/sdk/api/storage/index.md) · [Mount buckets](https://developers.cloudflare.com/sandbox/sdk/guides/mount-buckets/index.md) |
| Backups | [Backups API](https://developers.cloudflare.com/sandbox/sdk/api/backups/index.md) · [Backup and restore](https://developers.cloudflare.com/sandbox/sdk/guides/backup-restore/index.md) |
| Ports, preview URLs, expose | [Ports API](https://developers.cloudflare.com/sandbox/sdk/api/ports/index.md) · [Expose services](https://developers.cloudflare.com/sandbox/sdk/guides/expose-services/index.md) |
| Tunnels | [Tunnels API](https://developers.cloudflare.com/sandbox/sdk/api/tunnels/index.md) |
| Proxy / Workers connections | [Proxy requests](https://developers.cloudflare.com/sandbox/sdk/guides/proxy-requests/index.md) · [Workers connections](https://developers.cloudflare.com/sandbox/sdk/guides/workers-connections/index.md) |
| Browser / PTY terminal | [Terminal API](https://developers.cloudflare.com/sandbox/sdk/api/terminal/index.md) · [Terminal concept](https://developers.cloudflare.com/sandbox/sdk/concepts/terminal/index.md) · [Browser terminals](https://developers.cloudflare.com/sandbox/sdk/guides/browser-terminals/index.md) |
| Code interpreter | [Interpreter API](https://developers.cloudflare.com/sandbox/sdk/api/interpreter/index.md) · [Code execution](https://developers.cloudflare.com/sandbox/sdk/guides/code-execution/index.md) |
| Git in the sandbox | [Git workflows](https://developers.cloudflare.com/sandbox/sdk/guides/git-workflows/index.md) |
| Secrets / egress | [Outbound traffic](https://developers.cloudflare.com/sandbox/sdk/guides/outbound-traffic/index.md) |
| WebSockets | [WebSocket connections](https://developers.cloudflare.com/sandbox/sdk/guides/websocket-connections/index.md) |
| Docker-in-Docker | [Docker in Docker](https://developers.cloudflare.com/sandbox/sdk/guides/docker-in-docker/index.md) |
| Production deploy | [Production deployment](https://developers.cloudflare.com/sandbox/sdk/guides/preview-urls-custom-domain/index.md) |
| Containers concept | [Containers](https://developers.cloudflare.com/sandbox/sdk/concepts/containers/index.md) |
| How-to index | [Guides](https://developers.cloudflare.com/sandbox/sdk/guides/index.md) |
| API index | [API reference](https://developers.cloudflare.com/sandbox/sdk/api/index.md) |
| Deprecated APIs **while staying on stable** | [2026 deprecation guide](https://developers.cloudflare.com/sandbox/sdk/migrate/index.md) |
| Self-deployed bridge | [Bridge](https://developers.cloudflare.com/sandbox/sdk/bridge/index.md) · [Bridge HTTP API](https://developers.cloudflare.com/sandbox/sdk/bridge/http-api/index.md) |
| Examples (stable/`main`) | [examples on GitHub](https://github.com/cloudflare/sandbox-sdk/tree/main/examples) |
| New work on 1.0 preview | **`sandbox-next`** · [1.0 preview](https://developers.cloudflare.com/sandbox/index.md) |
| Port existing app to `@next` | **`sandbox-migrate-to-next`** · [Migrate](https://developers.cloudflare.com/sandbox/sdk/migrate/index.md) |

### Deprecated-API cleanup (stay on stable)

Update package + matching image first, then follow the guide. Typical search:

```sh
rg 'SANDBOX_TRANSPORT|transport:|exposePort\(|enableDefaultSession|execStream\(|readFileStream|writeFileStream'
```

This path does **not** switch you to `@next`.

## 4. Before you ship

- Worker package and container image on the **same stable** line  
- Typecheck against installed stable types  
- No live secrets in sandbox env  
- If using deprecated transports/helpers, finish or track [2026 deprecation](https://developers.cloudflare.com/sandbox/sdk/migrate/index.md) cleanup  
- When the team is ready for 1.0, use **`sandbox-migrate-to-next`**—do not force cutover unprompted  
