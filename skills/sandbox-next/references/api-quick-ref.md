# `@next` API quick reference

Canonical: https://developers.cloudflare.com/sandbox/1-0-preview/api/

Prefer installed `@cloudflare/sandbox@next` types. This file is a scan aid only.

## Lifecycle

```ts
getSandbox(binding, sandboxId, options?: {
  sleepAfter?: string | number;
  keepAlive?: boolean;
  normalizeId?: boolean;
}): Sandbox

await sandbox.destroy(): Promise<void>
```

No `transport` / `enableDefaultSession` on `@next`.

## Processes

```ts
await sandbox.exec(argv: readonly [string, ...string[]], options?: {
  cwd?: string;
  env?: Record<string, string>;
  timeout?: number; // remote process lifetime
}): Promise<SandboxProcess>

await sandbox.getProcess(id: string): Promise<SandboxProcess | null>
await sandbox.listProcesses(): Promise<ProcessStatus[]>

await process.output({ encoding?: "utf8"; maxBytes?; timeout?; signal? })
await process.logs({ since?; replay?; follow?; signal? })
await process.waitForExit({ timeout?; signal? })
await process.waitForPort(port, { mode?: "tcp" | "http"; path?; timeout?; ... })
await process.waitForLog(pattern, { stream?; timeout?; signal? })
await process.kill(signal?: number) // default 15
await process.status()
```

`await exec` = launch succeeded. No process stdin.

## Terminals

```ts
await sandbox.createTerminal({ command: readonly [string, ...string[]]; cwd?; env?; cols?; rows?; bufferSize? })
await sandbox.getTerminal(id): Promise<Terminal | null>
await sandbox.listTerminals(): Promise<Terminal[]>

await terminal.connect(request, { cursor?; cols?; rows? })
await terminal.write(data: Uint8Array)
await terminal.resize(cols, rows)
await terminal.output({ since?; replay?; follow?; signal? })
await terminal.interrupt()
await terminal.terminate()
```

## Interpreter

```ts
import { withInterpreter } from "@cloudflare/sandbox/interpreter";
// subclass: interpreter = withInterpreter(this)

await sandbox.interpreter.createCodeContext({ language?, cwd? })
await sandbox.interpreter.runCode(code, { context?, language?, onStdout?, ... })
await sandbox.interpreter.runCodeStream(code, { context?, language? })
await sandbox.interpreter.listCodeContexts()
await sandbox.interpreter.deleteCodeContext(id)
```

## Environment

```ts
await sandbox.setEnvVars(Record<string, string | undefined>)
```

Non-secret only. Secrets: Worker + outbound handlers.
