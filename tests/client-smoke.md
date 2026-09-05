# Package and client checks

Run `python -m pip install -r scripts/requirements-validation.txt`, then `python scripts/validate-package.py`, `python -m unittest discover -s tests -v`, and `python -m unittest discover -s skills/turnstile-spin/tests -v` from a checkout. Python 3.12, Git, Bash, and jq are needed for all offline checks. Missing jq skips the relevant helper test; release checks should not skip it. The reference validator is pinned; its upstream describes it as a demonstration library, so it supplements rather than replaces the other checks.

For releases, record client/version, installed revision, observed components, and pass/fail evidence in the release PR. Use disposable projects; do not connect an account or deploy merely to test discovery.

| Client/install | Check |
|---|---|
| Portable Agent Plugins v1 loader | Discover `skills/*/SKILL.md` and `mcp.json`; retain the portable `streamable-http` transport. Do not assume native command/rule support. |
| Codex plugin | Discover skills, icon, starter prompts, and the Cloudflare MCP configuration from the native manifest. Confirm whether the native `mcpServers` wrapper is accepted. |
| Claude Code plugin | Discover skills and both commands. Invoke a build command from a project outside the plugin root; confirm its reference reads resolve inside the installed plugin. |
| Cursor plugin | Confirm skill and native rule discovery using the client installation path; record which command capabilities the tested client actually supports. |
| Skills-only installation | Run the [activation scenarios](activation.md) with no plugin MCP configuration. Use available documentation retrieval and report unavailable live account tools. |
| Browser tooling absent | Ask for a performance audit; continue useful analysis and report unmeasured trace metrics without inventing values. |
| Cloudflare MCP disconnected | Confirm skills remain usable for local work; report unavailable account operations and connect only within the requested task scope. |

Native adapter directories and `commands/`/`rules/` support client formats. They are not implementations of Agent Plugins' reverse-domain extension mechanism. Preserve them until client support for another layout is verified.

Live Turnstile checks remain in [validation.md](../skills/turnstile-spin/tests/validation.md). Run them separately against an explicitly selected test account and backend. Offline tests mock curl and use synthetic values; they do not validate cloud access or end-to-end Turnstile behavior.
