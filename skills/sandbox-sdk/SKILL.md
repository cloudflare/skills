---
name: sandbox-sdk
description: Build apps with Cloudflare Sandbox SDK for secure code execution. Use for new sandboxes, AI code execution, interpreters, CI-like jobs, and interactive environments. Prefer @cloudflare/sandbox@next (Sandbox SDK 1.0 preview) for new work. Load sandbox-v1-migration when moving a stable app to @next; load sandbox-2026-deprecation for stable-only cleanup of transports, exposePort, and default sessions.
---

# Cloudflare Sandbox SDK

Isolated Linux environments on [Cloudflare Containers](https://developers.cloudflare.com/containers/), driven from Workers.

## Choose the right track

| Situation | Package | Skill / docs |
| --------- | ------- | ------------ |
| **New project** | `@cloudflare/sandbox@next` | This skill + [1.0 preview](https://developers.cloudflare.com/sandbox/1-0-preview/) |
| **Migrate stable → 1.0** | `@next` | **`sandbox-v1-migration`** + [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) |
| **Stay on stable; remove deprecated APIs** | current stable | **`sandbox-2026-deprecation`** + [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) |
| **Stable-only maintenance** | current stable | [Main Sandbox docs](https://developers.cloudflare.com/sandbox/) |

Do not mix a preview Worker package with a stable container image (or the reverse).

**Agent setup (install these skills):** [Agent setup](https://developers.cloudflare.com/agent-setup/) · [cloudflare/skills](https://github.com/cloudflare/skills)

## Retrieval (prefer docs over memory)

| Topic | URL |
| ----- | --- |
| 1.0 overview | https://developers.cloudflare.com/sandbox/1-0-preview/ |
| Get started (`@next`) | https://developers.cloudflare.com/sandbox/1-0-preview/get-started/ |
| Processes | https://developers.cloudflare.com/sandbox/1-0-preview/processes/ |
| Process API | https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/ |
| Terminals | https://developers.cloudflare.com/sandbox/1-0-preview/terminals/ |
| Errors | https://developers.cloudflare.com/sandbox/1-0-preview/errors/ |
| Environment | https://developers.cloudflare.com/sandbox/1-0-preview/environment/ |
| Interpreter | https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/ |
| Examples | https://github.com/cloudflare/sandbox-sdk/tree/next/examples |
| Stable docs | https://developers.cloudflare.com/sandbox/ |

Fetch the relevant page when implementing. Installed `@next` types win over guesses.

## Install (`@next`)

```bash
npm install @cloudflare/sandbox@next
docker info   # required for local container dev
```

Container image must match the Worker line, for example `cloudflare/sandbox:next` (Python interpreter: `next-python` variant).

## Required Worker shape

Re-export `Sandbox` and bind the Durable Object / container in wrangler (see preview get-started). Minimal Worker:

```ts
import { getSandbox, proxyToSandbox, Sandbox } from "@cloudflare/sandbox";

export { Sandbox };

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const proxy = await proxyToSandbox(request, env);
    if (proxy) return proxy;

    const sandbox = getSandbox(env.Sandbox, "user-123");
    const process = await sandbox.exec(["python3", "-c", "print(2 + 2)"]);
    const output = await process.output({ encoding: "utf8" });
    return Response.json({
      stdout: output.stdout,
      exitCode: output.exitCode,
    });
  },
};
```

## Core model (`@next`)

- `exec(argv)` takes an **argv array**, resolves when the process **starts**, returns a **handle**.
- Collect results with `output()`, `logs()`, `waitForExit()`, `waitForPort()`, `waitForLog()`, `kill(signal?)`.
- No implicit shell and no shell-escaping of argv. Shell syntax needs e.g. `["/bin/bash", "-lc", script]`.
- No hidden sessions: `cd` / `export` in one process do not affect the next. Pass `cwd` / `env` per launch or one shell script.
- Process handles have **no stdin**. Interactive PTY → `createTerminal` + `connect`.
- Local wait `timeout` / `AbortSignal` cancel the wait only — they do not kill the process.
- `getProcess` / `listProcesses` do not start a container; they return `null` / `[]` when none is up.
- Process IDs are per **current container**, not forever for a sandbox ID. Store the job to relaunch after stop/replace.

### Short command

```ts
const process = await sandbox.exec(["node", "--version"]);
const result = await process.output({ encoding: "utf8" });
// result.stdout, result.exitCode, result.truncated, ...
```

### Long-running + readiness

```ts
const server = await sandbox.exec(["/bin/bash", "-lc", "npm run dev"], {
  cwd: "/workspace/app",
});
await server.waitForPort(3000, { timeout: 60_000 }); // default mode: tcp
const stream = await server.logs({ follow: true, replay: true });
await server.kill(); // numeric signal, default 15
```

### Interpreter (extension)

```ts
import { Sandbox as BaseSandbox } from "@cloudflare/sandbox";
import { withInterpreter } from "@cloudflare/sandbox/interpreter";

export class Sandbox extends BaseSandbox<Env> {
  interpreter = withInterpreter(this);
}

const ctx = await sandbox.interpreter.createCodeContext({ language: "python" });
const result = await sandbox.interpreter.runCode("print(1+1)", { context: ctx });
```

Python needs the **`-python`** image variant.

### Terminals

```ts
const terminal = await sandbox.createTerminal({ command: ["bash"] });
// WebSocket upgrade:
const t = await sandbox.getTerminal(terminal.id);
if (t) return t.connect(request, { cursor });
```

### Files, mounts, ports, tunnels

Still on the sandbox. Prefer main docs for signatures; ignore stable-only session/transport/`sandbox.terminal` bits. Preview env: [Environment variables](https://developers.cloudflare.com/sandbox/1-0-preview/environment/).

Non-secret config only in `setEnvVars` / launch `env`. Live credentials: Worker secrets + [outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/).

### Errors (do not one-loop retry)

| Error | Action |
| ----- | ------ |
| `ContainerUnavailableError` | Back off; retry as a **new** operation |
| `OperationInterruptedError` / `RPCTransportError` | Inspect; work may have started — no blind replay |
| `StaleProcessHandleError` / `StaleTerminalHandleError` | Relaunch from stored job |
| Local wait timeout / abort | Observation only; process may still run |

See [Errors and recovery](https://developers.cloudflare.com/sandbox/1-0-preview/errors/).

### Public URLs

Prefer `sandbox.tunnels` where appropriate; `exposePort` + `proxyToSandbox` when the Worker must front the request. Production preview hostnames need wildcard DNS on a custom domain.

### Bridge

Self-deployed HTTP bridge is **not** on the 1.0 preview line yet. Keep bridge Worker + image + clients on **stable**. See [Bridge](https://developers.cloudflare.com/sandbox/bridge/).

## Anti-patterns

- String `exec` that expects buffered completion (stable) on `@next`
- Mixing `@next` Worker with stable image
- Assuming session/`cd` state across `exec` calls
- Putting API keys in sandbox env
- Inventing `gitCheckout` on core — use argv `git` via `exec`
- Using general knowledge instead of `@next` types + preview docs

## Related skills

- **`sandbox-v1-migration`** — stable → `@next`
- **`sandbox-2026-deprecation`** — deprecated APIs while staying on stable
