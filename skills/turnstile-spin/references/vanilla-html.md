# Vanilla HTML

For static sites or any project without a JS framework. The form posts directly to the Worker, no client-side JavaScript required for the integration itself.

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
		<form action="https://YOUR_WORKER_URL/" method="POST">
			<input name="email" type="email" required />
			<div
				class="cf-turnstile"
				data-sitekey="YOUR_SITEKEY"
				data-action="turnstile-spin-v1"
			></div>
			<button type="submit">Subscribe</button>
		</form>
	</body>
</html>
```

When the form is submitted, the browser includes `cf-turnstile-response` automatically. The Worker reads it (alias for `token`) and responds with siteverify JSON.

## Where to put the snippet

- Single-page site: in the `<body>` of `index.html`, wherever the form lives.
- Multi-page site: in each page that has a form. The script tag in `<head>` can live in a shared layout.

## Substitutions

| Placeholder        | Replace with                                            |
| ------------------ | ------------------------------------------------------- |
| `YOUR_WORKER_URL`  | The deployed Worker URL from Step 5                     |
| `YOUR_SITEKEY`     | The widget site key from Step 4                         |

## Variant: AJAX submit instead of form action

If the form is submitted via `fetch` instead of a native form post, the snippet still works. The widget div populates a hidden `cf-turnstile-response` input that you can read from `new FormData(form)`.

```html
<script>
	document.querySelector("form").addEventListener("submit", async (e) => {
		e.preventDefault();
		const data = new FormData(e.target);
		const res = await fetch("https://YOUR_WORKER_URL/", {
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
