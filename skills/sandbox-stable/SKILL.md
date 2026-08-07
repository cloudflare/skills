---
name: sandbox-stable
description: Use when building or changing Cloudflare Sandbox apps on the current stable @cloudflare/sandbox package (default npm tag)—commands, sessions, files, ports, tunnels, bridge, or deprecated-API cleanup while staying on stable. Not for @cloudflare/sandbox@next (use sandbox-next) or for porting to 1.0 (use sandbox-migrate-to-next).
---

# Cloudflare Sandbox SDK (stable package)

Isolated Linux environments on [Cloudflare Containers](https://developers.cloudflare.com/containers/), driven from Workers.

This skill is the **current stable** line: default `@cloudflare/sandbox` (today’s published package) and a **matching** stable container image. The main [Sandbox documentation](https://developers.cloudflare.com/sandbox/) describes this package.

We recommend starting **new** projects on the [1.0 preview](https://developers.cloudflare.com/sandbox/1-0-preview/) (`@cloudflare/sandbox@next`) with **`sandbox-next`**. Existing apps can stay on stable and keep shipping. When you can, plan a move with **`sandbox-migrate-to-next`** so you are ready when 1.0 becomes the stable release.

Prefer stable docs and installed package types over memory. Do not apply `@next` API shapes here.

## Confirm the package line

Before writing code, check the app:

- Dependency is default `@cloudflare/sandbox` (**not** `@next` / preview tags), **and**
- Container image matches that stable line (not `cloudflare/sandbox:next`)

| If you find… | Do this |
| ------------ | ------- |
| `@cloudflare/sandbox@next` (or preview image) | Stop. Use **`sandbox-next`**. |
| User wants to **port** to 1.0 / `@next` | Stop. Use **`sandbox-migrate-to-next`**. Do not half-apply preview APIs while the package is still stable. |
| Only cleaning deprecated stable APIs | Stay on this skill + [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/). That is **not** a move to `@next`. |

Never mix a stable Worker package with an `@next` container image (or the reverse).

Install skills: [Agent setup](https://developers.cloudflare.com/agent-setup/) · [cloudflare/skills](https://github.com/cloudflare/skills).

## Retrieval

| Topic | URL |
| ----- | --- |
| Overview | https://developers.cloudflare.com/sandbox/ |
| Get started | https://developers.cloudflare.com/sandbox/get-started/ |
| Commands | https://developers.cloudflare.com/sandbox/api/commands/ |
| Sessions | https://developers.cloudflare.com/sandbox/concepts/sessions/ · https://developers.cloudflare.com/sandbox/api/sessions/ |
| Lifecycle / options | https://developers.cloudflare.com/sandbox/api/lifecycle/ · https://developers.cloudflare.com/sandbox/configuration/sandbox-options/ |
| Files | https://developers.cloudflare.com/sandbox/api/files/ |
| Ports / tunnels | https://developers.cloudflare.com/sandbox/api/ports/ · https://developers.cloudflare.com/sandbox/api/tunnels/ |
| Terminal | https://developers.cloudflare.com/sandbox/api/terminal/ · https://developers.cloudflare.com/sandbox/concepts/terminal/ |
| Code interpreter | https://developers.cloudflare.com/sandbox/api/interpreter/ · https://developers.cloudflare.com/sandbox/guides/code-execution/ |
| Environment | https://developers.cloudflare.com/sandbox/configuration/environment-variables/ |
| Bridge | https://developers.cloudflare.com/sandbox/bridge/ |
| Deprecated APIs (stay on stable) | https://developers.cloudflare.com/sandbox/guides/2026-deprecation/ |
| 1.0 preview (when ready to move) | https://developers.cloudflare.com/sandbox/1-0-preview/ |

Fetch the relevant page when implementing. Installed **stable** types win over guesses.

## Install

```bash
npm install @cloudflare/sandbox
docker info   # local container dev
```

Use a stable container image tag that matches your SDK release (see Dockerfile in the template / docs). Do not switch the image to `next` unless the Worker package moves too.

## Worker shape

```ts
import { getSandbox, proxyToSandbox, Sandbox } from "@cloudflare/sandbox";

export { Sandbox };

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const proxy = await proxyToSandbox(request, env);
    if (proxy) return proxy;

    const sandbox = getSandbox(env.Sandbox, "user-123");
    // Stable: exec takes a command string and resolves when the command finishes
    const result = await sandbox.exec('python3 -c "print(2 + 2)"');
    return Response.json({
      output: result.stdout,
      exitCode: result.exitCode,
      success: result.success,
    });
  },
};
```

See [Get started](https://developers.cloudflare.com/sandbox/get-started/) for wrangler / Dockerfile binding details.

## Core model (stable)

- `await sandbox.exec(command)` runs a **shell command string** and resolves when the command **finishes**, with buffered `stdout` / `stderr` / `exitCode`.
- Long-running or streaming work often uses **`startProcess`** / **`execStream`** (and related helpers) — not the `@next` single-handle model. Follow [Commands](https://developers.cloudflare.com/sandbox/api/commands/).
- **Sessions** can preserve working directory and env across commands (`createSession`, default session / `enableDefaultSession`). See [Sessions](https://developers.cloudflare.com/sandbox/concepts/sessions/).
- Interactive browser terminals often use **`sandbox.terminal(request)`** and related session/xterm helpers — [Terminal](https://developers.cloudflare.com/sandbox/api/terminal/).
- Code interpreter methods may live on `Sandbox` on stable — [Interpreter API](https://developers.cloudflare.com/sandbox/api/interpreter/).
- Files, mounts, ports, tunnels, backups, and lifecycle options: use main docs for signatures.
- Prefer **RPC** transport for tunnels and large/binary streaming. HTTP/WebSocket transports are deprecated — see cleanup below.
- Non-secret config in sandbox env; live credentials in the Worker. [Outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) when processes call external APIs.
- Production preview hostnames need wildcard DNS on a custom domain (`.workers.dev` is not enough for those patterns).

```ts
// Short command (stable)
const result = await sandbox.exec("node --version");
console.log(result.stdout, result.exitCode);

// Background-style work — use stable APIs from the Commands docs, e.g. startProcess
// const proc = await sandbox.startProcess("node server.js");
```

## Deprecated APIs while staying on stable

If the app still uses HTTP/WebSocket transport, default sessions you want off, `exposePort` where tunnels fit, or stream-only helpers, follow the checklist in the [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/). That cleanup **keeps** the stable package; it is not Sandbox SDK 1.0.

```sh
rg 'SANDBOX_TRANSPORT|transport:|exposePort\(|enableDefaultSession|execStream\(|readFileStream|writeFileStream'
```

Update package + matching image first, switch to RPC, then adjust ports/sessions/streaming per that guide.

## Bridge

Self-deployed Sandbox bridge stays on the **stable** package and image. Keep Worker, image, and clients on the same stable line. [Bridge](https://developers.cloudflare.com/sandbox/bridge/).

## When to upgrade

Stable remains published and supported for existing apps. When the team has time, move to `@cloudflare/sandbox@next` with **`sandbox-migrate-to-next`** and the [Migrate guide](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/). Do **not** force production cutover unless the user asked for it.

## Common mistakes

- Applying `@next` argv/`output()` handle APIs while the package is still stable
- Mixing stable Worker with `cloudflare/sandbox:next` image
- Treating “deprecated API cleanup” as “must move to `@next` today”
- Putting API keys in sandbox env
- Guessing APIs instead of stable docs + installed types
