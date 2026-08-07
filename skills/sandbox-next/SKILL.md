---
name: sandbox-next
description: Use when building or changing Cloudflare Sandbox apps on @cloudflare/sandbox@next (Sandbox SDK 1.0 preview)—code execution, AI runners, interpreters, CI-like jobs, terminals, mounts, tunnels, or preview URLs. Not for the default stable package (use sandbox-stable) or for porting stable to @next (use sandbox-migrate-to-next).
---

# Cloudflare Sandbox SDK (`@next`)

Isolated Linux environments on [Cloudflare Containers](https://developers.cloudflare.com/containers/), driven from Workers.

This skill is the **1.0 preview** line: `@cloudflare/sandbox@next` and a matching `cloudflare/sandbox:next` image. We recommend this line for **new projects**. Existing apps on the default package should keep using **`sandbox-stable`** until they are ready to move; then use **`sandbox-migrate-to-next`**.

Prefer preview docs and installed `@next` types over memory. Stable and `@next` APIs differ.

## Confirm the package line

Before writing code, check the app:

- Dependency is `@cloudflare/sandbox@next` (or another preview tag), **and**
- Container image matches (for example `cloudflare/sandbox:next` or `next-python`)

| If you find… | Do this |
| ------------ | ------- |
| Default `@cloudflare/sandbox` (no `@next`) | Stop. Use **`sandbox-stable`** and the [main Sandbox docs](https://developers.cloudflare.com/sandbox/). Do not apply `@next` APIs. |
| User wants to **port** stable → `@next` | Stop. Use **`sandbox-migrate-to-next`**. |
| Self-deployed **bridge** only | Bridge is not on the 1.0 preview line yet. Keep bridge on the stable package + image. [Bridge](https://developers.cloudflare.com/sandbox/bridge/). |

Never mix an `@next` Worker package with a stable container image (or the reverse).

Install skills: [Agent setup](https://developers.cloudflare.com/agent-setup/) · [cloudflare/skills](https://github.com/cloudflare/skills).

## Retrieval

| Topic | URL |
| ----- | --- |
| Overview | https://developers.cloudflare.com/sandbox/1-0-preview/ |
| Get started | https://developers.cloudflare.com/sandbox/1-0-preview/get-started/ |
| Processes | https://developers.cloudflare.com/sandbox/1-0-preview/processes/ |
| Process API | https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/ |
| Terminals | https://developers.cloudflare.com/sandbox/1-0-preview/terminals/ |
| Errors | https://developers.cloudflare.com/sandbox/1-0-preview/errors/ |
| Environment | https://developers.cloudflare.com/sandbox/1-0-preview/environment/ |
| Interpreter | https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/ |
| Examples (`next` branch) | https://github.com/cloudflare/sandbox-sdk/tree/next/examples |
| API quick ref | [references/api-quick-ref.md](references/api-quick-ref.md) |

## Install

```bash
npm install @cloudflare/sandbox@next
docker info   # local container dev
```

## Worker shape

Re-export `Sandbox` and bind the Durable Object / container (see get-started):

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

## Core model

- `exec(argv)` takes an **argv** list and resolves when the process **starts**. It returns a **handle**.
- Observe or control with `output()`, `logs()`, `waitForExit()`, `waitForPort()`, `waitForLog()`, `kill(signal?)`.
- No implicit shell. Shell syntax needs an explicit shell, for example `["/bin/bash", "-lc", script]`.
- Each launch is independent. A `cd` in one `exec()` is not remembered in the next. Pass `cwd` and `env` when you need them.
- Process handles have **no stdin**. Interactive PTY → `createTerminal` + `connect`.
- Wait `timeout` / `AbortSignal` cancel the **wait only** — they do not kill the process. Use `kill` or `exec` remote `timeout`.
- `getProcess` / `listProcesses` do not start a container; they return `null` / `[]` when none is up.
- Process IDs live in the **current container**. Store the full job (argv, cwd, env) to relaunch after stop or replace.

```ts
const p = await sandbox.exec(["node", "--version"]);
const result = await p.output({ encoding: "utf8" });

const server = await sandbox.exec(["/bin/bash", "-lc", "npm run dev"], {
  cwd: "/workspace/app",
});
await server.waitForPort(3000, { timeout: 60_000 }); // default mode: tcp
await server.kill(); // numeric signal; default 15
```

### Interpreter

```ts
import { Sandbox as BaseSandbox } from "@cloudflare/sandbox";
import { withInterpreter } from "@cloudflare/sandbox/interpreter";

export class Sandbox extends BaseSandbox<Env> {
  interpreter = withInterpreter(this);
}
// sandbox.interpreter.createCodeContext / runCode
// Python needs the -python image variant
```

### Terminals

```ts
const terminal = await sandbox.createTerminal({ command: ["bash"] });
const t = await sandbox.getTerminal(terminal.id);
if (t) return t.connect(request, { cursor });
```

### Env, URLs, errors

- Non-secret config only in `setEnvVars` / launch `env`. Secrets stay in the Worker; use [outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) when processes call external APIs.
- Public URLs: `sandbox.tunnels` when it fits; `exposePort` + `proxyToSandbox` when the Worker must front the request. Production hostnames need wildcard DNS on a custom domain.
- Do not use one retry loop for every error. `ContainerUnavailableError` → back off, new operation. `OperationInterruptedError` / `RPCTransportError` → inspect (work may have started). Stale handle → relaunch from stored job. Local wait timeout → observation only.

## Common mistakes

- Using this skill on the default stable package
- Treating `await exec` as “command finished”
- Mixing `@next` Worker with a stable image
- Assuming shell state across `exec` calls
- Putting API keys in sandbox env
- Inventing `gitCheckout` on core — run `git` via argv `exec`
