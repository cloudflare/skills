# Hugo

For Hugo static sites. Use a partial for the widget so it can be referenced from any layout or content file.

```html title="layouts/partials/turnstile.html"
<script
	src="https://challenges.cloudflare.com/turnstile/v0/api.js"
	async
	defer
></script>

<form action="{{ .Site.Params.turnstileWorkerUrl }}/" method="POST">
	<input name="email" type="email" required />
	<div
		class="cf-turnstile"
		data-sitekey="{{ .Site.Params.turnstileSitekey }}"
		data-action="turnstile-spin-v1"
	></div>
	<button type="submit">Subscribe</button>
</form>
```

Add the params to your site config:

```toml title="hugo.toml"
[params]
turnstileSitekey = "YOUR_SITEKEY"
turnstileWorkerUrl = "https://YOUR_WORKER_URL"
```

Reference the partial from any layout or content file:

```text
{{ partial "turnstile.html" . }}
```

## Variant: shortcode for content files

If you want to drop the widget into Markdown content (not just layouts), create a shortcode:

```html title="layouts/shortcodes/turnstile-form.html"
{{ partial "turnstile.html" . }}
```

Use in content:

```markdown title="content/contact.md"
---
title: Contact
---

Contact us:

{{< turnstile-form >}}
```

## Substitutions

| Placeholder        | Replace with                                |
| ------------------ | ------------------------------------------- |
| `YOUR_WORKER_URL`  | Deployed Worker URL from Step 5             |
| `YOUR_SITEKEY`     | Widget site key from Step 4                 |
