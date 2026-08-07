---
name: sandbox-migrate-to-next
description: Use when porting a Cloudflare Sandbox app from stable @cloudflare/sandbox to @cloudflare/sandbox@next (Sandbox SDK 1.0 preview), or when the user asks to migrate or upgrade to Sandbox 1.0 / @next. Not for day-to-day stable work (sandbox-stable) or new @next apps (sandbox-next).
---

# Migrate to Sandbox SDK 1.0 preview (`@next`)

**Perform** the port from the current stable package to `@cloudflare/sandbox@next`. Follow the steps in order. Human depth: [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [1.0 preview](https://developers.cloudflare.com/sandbox/1-0-preview/).

We recommend **new** projects start on `@next` (**`sandbox-next`**). Existing apps should migrate **when you can**, so you are ready when 1.0 becomes the stable release. The main [Sandbox docs](https://developers.cloudflare.com/sandbox/) still describe today’s stable package (**`sandbox-stable`**).

Do **not** force production cutover without the user agreeing.

**Not this skill:** day-to-day stable feature work → **`sandbox-stable`**. New `@next` work → **`sandbox-next`**. Deprecated-API cleanup **without** moving to `@next` → [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) on the stable package first if needed.

## Workflow

1. **Review** the hard rules and replacement map below (and the migrate doc if needed).
2. **Audit** the codebase; list every hit and its target shape.
3. **Clarify** uncertainty with the user (cutover timing, bridge, Python image, unclear call sites).
4. **Upgrade** package + image and apply code changes.
5. **Validate** typecheck, smokes, and a second grep.

Stop after any step that needs a user decision.

## Hard rules

- Worker package and container image must be the **same** `@next` line.
- Production cutover uses **immediate** container rollout (`--containers-rollout=immediate`). Stable and `@next` control protocols are incompatible both ways; gradual rollout leaves a broken mixed window. In-flight container work can stop.
- `await sandbox.exec(...)` means the process **started**, not that the command **finished**.
- Argv is passed **as-is** (no implicit shell). Shell syntax needs an explicit shell binary.
- Process handles have **no stdin**. Interactive input → terminals.
- Observation `timeout` / `AbortSignal` cancel **only that wait**. They do **not** kill the process.
- Do **not** use one retry loop for every error.
- Do **not** invent APIs (`gitCheckout` on core, process stdin, string-exec completion helper).
- Prefer installed `@next` types over guesses.
- Self-deployed bridge is not on the preview — keep bridge Worker, image, and clients on **stable**.

## Replacement map

| Stable | Preview |
| ------ | ------- |
| `SANDBOX_TRANSPORT` / `transport` / `setTransport` | Remove — RPC only |
| `await sandbox.exec("cmd")` → buffered result | `await sandbox.exec(argv)` → handle, then `output` / waits |
| `execStream` / `startProcess` | Same handle: `logs`, `waitFor*`, `kill` |
| Default / named sessions | Gone — `cwd`/`env` per launch, or one shell script |
| `sandbox.terminal(request)` / session terminal | `createTerminal` + `terminal.connect(request)` |
| xterm `sessionId` | `terminalId` |
| Interpreter on `Sandbox` | `withInterpreter` → `sandbox.interpreter.*` |
| `gitCheckout` | argv `git` via `exec` |
| String kill signals | Numeric only |
| Files, mounts, backups, ports, tunnels, `proxyToSandbox` | Mostly unchanged (ignore session/transport bits) |

## Audit

```sh
rg 'SANDBOX_TRANSPORT|transport:|setTransport|enableDefaultSession|createSession|getSession|deleteSession|execStream\(|startProcess\(|killProcess\(|sandbox\.terminal\(|sessionId|gitCheckout\(|SandboxTransport|ExecutionSession'
```

Also: string `exec(`, `cd` then a later `exec`, bare `createCodeContext` / `runCode` on `Sandbox`.

## Clarify (ask when needed)

- OK to cut production with immediate container rollout (live processes/terminals/streams may stop)?
- Self-deployed bridge present? Leave it on stable.
- Python interpreter → **`-python`** image variant?
- Call sites not covered below?

## Upgrade

### Package and image

```sh
npm install @cloudflare/sandbox@next
```

```dockerfile
FROM cloudflare/sandbox:next
# Python interpreter: cloudflare/sandbox:next-python
```

Use the same prerelease tag on Worker and image when not on floating `next`.

### Transport

Delete `SANDBOX_TRANSPORT`, `transport` on `getSandbox()`, `setTransport()`, `SandboxTransport`. No replacement setting.

### Commands

```ts
// Stable
const result = await sandbox.exec("npm test");

// Preview
const process = await sandbox.exec(["/bin/bash", "-lc", "npm test"]);
// or: await sandbox.exec(["npm", "test"], { cwd: "/workspace/app" });
const result = await process.output({ encoding: "utf8" });
```

Default `output()` streams are **bytes**. Pass `{ encoding: "utf8" }` for strings.

```ts
const server = await sandbox.exec(["/bin/bash", "-lc", "npm run dev"], {
  cwd: "/workspace/app",
});
await server.waitForPort(3000, { timeout: 60_000 }); // default mode: tcp
const stream = await server.logs({ follow: true, replay: true });
await server.kill(); // default 15
```

```ts
// One shot — do not rely on cd across separate exec calls
await sandbox.exec(["/bin/bash", "-lc", "cd /app && npm test"]);
// or
await sandbox.exec(["npm", "test"], { cwd: "/app", env: { NODE_ENV: "test" } });
```

- `setEnvVars` remains for sandbox-wide **non-secret** config.
- Do **not** put live API keys in `setEnvVars` or launch `env`. [Outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/).

| Goal | API |
| ---- | --- |
| Limit process lifetime | `exec(argv, { timeout })` |
| Limit how long you wait | `timeout` / `signal` on `output` / `waitFor*` / `logs` — does not kill |

### Sessions

Remove `createSession`, `getSession`, `deleteSession`, `enableDefaultSession`, `sessionId` options. Isolate users with **separate sandbox IDs**.

### Terminals

```ts
const terminal = await sandbox.createTerminal({
  command: ["bash"],
  cwd: "/workspace",
});
const t = await sandbox.getTerminal(terminal.id);
if (!t) return new Response("terminal gone", { status: 410 });
return t.connect(request, { cursor, cols, rows });
```

Browser `@cloudflare/sandbox/xterm`: pass `terminalId` (not `sessionId`).

### Interpreter

```ts
import { Sandbox as BaseSandbox } from "@cloudflare/sandbox";
import { withInterpreter } from "@cloudflare/sandbox/interpreter";

export class Sandbox extends BaseSandbox<Env> {
  interpreter = withInterpreter(this);
}

const ctx = await sandbox.interpreter.createCodeContext({ language: "python" });
const result = await sandbox.interpreter.runCode('print("hi")', { context: ctx });
```

Python requires the **`-python`** image. Same `@next` Worker + image line.

### Git

```ts
const clone = await sandbox.exec(
  ["git", "clone", "--depth", "1", "--", repoUrl, "/workspace/repo"],
  { cwd: "/workspace" },
);
const result = await clone.output({ encoding: "utf8" });
if (result.exitCode !== 0) throw new Error(result.stderr);
```

### Work across requests

Process IDs are **not** durable jobs. Store argv (or script), `cwd`, `env`, and app checkpoint — optionally `process.id` while it might still be alive.

```ts
const existing = processId ? await sandbox.getProcess(processId) : null;
if (existing) {
  await existing.logs({ since: cursor, replay: true, follow: true });
} else {
  const p = await sandbox.exec(storedArgv, { cwd: storedCwd, env: storedEnv });
  // save p.id
}
```

`getProcess` / `getTerminal` / `list*` do not start a container; they return `null` / `[]` when none is running.

### Errors

| Error | What to do |
| ----- | ---------- |
| `ContainerUnavailableError` | Back off; retry **new** operation |
| `OperationInterruptedError` | Work may have started — inspect before repeating side effects |
| `RPCTransportError` | This call may already have run |
| `StaleProcessHandleError` / `StaleTerminalHandleError` | Relaunch from stored work |
| `ProcessWaitTimeoutError` / `ProcessAbortedError` | Wait ended only — process may still run |
| `RuntimeControlProtocolError` | Worker and image not on same `@next` line — fix deploy |

Prefer `instanceof` on classes from `@cloudflare/sandbox`.

### Bridge

Leave self-deployed bridge on the stable release line. Do not pair bridge with `@cloudflare/sandbox@next`.

### Deploy cutover

Finish code on a branch/staging first. Production is **one** deploy of matching Worker + image:

```sh
npx wrangler deploy --containers-rollout=immediate
```

- Does not clear `rollout_active_grace_period`. Leave grace at default `0` (or set `0` if raised).
- Before: finish or stop work you must keep.
- After: treat pre-deploy process/terminal IDs as invalid; start work again.

## Validate

1. Lockfile + Dockerfile on the same `@next` line  
2. Typecheck against `@next`  
3. Smoke argv `exec` + `output({ encoding: "utf8" })`  
4. Smoke long process / terminal / interpreter if used  
5. Error handling distinguishes unavailable / interrupted-RPC / stale / local wait  
6. No live secrets in sandbox env  
7. Grep again for removed APIs  
8. Production cutover used `--containers-rollout=immediate`

## Red flags — stop and fix

- Mixing `@next` Worker with stable image (or reverse)
- Gradual container rollout for this control-plane cutover
- Treating `await exec` as command completion
- Assuming `cd` / exports persist across `exec` calls
- One retry wrapper for every sandbox error
- Inventing `gitCheckout`, process stdin, or undocumented extension APIs
- Keeping pre-cutover process/terminal IDs after deploy
- Forcing production cutover without user agreement
- Putting live secrets in `setEnvVars` / launch `env`
