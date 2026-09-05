# Skill discovery scenarios

Run these in fresh sessions with the plugin installed, using disposable fixtures. Record client/version, loaded skills, and observed behavior. Do not configure accounts or deploy during discovery checks. These are behavioral scenarios, not automated assertions about model routing.

| Prompt | Expected routing and behavior |
|---|---|
| Build a remote MCP server on Cloudflare with two read-only tools. | agents-sdk; retrieve MCP handler and security guidance; no dependency on slash commands. |
| Build a Cloudflare AI agent with persistent chat. | agents-sdk; use configuration, routing, and chat references. |
| Add Turnstile to this existing signup form and backend. | turnstile-spin; inspect the existing handler and preserve its behavior. |
| Send transactional email from this Worker. | cloudflare-email-service; retrieve sending/binding guidance. |
| Review this Worker for production readiness. | workers-best-practices; inspect installed versions and configuration. |
| Which Cloudflare storage product fits this workload? | cloudflare; compare relevant product references. |
| Build an MCP server for a local desktop app; do not use Cloudflare. | Do not select a Cloudflare implementation merely because MCP is mentioned. |

Repeat the first three prompts with a skills-only installation and a client without `commands/` support. Confirm the workflow remains discoverable. If a skill is absent, report that capability rather than pretending it was loaded.
