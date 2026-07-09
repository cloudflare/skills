---
name: turnstile-spin
description: Set up Cloudflare Turnstile end-to-end in a project — scan the codebase, create the widget via the Cloudflare API, deploy the managed siteverify Worker, write the frontend snippets, validate, and persist the skill. Load this when a user asks to add Turnstile, set up CAPTCHA, protect a form from bots, or fix a Turnstile integration. Mirrors developers.cloudflare.com/turnstile/spin.
references:
  - vanilla-html
  - nextjs-app
  - nextjs-pages
  - astro
  - sveltekit
  - hugo
---

# Turnstile Spin skill

Turns the prompt "set up Turnstile" into a working end-to-end integration: a widget, a deployed managed siteverify Worker, frontend snippets at every chosen insertion point, and a real validation pass before reporting success.

You are the agent. Run the wizard below by invoking the scripts under `scripts/` and branching on their JSON output. The scripts hold the deterministic logic (API calls, retry/error handling); your job is orchestration, codebase reading, confirmation, and the frontend edits.

Canonical instructions live at [`developers.cloudflare.com/turnstile/spin`](https://developers.cloudflare.com/turnstile/spin/). If the docs page and this file disagree, trust the docs page.

## When to load this skill

Load when the user's prompt mentions any of:

- "Turnstile", "CAPTCHA", "bot protection"
- "siteverify", "cf-turnstile-response"
- "protect this form", "stop bot signups", "spam signups"
- A specific signup, login, or contact form combined with "Cloudflare" or "bot"

Do not load for unrelated Cloudflare tasks (Workers, Pages, R2, etc.) unless Turnstile is also mentioned.

## Conversation flow

The user pasted the prompt. You are in a multi-step dialog. Detect what you can, ask only when you have to, confirm before every irreversible step. Each numbered moment is one agent message. Items marked **[wait for user]** require a user response.

1. **Brief acknowledge.** One sentence: "I'll run Turnstile setup end to end. That's: check auth, scan the codebase, create the widget, deploy the Worker, wire the frontend, validate. Proceed?" **[wait for user]** Do NOT present a plan yet. Auth + scan come first.

2. **Wrangler check.** `npx wrangler --version`. If missing, ask once: "Install wrangler with `npm install --save-dev wrangler` (Node project) or `npm install -g wrangler` (other)? Proceed?" **[wait for user]** If install is blocked entirely (corporate policy, blocked npm), fall back to driving Steps 4-5 via `curl` against `api.cloudflare.com/client/v4/`.

3. **Auth + scope probe (FIRST irreversible action).** Run `scripts/auth-probe.sh`. Branch on `status`:
   - `ok`: continue to Step 4. The script already picked the account (single-account token, or one matching `$CLOUDFLARE_ACCOUNT_ID`).
   - `missing_token`, `missing_scope`, or `missing_workers_scope`: ask the user to create a token at https://dash.cloudflare.com/profile/api-tokens → Custom token → permissions `Account.Turnstile:Edit` **and** `Account.Workers Scripts:Edit` → include the target account in Account Resources. **Do NOT direct them to `wrangler login`**. Its OAuth scope doesn't include `Account.Turnstile:Edit` or `Account.Workers Scripts:Edit`. Offer three ways to hand the token over, cleanest first:
     1. **Export + relaunch** (token never enters chat): `export CLOUDFLARE_API_TOKEN=<token>` then restart the agent from that terminal.
     2. **Save to file** (token in file with user-only perms, not in chat): `umask 077 && printf '%s' '<token>' > ~/.cf-turnstile-token`, then read with `TOKEN=$(cat ~/.cf-turnstile-token)`.
     3. **Paste in chat** (fastest, but token lands in conversation log; user should rotate it after if the log is ever shared).
     If the user picks option 3 (paste in chat), you can use the wait to run Steps 5, 6, 7 (Domain, Codebase scan, Insertion plan). Options 1 and 2 will restart your session, so do not pre-fetch state in those cases. When auth is established, re-run `auth-probe.sh`, then continue to Step 8.
   - `multiple_accounts`: the token covers more than one account and `$CLOUDFLARE_ACCOUNT_ID` is unset. Present the numbered `accounts` list. **[wait for user]** Then export `CLOUDFLARE_ACCOUNT_ID=<chosen>` and re-run `auth-probe.sh`.
   - `account_mismatch`: `$CLOUDFLARE_ACCOUNT_ID` is set but isn't one of the token's accounts. Show the `accounts` list and ask the user to either `unset CLOUDFLARE_ACCOUNT_ID` or set it to one of those IDs.

4. **Account selection.** If `auth-probe.sh` returned `ok` after a `multiple_accounts` round-trip, this is already done. Otherwise the script picked the single account silently and you continue to Step 5.

5. **Domain.** Always include `localhost` and `127.0.0.1`. For production, scan `package.json` `homepage`, `wrangler.toml`, `README.md`, `AGENTS.md`, git remote. Confirm: "I'll register for `localhost`, `127.0.0.1`, and `<domain>`. OK?" **[wait for user]** If no production domain is found, ask.

6. **Codebase scan.** Detect framework + insertion candidates silently.

7. **Insertion plan.** Show the candidate list with `[recommended]` / `[skip by default]` markers; ask the user to confirm (numbers, "all", "recommended", or a list). **[wait for user]** If an existing CAPTCHA was detected, present a migration plan instead (see "Migrating from another CAPTCHA").

8. **Widget creation.** Run `scripts/widget-create.sh --account-id <id> --name <name> --domains <list> --mode managed`. Report the sitekey. The secret stays in env; never write it to disk.

9. **Worker deploy.** Run `scripts/worker-deploy.sh --name turnstile-siteverify-<project-slug>` with `WIDGET_SECRET` exported. Report the Worker URL on `status: ok`. On `set_secret_failed`, the Worker deployed but `TURNSTILE_SECRET_KEY` is not set on it; surface the error, then retry with `echo "$WIDGET_SECRET" | npx wrangler secret put TURNSTILE_SECRET_KEY --name <returned worker_name>` before running validation.

10. **Frontend edits.** State the contract: "I'll add the widget + gate the existing submit handler on `success === true`. The existing handler logic stays the same." Ask "yes" / "show". **[wait for user]** If "show", print unified diffs and ask again. Do NOT propose alternate behavior (mail delivery, custom backends).

11. **Validation.** Run `scripts/validate.sh`. Report each check as it passes. If any fails, surface the error and stop. **[wait for user if anything fails]**

12. **Persist skill.** Ask: "Save the Spin skill to `.claude/skills/turnstile-spin/SKILL.md` so I can reuse it on follow-up tasks?" Default yes. **[wait for user]** Then run `scripts/persist-skill.sh --path <agent-specific-path>`.

13. **Final report.** Print the structured summary: what was created, what was validated, what to do next.

### Things you must NOT do

- Do not write the Turnstile secret to disk. Only pass it via stdin to `wrangler secret put` (the worker-deploy.sh script handles this).
- Do not skip validation.
- Do not overwrite files without showing a diff.
- Do not deploy a Worker to a different account than the widget was created in.
- Do not call siteverify from the browser. Always: browser → user's Worker → siteverify.
- Do not use `sudo` or install global packages without asking.

### Hard scope boundary: DO NOT ask the user about

Spin validates the Turnstile token via a managed Worker before the user's existing form handler runs. Everything else is out of scope:

- **Email / SMS / notification delivery.** Leave the existing submit handler alone (just gate it on `success === true`). Don't propose Resend, Mailchannels, SMTP, mailto.
- **Custom Worker code.** Deploy the stock Worker template bundled at `templates/worker/`. Don't write a new Worker. Don't add features (rate limiting, custom routing, third-party integrations).
- **Database / payment / OAuth / form persistence.** Out of scope.
- **Frontend framework migration, refactoring, or styling.** Edit only what's needed.
- **reCAPTCHA v3 score thresholds.** Turnstile returns `success: true/false`.
- **Pre-clearance-only setups.** If `clearance_level !== no_clearance`, siteverify is optional and Spin doesn't apply. Redirect the user and exit.

### Recovery flow: respect existing widget configuration

When the user has Cloudflare dashboard access, the in-dashboard **Fix with Spin** banner is the preferred recovery path; it deploys the managed siteverify Worker server-side without requiring `wrangler` or an API token. This skill's recovery flow below is the fallback: use it when the user is driving from their editor without leaving it, or when the dashboard recovery does not apply (FedRAMP, gate-restricted account, etc.).

If the user tells you they already have a Turnstile widget set up and want to wire siteverify to it without rotating the sitekey (e.g. "I have a sitekey but siteverify never worked", "set up Spin against my existing widget `<sitekey>`"):

1. Skip Step 8 (widget creation). The sitekey already exists; get it from the user.
2. Fetch the widget metadata via `scripts/fetch-secret.sh --account-id <id> --sitekey <key>`. Branch on `status`:
   - `ok`: read `secret`, `clearance_level`, and `domains` from the response. Confirm `domains` includes the user's production hostname; if not, surface the gap before proceeding.
   - `missing_read_scope`: tell the user to add `Account.Turnstile:Read` to the token, or fall back to asking them to paste the secret. In the paste path, you do not have `clearance_level` or `domains`; ask the user to confirm both.
3. Check `clearance_level` from the response (or the user's answer):
   - `no_clearance`: standard recovery (deploy Worker, wire siteverify).
   - anything else: ask whether they want siteverify on top of pre-clearance, or exit per the scope boundary.
4. Continue from Step 9 (Worker deploy). Site key does not change. Dashboard's `Deployment` column flips from `Manual` to `Spin` on the first request carrying `data-action="turnstile-spin-v1"` (this skill) or `data-action="turnstile-spin-v2"` (dashboard "Set up with Spin" button).

If the user is recovering a widget that was created via the dashboard "Set up with Spin" button, a managed Worker is likely already deployed in the account. Confirm with the user whether they want a fresh Worker (proceed) or just need help wiring the frontend to the existing one (skip to Step 10 and ask for the existing Worker URL).
5. Never recreate the widget to get a fresh secret. That breaks the existing sitekey everywhere it's deployed.

### The frontend-edit contract

When wiring an existing form to the Worker (Step 10), the contract is: **gate, don't replace.** The user's existing submit handler keeps doing what it did. Spin only adds a validation step before it.

```js
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const token = /* read cf-turnstile-response */;
  const result = await fetch(WORKER_URL, { method: 'POST', body: JSON.stringify({ token }) });
  const data = await result.json();
  if (!data.success) return; // show failure
  // existing handler logic runs here, unchanged
});
```

If the existing handler was a stub, Spin leaves it a stub gated on success. The user can replace the stub later; that's not Spin's job.

## Migrating from another CAPTCHA

During the Step 6 codebase scan, also look for existing reCAPTCHA or hCaptcha. If found, switch Step 7 to a migration plan.

Detection signals:
- reCAPTCHA: `https://www.google.com/recaptcha/api.js`, `class="g-recaptcha"`, `data-sitekey="6L..."`, backend POST to `/recaptcha/api/siteverify`
- hCaptcha: `https://js.hcaptcha.com/1/api.js`, `class="h-captcha"`, backend POST to `https://hcaptcha.com/siteverify`

Substitution:
- Replace script tags with `https://challenges.cloudflare.com/turnstile/v0/api.js` (`async defer`).
- Replace `class="g-recaptcha"` / `class="h-captcha"` divs with `class="cf-turnstile"`, update `data-sitekey` to the new Turnstile sitekey, add `data-action="turnstile-spin-v1"`.
- Token field changes from `g-recaptcha-response` to `cf-turnstile-response`.
- Backend siteverify URL points at the Spin-deployed Worker. Drop `RECAPTCHA_SECRET` / `HCAPTCHA_SECRET` env vars.

Edge cases to surface to the user:
- **reCAPTCHA v3 score thresholds.** Turnstile has no score. Tell the user explicitly that migrated code will reject on `success === false`.
- **reCAPTCHA Enterprise.** Don't auto-migrate. Point at [developers.cloudflare.com/turnstile/migration/recaptcha/](https://developers.cloudflare.com/turnstile/migration/recaptcha/).
- **Custom `action=` values.** Preserve any custom action the user passed to `grecaptcha.execute` as `data-action` on the widget. Use `turnstile-spin-v1` only when no custom action exists.

## Edge cases

| Situation | Action |
|---|---|
| `wrangler` not installed | Install path: `npm install --save-dev wrangler` (Node project) or `npm install -g wrangler` (other) |
| Multiple Cloudflare accounts | `scripts/auth-probe.sh` returns all accounts; ask the user to choose, export `CLOUDFLARE_ACCOUNT_ID` |
| Cloudflare Pages project | Deploy the managed Worker anyway, OR suggest the [Pages Plugin](https://developers.cloudflare.com/pages/functions/plugins/turnstile/) |
| `EXPECTED_HOSTNAME` mismatch | Update widget domains via PUT, not PATCH (PATCH returns `10405 Method not allowed`): `curl -X PUT .../widgets/$SITEKEY -d '{"name":"...","mode":"managed","domains":[...]}'` |
| Worker name conflict | `worker-deploy.sh` retries automatically with a hash suffix |
| Token expired mid-flow | Stop, re-run `scripts/auth-probe.sh`, prompt for fresh credentials |
| Step 11 returns `missing-input-secret` | Secret didn't propagate. Re-set: `echo "$WIDGET_SECRET" \| npx wrangler secret put TURNSTILE_SECRET_KEY --name <worker_name from worker-deploy.sh output>`, wait 10s, re-validate. Use the `worker_name` field returned by `worker-deploy.sh`; do not rely on a `$WORKER_NAME` env var. |
| `worker-deploy.sh` returns `set_secret_failed` | Worker is deployed but secret is not set. Re-run only the secret-put using the returned `worker_name`: `echo "$WIDGET_SECRET" \| npx wrangler secret put TURNSTILE_SECRET_KEY --name <worker_name>`. Surface the `detail` field to the user — it carries the wrangler error. |

## Telemetry marker

Every snippet this skill writes must include `data-action="turnstile-spin-v1"`. Widgets created via the dashboard "Set up with Spin" button use `data-action="turnstile-spin-v2"` instead; preserve that marker if you encounter it on an existing widget you are modifying. Both feed the same account-level aggregate telemetry, never per-user. Cloudflare uses it to measure activation. If the user removes the attribute, the integration still works; only the analytics segmentation is lost.

## Do not

- Do not write the secret to disk.
- Do not skip validation (Step 11).
- Do not propose features outside the wizard (custom Worker code, custom domains, advanced WAF rules) unless asked.
- Do not call siteverify from the browser.
- Do not deploy the Worker into a different account than the widget.
