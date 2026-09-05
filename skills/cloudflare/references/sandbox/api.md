# Sandbox API documentation

[Choose the package line](./README.md#choose-the-package-line-first) first. Fetch the task's API page and check installed types instead of copying signatures between stable and preview.

| Task | Stable | 1.0 preview (`@next`) |
| --- | --- | --- |
| Execute commands, stream output, run background work, wait for readiness | [Commands API](https://developers.cloudflare.com/sandbox/api/commands/) | [Processes API](https://developers.cloudflare.com/sandbox/1-0-preview/api/processes/) |
| Shell state and environment across calls | [Sessions API](https://developers.cloudflare.com/sandbox/api/sessions/) | [Environment](https://developers.cloudflare.com/sandbox/1-0-preview/environment/) (sessions were removed) |
| Interactive browser terminals | [Terminal API](https://developers.cloudflare.com/sandbox/api/terminal/) | [Terminals API](https://developers.cloudflare.com/sandbox/1-0-preview/api/terminals/) |
| Python and JavaScript code interpretation | [Interpreter API](https://developers.cloudflare.com/sandbox/api/interpreter/) | [Interpreter API](https://developers.cloudflare.com/sandbox/1-0-preview/api/interpreter/) |
| Sandbox identity, sleep, and destruction | [Lifecycle API](https://developers.cloudflare.com/sandbox/api/lifecycle/) | [Sandbox lifecycle](https://developers.cloudflare.com/sandbox/1-0-preview/lifecycle/) |

For shared surfaces, read [Files](https://developers.cloudflare.com/sandbox/api/files/), [Storage](https://developers.cloudflare.com/sandbox/api/storage/), [Backups](https://developers.cloudflare.com/sandbox/api/backups/), [Ports](https://developers.cloudflare.com/sandbox/api/ports/), and [Tunnels](https://developers.cloudflare.com/sandbox/api/tunnels/). The [preview overview](https://developers.cloudflare.com/sandbox/1-0-preview/) explains which main-docs surfaces remain applicable; ignore removed session and transport options on those pages when using `@next`.
