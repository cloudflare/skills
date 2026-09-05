---
name: sandbox-migrate-to-next
description: Use when porting a Cloudflare Sandbox app from stable @cloudflare/sandbox to @cloudflare/sandbox@next (Sandbox SDK 1.0 preview), or when the user asks to migrate or upgrade to Sandbox 1.0 / @next. Not for day-to-day stable work (sandbox-stable) or new @next apps (sandbox-next).
---

# Migrate stable → Sandbox SDK 1.0 preview (`@next`)

**Perform** the authorized local port through validation. Resolve production cutover separately, after the changes are concrete and reviewable. Depth lives in docs—fetch the linked page when a step needs detail.

Human guide: [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [1.0 preview](https://developers.cloudflare.com/sandbox/1-0-preview/)

**New projects** should start on `@next` (**`sandbox-next`**), not this skill. **Day-to-day stable work** → **`sandbox-stable`**. Deprecated-API cleanup **without** moving to `@next` → [2026 deprecation guide](https://developers.cloudflare.com/sandbox/guides/2026-deprecation/) first if needed.

Existing apps should migrate **when you can**, so you are ready when 1.0 becomes the stable release. Do **not** force production cutover without the user agreeing.

**Prefer installed `@next` types and the migrate doc over memory.**

## Workflow

1. **Review and audit** the hard rules, replacement map, and affected code. Infer bridge and interpreter requirements from the project.
2. **Upgrade locally** the package, image, and code within the requested scope. Resolve missing consequential details only for the changes that depend on them.
3. **Validate locally**, fix migration defects, and rerun the affected checks.
4. **Prepare cutover** details and a reviewable result. Deploy only when the exact target and disruptive rollout are explicitly authorized.

A pending deployment decision does not block the local port. If another decision is needed, pause its dependent work and continue independent changes and validation. A request to migrate code does not by itself authorize a production deployment.

## Hard rules

- Worker package and container image must be the **same** `@next` line.  
- Production cutover uses **immediate** container rollout. Stable and `@next` control protocols are incompatible both ways; gradual rollout leaves a broken mixed window. In-flight container work can stop.  
- After cutover, `await sandbox.exec(...)` means process **started**, not command **finished**.  
- Argv is as-is (no implicit shell). Shell syntax needs an explicit shell binary.  
- Process handles have **no stdin** → terminals for interactive input.  
- Observation `timeout` / `AbortSignal` cancel the **wait only**, not the process.  
- No single retry loop for every error.  
- Do not invent APIs (`gitCheckout` on core, process stdin, string-exec completion helper).  
- Self-deployed bridge stays on **stable** (not part of the preview line yet).  

## Replacement map

| Stable | `@next` |
| ------ | ------- |
| `SANDBOX_TRANSPORT` / `transport` / `setTransport` | Remove — RPC only |
| `await sandbox.exec("cmd")` → buffered result | `await sandbox.exec(argv)` → handle, then `output` / waits |
| `execStream` / `startProcess` | Same handle: `logs`, `waitFor*`, `kill` |
| Default / named sessions | Gone — `cwd`/`env` per launch, or one shell script |
| `sandbox.terminal(request)` / session terminal | `createTerminal` + `terminal.connect(request)` |
| xterm `sessionId` | `terminalId` |
| Interpreter methods on `Sandbox` | `withInterpreter` → `sandbox.interpreter.*` |
| `gitCheckout` | argv `git` via `exec` |
| String kill signals | Numeric only |
| Files, mounts, backups, ports, tunnels, `proxyToSandbox` | Mostly unchanged (ignore session/transport bits on stable pages) |

Depth: [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · after port, day-to-day → **`sandbox-next`**

## Audit

```sh
rg 'SANDBOX_TRANSPORT|transport:|setTransport|enableDefaultSession|createSession|getSession|deleteSession|execStream\(|startProcess\(|killProcess\(|sandbox\.terminal\(|sessionId|gitCheckout\(|SandboxTransport|ExecutionSession'
```

Also: string `exec(`, `cd` then a later `exec`, bare `createCodeContext` / `runCode` on `Sandbox`.

## Resolve Local Requirements

Inspect dependencies, images, configuration, and call sites before asking:

- **Self-deployed bridge:** leave it on stable. If it shares dependencies or an image with the migrating app, isolate the targets before upgrading; ask when the intended split is unclear.
- **Python interpreter:** preserve existing Python use with the matching **`-python`** preview image. Ask only when the code and configuration leave the requirement unclear.
- **Unmapped call sites:** inspect the linked migration documentation and installed preview types. Ask about application behavior only when it cannot be inferred and materially changes the port.

Collect unresolved choices together when practical. Production rollout timing and interruption approval belong to the cutover step after local validation.

## Upgrade

### Package and image

```sh
npm install @cloudflare/sandbox@next
```

```dockerfile
FROM cloudflare/sandbox:next
# Python: cloudflare/sandbox:next-python
```

Same prerelease tag on Worker and image when not on floating `next`.

### Code by area

Apply replacements from the map. For each area, implement from the doc—not from stable habits:

| Area | Doc |
| ---- | --- |
| Commands / handles / waits | [Processes](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) · [Processes API](https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/) |
| `cwd` / `env` / secrets | [Environment](https://developers.cloudflare.com/sandbox/1-0-preview/environment/) · [Outbound traffic](https://developers.cloudflare.com/sandbox/guides/outbound-traffic/) |
| Drop sessions | [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [Lifecycle](https://developers.cloudflare.com/sandbox/1-0-preview/lifecycle/) |
| Terminals | [Terminals](https://developers.cloudflare.com/sandbox/1-0-preview/terminals/) |
| Interpreter | [Interpreter](https://developers.cloudflare.com/sandbox/1-0-preview/interpreter/) |
| Errors | [Errors](https://developers.cloudflare.com/sandbox/1-0-preview/errors/) |
| Durable job across requests | [Process execution — lifetime / durability](https://developers.cloudflare.com/sandbox/1-0-preview/processes/) |

**Commands (shape):**

```ts
// Before (stable)
const result = await sandbox.exec("npm test");

// After (@next)
const process = await sandbox.exec(["/bin/bash", "-lc", "npm test"]);
const result = await process.output({ encoding: "utf8" });
```

```ts
const server = await sandbox.exec(["/bin/bash", "-lc", "npm run dev"], {
  cwd: "/workspace/app",
});
await server.waitForPort(3000, { timeout: 60_000 });
await server.kill(); // numeric; default 15
```

**Terminals (shape):**

```ts
const terminal = await sandbox.createTerminal({ command: ["bash"], cwd: "/workspace" });
const t = await sandbox.getTerminal(terminal.id);
if (!t) return new Response("terminal gone", { status: 410 });
return t.connect(request, { cursor, cols, rows });
```

**Interpreter (shape):**

```ts
import { Sandbox as BaseSandbox } from "@cloudflare/sandbox";
import { withInterpreter } from "@cloudflare/sandbox/interpreter";

export class Sandbox extends BaseSandbox<Env> {
  interpreter = withInterpreter(this);
}
```

**Git (shape):**

```ts
const clone = await sandbox.exec(
  ["git", "clone", "--depth", "1", "--", repoUrl, "/workspace/repo"],
  { cwd: "/workspace" },
);
const result = await clone.output({ encoding: "utf8" });
```

Delete transport settings entirely. Remove session APIs. Isolate users with **separate sandbox IDs**.

## Validate Locally

Use the checks relevant to the migrated features in a local or disposable environment. Fix failures caused by the port and rerun the affected checks without asking for approval at each iteration. If a runtime or dependency is unavailable, finish the checks that can run and report the remaining validation as pending. Do not use production as an implicit smoke-test target.

1. Lockfile + Dockerfile on the same `@next` line  
2. Typecheck against `@next`  
3. Smoke argv `exec` + `output({ encoding: "utf8" })`  
4. Smoke long process / terminal / interpreter if used  
5. Errors distinguished: unavailable / interrupted-RPC / stale / local wait  
6. No live secrets in sandbox env  
7. Grep again for removed APIs  

## Production Cutover

After local work is ready, summarize the changes and validation, then resolve the exact account, Worker, environment/configuration, and matching image. State that immediate rollout can interrupt live processes, terminals, and streams and invalidates their existing IDs. If explicit authorization already covers that target and interruption, reuse it; otherwise ask immediately before deployment. Keep any deployment pending while completing the local migration deliverable.

Use staging or a branch environment first when available and authorized. Production is **one** deploy of matching Worker + image, using the resolved target arguments:

```sh
npx wrangler deploy --containers-rollout=immediate
```

Leave `rollout_active_grace_period` at default `0` (or set `0` if raised). After cutover, pre-deploy process/terminal IDs are invalid. Details: [Migrate](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) · [Container rollouts](https://developers.cloudflare.com/containers/platform-details/rollouts/)

When deployment is authorized and performed, verify the intended target used `--containers-rollout=immediate` with matching package and image, then run the applicable authorized post-deploy checks. Report deployment and runtime verification separately from local validation; do not claim production cutover occurred when it remains pending.

Then day-to-day work uses **`sandbox-next`**.

## Red flags — stop and fix

- Mixing `@next` Worker with stable image (or reverse)  
- Gradual container rollout for this cutover  
- Treating `await exec` as command completion  
- Assuming `cd` / exports persist across `exec` calls  
- One retry wrapper for every error  
- Inventing `gitCheckout`, process stdin, or undocumented APIs  
- Keeping pre-cutover process/terminal IDs after deploy  
- Forcing production cutover without user agreement  
- Putting live secrets in `setEnvVars` / launch `env`  
