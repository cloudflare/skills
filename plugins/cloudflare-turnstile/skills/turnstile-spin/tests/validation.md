# Skill validation cases

These cases match the assertions in the Turnstile Spin PRD. Run them after editing this skill to confirm an agent loading it can still execute the wizard end-to-end.

## Test 1 — Dummy siteverify returns a structured error

Step 10's `validate.sh` sends a deliberately-invalid token directly to `challenges.cloudflare.com/turnstile/v0/siteverify` using the captured secret. The expected response is `success: false` with `error-codes: ["invalid-input-response"]`. Anything else means the secret is wrong or the widget is misconfigured.

```sh
curl -s -X POST "https://challenges.cloudflare.com/turnstile/v0/siteverify" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "secret=${TURNSTILE_SECRET}" \
  --data-urlencode "response=XXXX.DUMMY.TOKEN.XXXX" | \
  jq -e '.success == false and (.["error-codes"] | index("invalid-input-response"))'
```

Expected exit code: 0.

## Test 2 — Hostname configuration

```sh
curl -s "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/challenges/widgets/${SITEKEY}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | \
  jq -e '.result.domains | contains(["example.com"])'
```

Expected exit code: 0.

## Test 3 — Telemetry marker is in every written snippet

After the wizard completes, grep the written files:

```sh
rg -l 'data-action="turnstile-spin-v2"' <(echo "$WRITTEN_FILES")
```

Expected: every written file matches. If a snippet was written without the marker, the wizard skipped the Step 9 contract (or the agent edited the template). Re-run.

## Test 4 — Skill persists to the right location

After Step 11:

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
ACCOUNT_ID=... SITEKEY=... TURNSTILE_SECRET=... CLOUDFLARE_API_TOKEN=... \
  bash tests/run-all.sh
```

(`run-all.sh` is not bundled with this skill; the cases above are intended to be wired into the consuming agent's own test harness, or run by hand after a deploy.)
