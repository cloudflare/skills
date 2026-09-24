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
				data-action="subscribe"
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
const expectedHostnames = new Set(
	(process.env.TURNSTILE_HOSTNAMES ?? '')
		.split(',')
		.map((h) => h.trim())
		.filter(Boolean),
);
const token = req.body['cf-turnstile-response'];
if (typeof token !== 'string' || token.length === 0 || token.length > 2048 || expectedHostnames.size === 0) {
	return res.status(403).end();
}

let result;
try {
	const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		signal: AbortSignal.timeout(10_000),
		body: new URLSearchParams({
			secret: process.env.TURNSTILE_SECRET,
			response: token,
			remoteip: req.ip,
		}),
	});
	if (!r.ok) throw new Error('Siteverify failed');
	result = await r.json();
} catch {
	return res.status(403).end();
}
if (
	result?.success !== true ||
	result.action !== 'subscribe' ||
	!expectedHostnames.has(result.hostname)
) {
	return res.status(403).end();
}
// existing handler logic runs here
```

Equivalent calls in other backend languages (each also compares `result.hostname` to a `TURNSTILE_HOSTNAMES` allowlist):

```ruby
# Ruby
require 'net/http'; require 'uri'; require 'json'; require 'set'; require 'openssl'
expected_hostnames = (ENV['TURNSTILE_HOSTNAMES'] || '').split(',').map(&:strip).reject(&:empty?).to_set
token = params['cf-turnstile-response']
halt 403 if !token.is_a?(String) || token.empty? || token.length > 2048 || expected_hostnames.empty?
begin
  uri = URI('https://challenges.cloudflare.com/turnstile/v0/siteverify')
  req = Net::HTTP::Post.new(uri)
  req.set_form_data(secret: ENV['TURNSTILE_SECRET'], response: token, remoteip: request.ip)
  res = Net::HTTP.start(uri.host, uri.port, use_ssl: true, open_timeout: 10, read_timeout: 10) { |http| http.request(req) }
  halt 403 unless res.is_a?(Net::HTTPSuccess)
  result = JSON.parse(res.body)
rescue SocketError, SystemCallError, Timeout::Error, IOError, OpenSSL::SSL::SSLError, JSON::ParserError
  halt 403
end
halt 403 unless result.is_a?(Hash) && result['success'] == true && result['action'] == 'subscribe' && expected_hostnames.include?(result['hostname'])
```

```python
# Python (requests)
expected_hostnames = {h.strip() for h in os.environ.get('TURNSTILE_HOSTNAMES', '').split(',') if h.strip()}
token = form.get('cf-turnstile-response')
if not isinstance(token, str) or not token or len(token) > 2048 or not expected_hostnames:
    return '', 403
try:
    r = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify',
        data={'secret': os.environ['TURNSTILE_SECRET'],
              'response': token,
              'remoteip': request.remote_addr},
        timeout=10)
    r.raise_for_status()
    result = r.json()
except (requests.RequestException, ValueError):
    return '', 403
if (not isinstance(result, dict) or result.get('success') is not True or result.get('action') != 'subscribe'
        or result.get('hostname') not in expected_hostnames):
    return '', 403
```

`subscribe` is the stable action for this surface. Preserve an existing custom migration action and compare the returned action to the same value. Siteverify is mandatory for every widget mode, including pre-clearance. Set `TURNSTILE_HOSTNAMES` to the deployment-specific frontend hostnames; a production value must not include `localhost` or `127.0.0.1`.

## Variant: AJAX submit instead of form action

For an AJAX flow, replace the native form and API script with explicit rendering. Keep this surface's widget ID and reset it in `finally`, which covers network, JSON, validation, and server failures as well as successful same-page completion.

```html
<form id="subscribe-form">
	<input name="email" type="email" required />
	<div id="subscribe-turnstile"></div>
	<button type="submit">Subscribe</button>
</form>
<script>
	let subscribeWidgetId;

	window.onSubscribeTurnstileLoad = () => {
		subscribeWidgetId = window.turnstile.render("#subscribe-turnstile", {
			sitekey: "YOUR_SITEKEY",
			action: "subscribe",
		});
	};

	document.getElementById("subscribe-form").addEventListener("submit", async (event) => {
		event.preventDefault();
		try {
			const res = await fetch("/api/subscribe", {
				method: "POST",
				body: new FormData(event.currentTarget),
			});
			const json = await res.json();
			if (!res.ok || json.ok !== true) throw new Error("Submission failed");
			// proceed
		} catch {
			// surface the error
		} finally {
			if (subscribeWidgetId !== undefined) {
				window.turnstile.reset(subscribeWidgetId);
			}
		}
	});
</script>
<script
	src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onSubscribeTurnstileLoad&render=explicit"
	async
	defer
></script>
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
