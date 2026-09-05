# Integration contract

All `scripts/` paths in commands refer to the skill bundle root; resolve them there, while project inspection and configuration target the user's project.

Canonical server-side siteverify (Node / fetch idiom; adapt to the detected backend):

```js
const expectedAction = 'signup';
const expectedHostnames = new Set(
  (process.env.TURNSTILE_HOSTNAMES ?? '')
    .split(',')
    .map((hostname) => hostname.trim())
    .filter(Boolean),
);

if (typeof token !== 'string' || token.length === 0 || token.length > 2048 || expectedHostnames.size === 0) {
  return res.status(403).send('forbidden');
}

let result;
try {
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    signal: AbortSignal.timeout(10_000),
    body: new URLSearchParams({
      secret: process.env.TURNSTILE_SECRET,
      response: token,         // cf-turnstile-response from the request
      remoteip: clientIp,      // X-Forwarded-For / req.ip / etc.
    }),
  });
  if (!r.ok) throw new Error(`siteverify ${r.status}`);
  result = await r.json();
} catch (err) {
  // Network error, non-2xx, or non-JSON body from siteverify. Fail closed.
  return res.status(403).send('forbidden');  // adapt to your framework
}
if (
  !result.success ||
  result.action !== expectedAction ||
  !expectedHostnames.has(result.hostname)
) {
  return res.status(403).send('forbidden');
}
// existing handler logic runs here, unchanged
```

Set `TURNSTILE_HOSTNAMES` to the deployment-specific frontend hostnames. A production value must not include `localhost` or `127.0.0.1`. Write the secret into the user's existing secret store (`.env` for Node/Rails/Python, standard `"$WRANGLER_BIN" secret put TURNSTILE_SECRET` for a confirmed existing Worker, or the platform's secret manager). Before writing to any `.env`-style file, run `git check-ignore -q <path>` from within a git working tree; if the file is not ignored (or the project is not under git), stop and ask the user to add it to `.gitignore` or point you at the platform's secret manager. For Workers, resolve the exact name, configuration, and environment, then run `secret list` with the same target arguments immediately before the write. Never inline the secret or ask the user to paste it into chat. For an existing widget, follow the [guarded existing-widget retrieval flow](existing-widget.md).


## The frontend-edit contract

When wiring an existing form or user-triggered endpoint (creation Step 9), the contract is: **gate, don't replace.** The user's existing handler keeps doing what it did. Spin only adds a validation step before it.

Frontend (embeds the widget; submits to the user's existing endpoint):

```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>

<form action="/signup" method="POST">
  <!-- existing inputs unchanged -->
  <div class="cf-turnstile" data-sitekey="<SITEKEY>" data-action="signup"></div>
  <button type="submit">Sign up</button>
</form>
```

Backend: use the canonical siteverify fetch above inside the existing handler. Read the token from `req.body['cf-turnstile-response']`, require `success === true`, compare `action` with the surface's action, compare `hostname` with the deployment-specific frontend hostname allowlist, and leave the rest of the handler alone. If the existing handler was a stub, Spin leaves it a stub gated on those checks. The user can replace the stub later; that's not Spin's job.

**Token lifecycle: tokens are single-use.** A `cf-turnstile-response` token is redeemed exactly once at Siteverify. A native form that navigates away does not need reset logic. If the page remains active after a submission attempt, render the widget explicitly, retain that widget's ID, and call `window.turnstile.reset(widgetId)` after the request completes before allowing a retry. Each protected surface must retain and reset its own widget ID. The framework references show the appropriate lifecycle hook.


## Framework snippets

Read the snippet matching the detected frontend:

- [vanilla-html](vanilla-html.md)
- [nextjs-app](nextjs-app.md)
- [nextjs-pages](nextjs-pages.md)
- [astro](astro.md)
- [sveltekit](sveltekit.md)
- [hugo](hugo.md)
