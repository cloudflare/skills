# Vanilla HTML

For static sites or any project without a JS framework. The widget renders client-side; the form submits to whatever backend handles your form (a Node/PHP/Ruby/Go server, a Cloudflare Worker, a Pages Function, a third-party form host that supports server-side hooks, etc.).

```html
<!doctype html>
<html>
	<head>
		<script
			src="https://challenges.cloudflare.com/turnstile/v0/api.js"
			async
			defer
		></script>
	</head>
	<body>
		<form action="/api/subscribe" method="POST">
			<input name="email" type="email" required />
			<div
				class="cf-turnstile"
				data-sitekey="YOUR_SITEKEY"
				data-action="turnstile-spin-v2"
			></div>
			<button type="submit">Subscribe</button>
		</form>
	</body>
</html>
```

When the form submits, the browser includes `cf-turnstile-response` automatically. Your backend reads it and calls canonical siteverify.

## Backend (any language)

Add this to your existing `/api/subscribe` handler before the rest of its logic:

```js
// Node / fetch idiom
const token = req.body['cf-turnstile-response'];
const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
	method: 'POST',
	headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
	body: new URLSearchParams({
		secret: process.env.TURNSTILE_SECRET,
		response: token,
		remoteip: req.ip,
	}),
});
const { success } = await r.json();
if (!success) return res.status(403).end();
// existing handler logic runs here
```

Equivalent calls in other backend languages:

```ruby
# Ruby
require 'net/http'; require 'uri'; require 'json'
res = Net::HTTP.post_form(URI('https://challenges.cloudflare.com/turnstile/v0/siteverify'),
  secret: ENV['TURNSTILE_SECRET'], response: params['cf-turnstile-response'], remoteip: request.ip)
halt 403 unless JSON.parse(res.body)['success']
```

```python
# Python (requests)
r = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify',
    data={'secret': os.environ['TURNSTILE_SECRET'],
          'response': form['cf-turnstile-response'],
          'remoteip': request.remote_addr})
if not r.json()['success']:
    return '', 403
```

## Variant: AJAX submit instead of form action

If the form is submitted via `fetch` instead of a native form post, the snippet still works. The widget div populates a hidden `cf-turnstile-response` input that you can read from `new FormData(form)`.

```html
<script>
	document.querySelector("form").addEventListener("submit", async (e) => {
		e.preventDefault();
		const data = new FormData(e.target);
		const res = await fetch("/api/subscribe", {
			method: "POST",
			body: data,
		});
		const json = await res.json();
		if (json.success) {
			// proceed
		}
	});
</script>
```

## No backend?

If your project is pure-static (no server-side handler — just HTML served from a CDN), Spin doesn't apply. Siteverify is server-side by design. Options:

- Add a Cloudflare Pages Function (`functions/api/subscribe.js`) to host the siteverify call.
- Deploy a tiny Cloudflare Worker that does siteverify against your existing form host.
- Use a third-party form host that exposes a server-side webhook where you can wire siteverify.

## Substitutions

| Placeholder         | Replace with                                                         |
| ------------------- | -------------------------------------------------------------------- |
| `YOUR_SITEKEY`      | The widget site key from Step 8                                      |
| `/api/subscribe`    | The path to your existing form-handling endpoint                     |
| `TURNSTILE_SECRET`  | Env-var name. Value is the secret captured in Step 8, kept off disk. |
