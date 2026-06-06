# Cloudflare Skills

A collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), MCP servers, and slash commands for building on Cloudflare, Workers, the Agents SDK, and the wider Cloudflare Developer Platform.

This marketplace ships **10 plugins** for both Claude Code and Cursor: 9 product plugins plus an umbrella. Install the umbrella for the full experience, or install only the product plugins you need to keep your context window lean.

## Installing

These skills work with any agent that supports the Agent Skills standard, including Claude Code, OpenCode, OpenAI Codex, and Pi.

### Claude Code

Add the marketplace, then install:

```
/plugin marketplace add cloudflare/skills
```

For the **full experience** (everything, identical to previous behavior):

```
/plugin install cloudflare@cloudflare
```

This installs the `cloudflare` umbrella plugin, which depends on all 9 product plugins and pulls them in automatically.

For **narrower scope** (lower per-session token usage), install only the plugins you need. Examples:

```
# Just Workers + the umbrella's API/docs context
/plugin install cloudflare-workers@cloudflare

# Workers + log inspection
/plugin install cloudflare-workers@cloudflare
/plugin install cloudflare-observability@cloudflare

# Just web-performance auditing (no Cloudflare context loaded at all)
/plugin install cloudflare-web-perf@cloudflare
```

Each product plugin transitively pulls in the plugins it depends on (e.g. installing `cloudflare-workers` automatically installs `cloudflare-core`).

### Cursor

Add the marketplace via the Cursor plugin UI, then install plugins from it.

For the **full experience** (all skills + all 5 MCP servers in one install, identical to previous behavior), install the `cloudflare` umbrella plugin.

For **narrower scope**, install only the per-product plugins you need. Cursor's plugin system has no dependency mechanism, so each plugin is installed individually and ships only its own MCP servers — installing only `cloudflare-workers`, for example, gives you `cloudflare-bindings` and `cloudflare-builds` but not `cloudflare-api`/`cloudflare-docs`/`cloudflare-observability`. Install the umbrella `cloudflare` plugin if you want the full MCP surface.

### npx skills

Install using the [`npx skills`](https://skills.sh) CLI:

```
npx skills add https://github.com/cloudflare/skills
```

### Clone / Copy

Clone this repo and copy the relevant skill folders from `plugins/<plugin-name>/skills/` into the appropriate directory for your agent:

| Agent | Skill Directory | Docs |
|-------|-----------------|------|
| Claude Code | `~/.claude/skills/` | [docs](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.cursor/skills/` | [docs](https://cursor.com/docs/context/skills) |
| OpenCode | `~/.config/opencode/skills/` | [docs](https://opencode.ai/docs/skills/) |
| OpenAI Codex | `~/.codex/skills/` | [docs](https://developers.openai.com/codex/skills/) |
| Pi | `~/.pi/agent/skills/` | [docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills) |

## Plugins

| Plugin | Skills | MCP servers | Commands | Depends on |
|---|---|---|---|---|
| `cloudflare-core` | `cloudflare` | `cloudflare-api`, `cloudflare-docs` | — | — |
| `cloudflare-workers` | `wrangler`, `workers-best-practices` | `cloudflare-bindings`, `cloudflare-builds` | — | `cloudflare-core` |
| `cloudflare-observability` | — | `cloudflare-observability` | — | `cloudflare-workers` |
| `cloudflare-durable-objects` | `durable-objects` | — | — | `cloudflare-workers` |
| `cloudflare-agents` | `agents-sdk` | — | `/build-agent`, `/build-mcp` | `cloudflare-workers` |
| `cloudflare-sandbox` | `sandbox-sdk` | — | — | `cloudflare-workers` |
| `cloudflare-email` | `cloudflare-email-service` | — | — | `cloudflare-core` |
| `cloudflare-turnstile` | `turnstile-spin` | — | — | `cloudflare-workers` |
| `cloudflare-web-perf` | `web-perf` | — | — | — *(no Cloudflare dep)* |
| `cloudflare` | — | — | — | all 9 above (umbrella) |

Cursor's plugin system has no dependency mechanism, so the dependency arrows above don't apply on Cursor. The Cursor `cloudflare` umbrella bundles all skills and MCP servers in a single install (rather than depending on the product plugins, which is what the Claude umbrella does); per-product Cursor installs ship only their own MCP servers. See the [Repository layout](#repository-layout) section for how this is wired.

## Commands

Commands are user-invocable slash commands that you explicitly call. They're shipped by the `cloudflare-agents` plugin.

| Command | Description |
|---------|-------------|
| `/cloudflare-agents:build-agent` | Build an AI agent on Cloudflare using the Agents SDK |
| `/cloudflare-agents:build-mcp` | Build an MCP server on Cloudflare |

## Skills

Skills are contextual and auto-loaded based on your conversation. When a request matches a skill's triggers, the agent loads and applies the relevant skill to provide accurate, up-to-date guidance.

| Skill | Plugin | Useful for |
|-------|--------|------------|
| cloudflare | cloudflare-core | Comprehensive platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI, Vectorize, Agents SDK), networking (Tunnel, Spectrum), security (WAF, DDoS), and IaC (Terraform, Pulumi) |
| wrangler | cloudflare-workers | Deploying and managing Workers, KV, R2, D1, Vectorize, Queues, Workflows |
| workers-best-practices | cloudflare-workers | Reviewing and authoring Workers code against production best practices |
| durable-objects | cloudflare-durable-objects | Stateful coordination (chat rooms, games, booking), RPC, SQLite, alarms, WebSockets |
| agents-sdk | cloudflare-agents | Building stateful AI agents with state, scheduling, RPC, MCP servers, email, and streaming chat |
| sandbox-sdk | cloudflare-sandbox | Secure code execution for AI code execution, code interpreters, CI/CD systems, and interactive dev environments |
| cloudflare-email-service | cloudflare-email | Sending and receiving transactional emails (Workers binding or REST API) |
| turnstile-spin | cloudflare-turnstile | Setting up Turnstile CAPTCHA end-to-end: widget creation, managed siteverify Worker, and frontend snippets |
| web-perf | cloudflare-web-perf | Auditing Core Web Vitals (FCP, LCP, TBT, CLS), render-blocking resources, network chains |

## Cloudflare One

Short, retrieval-first skills for [Cloudflare One](https://developers.cloudflare.com/cloudflare-one/) work.

| Skill | Useful for |
|-------|------------|
| cloudflare-one | Designing, configuring, troubleshooting, or reviewing Cloudflare One deployments across Access, Gateway, WARP, Tunnel, Magic WAN, DLP, CASB, posture, and identity |
| cloudflare-one-migrations | Migration assessments, policy mapping, rollout plans, and gap analysis for Zscaler, Palo Alto, legacy VPN/SWG, and SASE migrations to Cloudflare One |

## MCP Servers

This marketplace bundles [Cloudflare's remote MCP servers](https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/), distributed across the plugins that own them:

| Server | Plugin | Purpose |
|--------|--------|---------|
| cloudflare-api | cloudflare-core | Manage Cloudflare account resources, zones, and settings |
| cloudflare-docs | cloudflare-core | Up-to-date Cloudflare documentation and reference |
| cloudflare-bindings | cloudflare-workers | Build Workers applications with storage, AI, and compute primitives |
| cloudflare-builds | cloudflare-workers | Manage and get insights into Workers builds |
| cloudflare-observability | cloudflare-observability | Debug and analyze Workers logs and analytics |

## Repository layout

Canonical plugin content lives under `plugins/<product>/` — each product plugin owns its own `skills/`, `commands/`, `rules/`, and (where applicable) `.mcp.json`. Edit there.

The repo root has `skills/`, `commands/`, `rules/` directories of **symlinks** pointing into the product plugins. These exist so the Cursor `cloudflare` umbrella plugin (rooted at `./`) can serve the same content as the per-product plugins without duplication on disk.

The root `.mcp.json` aggregates all 5 MCP servers and is **hand-maintained**. When you add or remove a server in any product `plugins/<product>/.mcp.json`, also update the root file to keep them in sync.

## Resources

- [Cloudflare Agents Documentation](https://developers.cloudflare.com/agents/)
- [Cloudflare MCP Guide](https://developers.cloudflare.com/agents/model-context-protocol/)
- [Agents SDK Repository](https://github.com/cloudflare/agents)
- [Agents Starter Template](https://github.com/cloudflare/agents-starter)
