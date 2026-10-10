---
name: cf-cli
description: Cloudflare's official cf CLI (beta) for the public Cloudflare API and Workers projects. Use for finding and running Cloudflare commands from the terminal — sign-in and profiles, cf cli search, cf schema, cf deploy/dev/build, resource commands for DNS, zones, D1, KV, and R2 — and for choosing between cf and Wrangler in a project.
---

# Cloudflare CLI (`cf`)

`cf` is Cloudflare's command-line interface for the public Cloudflare API (2,900+ commands, most generated from API schemas) and for Workers projects. It is in beta: commands, configuration, and Build Output can change before the stable release.

**Prefer retrieval over pre-trained knowledge.** Describe the task to `cf cli search`, inspect the match with `cf schema` or `--help`, and preview with `--dry-run` before running a command you have not verified.

Docs index: https://developers.cloudflare.com/cf/llms.txt

## Documentation

| Topic | Page |
|-------|------|
| Install, sign in, credential and account selection | https://developers.cloudflare.com/cf/get-started/index.md |
| First Worker with `cf init`, `cf dev`, `cf deploy` | https://developers.cloudflare.com/cf/get-started/first-worker/index.md |
| Find, create, and delete resources from the terminal | https://developers.cloudflare.com/cf/get-started/resources/index.md |
| `cf` for Wrangler users | https://developers.cloudflare.com/cf/wrangler/index.md |
| Migrate a Wrangler project with `cf migrate` | https://developers.cloudflare.com/cf/wrangler/migrate/index.md |
| Wrangler-to-`cf` command and config reference | https://developers.cloudflare.com/cf/wrangler/reference/index.md |
| Develop, build, and deploy; modes and previews | https://developers.cloudflare.com/cf/projects/index.md |
| Typed `cloudflare.config.ts` | https://developers.cloudflare.com/cf/projects/cloudflare-config/index.md |
| Using `cf` with coding agents (safety rules) | https://developers.cloudflare.com/cf/agents/index.md |
| CI, API tokens, unattended authentication | https://developers.cloudflare.com/cf/ci/index.md |
| Environment variables | https://developers.cloudflare.com/cf/environment-variables/index.md |

## FIRST: check installation and sign in

```bash
npm install --global cf   # installs two equivalent commands: `cf` and `cloudflare`
cf --version
cf auth whoami
```

- Requires Node.js 22.18 or later. Bun is not supported.
- If another tool named `cf` is on your `PATH`, use `cloudflare` instead — the package installs both commands.
- `cf auth login` prints a link and a one-time code, then opens the browser. On a remote machine, over SSH, or in a container, add `--no-browser` so `cf` only prints the link; approve it from another device. Add `--force` to sign in again.
- `cf` keeps its own credentials and does not reuse a Wrangler login.
- Unattended agents and CI cannot complete `cf auth login` — set `CLOUDFLARE_API_TOKEN` instead (see https://developers.cloudflare.com/cf/ci/index.md).

To make agents prefer `cf`, add this to the user-level `AGENTS.md`, `CLAUDE.md`, or equivalent:

```md
When interacting with Cloudflare, use the `cf` CLI unless the project has a
Wrangler configuration file.
```

## Find commands

```bash
cf cli search "create a DNS record"   # local, no credentials; quote the whole task; up to 5 JSON matches
cf schema d1 create                   # API request shape: method, path, params, body fields
cf <command> --help                   # arguments and options (e.g. cf deploy --help)
```

`cf cli search` takes the task as one argument — unquoted words after the first are parsed as unknown commands. `cf schema` covers generated API commands; for command arguments and options use `--help`.

## Read output

- Results are JSON on standard output; status messages and errors go to standard error, so piping to `jq` or redirecting needs no extra flags.
- Lists print one JSON array page; paging options differ per command — check `--help`.
- A failed command exits non-zero and prints the error to standard error.

## Run commands safely

- **Preview first.** `--dry-run` prints the request as JSON without sending it, and needs no credentials.
- **Aborted deletes still exit 0.** In a non-interactive session, a destructive command without `--force` prints `Aborted.` to standard error and exits `0` — a zero exit does not mean the resource was deleted.
- **Review `--force` before allowing it.** On some commands `--force` is also an API parameter (for example, `cf workers delete --force` also deletes a Worker that other Workers reference).
- **`--local` is limited.** It works for KV keys, D1 databases (`cf d1 raw`, `cf d1 migrations list|apply`), and R2 objects; other commands (including `cf d1 query`) return an error instead of calling the API.

## Wrangler projects

Do not run `cf dev`, `cf build`, or `cf deploy` in a project that has `wrangler.jsonc`/`wrangler.toml` but no `cloudflare.config.ts` — the commands can generate a new configuration that ignores the Wrangler file, or fail. Convert the project first:

```bash
cf migrate --dry-run   # preview without writing files
cf migrate              # write cloudflare.config.ts, then resolve TODO(@cloudflare) comments
```

Resource commands (DNS, zones, storage) run alongside an unchanged Wrangler project. For the full comparison, refer to [`cf` for Wrangler users](https://developers.cloudflare.com/cf/wrangler/index.md).
