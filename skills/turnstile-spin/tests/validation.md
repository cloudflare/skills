# Skill validation cases

These cases match the MVP-row assertions in the Turnstile Spin PRD. Run them after editing this skill to confirm an agent loading it can still execute the wizard end-to-end.

## Test 1 — Health check parses cleanly

Given a deployed Worker, the agent should be able to parse `/health` without ambiguity.

```sh
curl -sf "${WORKER_URL}/health" | jq -e '.ok == true and (.version | type) == "string"'
```

Expected exit code: 0.

## Test 2 — Dummy siteverify returns a structured error

The wizard's Step 7b sends a deliberately-invalid token. The Worker must return `success: false`, a non-empty `error-codes` array, and a `_worker` block — not a bare 500.

```sh
curl -s -X POST "${WORKER_URL}/" \
  -H "Content-Type: application/json" \
  -d '{"token":"XXXX.DUMMY.TOKEN.XXXX"}' | \
  jq -e '.success == false and (.["error-codes"] | length) > 0 and (._worker | type) == "object"'
```

Expected exit code: 0.

## Test 3 — Hostname configuration

```sh
npx wrangler turnstile widget show "${WIDGET_ID}" | \
  jq -e '.result.domains | contains(["example.com"])'
```

Expected exit code: 0.

## Test 4 — Telemetry marker is in every written snippet

After the wizard completes, grep the written files:

```sh
rg -l 'data-action="turnstile-spin-v1"' <(echo "$WRITTEN_FILES")
```

Expected: every written file matches. If a snippet was written without the marker, the wizard skipped Step 6 (or the agent edited the template). Re-run.

## Test 5 — Skill persists to the right location

After Step 8:

```sh
test -f .claude/skills/turnstile-spin/SKILL.md \
  || test -f .cursor/rules/turnstile-spin.md \
  || test -f .codex/skills/turnstile-spin/SKILL.md \
  || test -f .opencode/skills/turnstile-spin/SKILL.md \
  || test -f .github/copilot/skills/turnstile-spin.md \
  || test -f .windsurf/rules/turnstile-spin.md
```

Expected exit code: 0.

## Running all cases

```sh
WORKER_URL=https://your-worker.workers.dev WIDGET_ID=0x4AAAAAAA... \
  bash tests/run-all.sh
```

(`run-all.sh` is not bundled with this skill; the cases above are intended to be wired into the consuming agent's own test harness, or run by hand after a deploy.)
