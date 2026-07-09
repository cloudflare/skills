# Astro

For Astro projects. The form posts directly to the Worker. Astro frontmatter handles config substitution at build time.

```astro title="src/pages/signup.astro"
---
const WORKER_URL = import.meta.env.PUBLIC_TURNSTILE_WORKER_URL;
const SITEKEY = import.meta.env.PUBLIC_TURNSTILE_SITEKEY;
---

<html>
	<head>
		<script
			src="https://challenges.cloudflare.com/turnstile/v0/api.js"
			async
			defer
		></script>
	</head>
	<body>
		<form action={`${WORKER_URL}/`} method="POST">
			<input name="email" type="email" required />
			<div
				class="cf-turnstile"
				data-sitekey={SITEKEY}
				data-action="turnstile-spin-v1"
			/>
			<button type="submit">Sign up</button>
		</form>
	</body>
</html>
```

In your `.env`:

```text
PUBLIC_TURNSTILE_WORKER_URL=https://YOUR_WORKER_URL
PUBLIC_TURNSTILE_SITEKEY=YOUR_SITEKEY
```

The `PUBLIC_` prefix is mandatory for client-exposed variables in Astro.

## Variant: hardcoded values

If you do not use env vars, inline directly:

```astro title="src/pages/signup.astro"
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
			<div
				class="cf-turnstile"
				data-sitekey="YOUR_SITEKEY"
				data-action="turnstile-spin-v1"
			/>
			<button type="submit">Sign up</button>
		</form>
	</body>
</html>
```

## Variant: Astro Actions

If the project uses Astro Actions, call siteverify from the action:

```ts title="src/actions/index.ts"
import { defineAction } from "astro:actions";
import { z } from "astro:schema";

export const server = {
	signup: defineAction({
		accept: "form",
		input: z.object({
			email: z.string().email(),
			"cf-turnstile-response": z.string(),
		}),
		handler: async (input) => {
			const verify = await fetch("https://YOUR_WORKER_URL/", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ token: input["cf-turnstile-response"] }),
			});
			const data = await verify.json();
			if (!data.success) throw new Error("Verification failed");
			// process signup
		},
	}),
};
```

## Substitutions

| Placeholder        | Replace with                                |
| ------------------ | ------------------------------------------- |
| `YOUR_WORKER_URL`  | Deployed Worker URL from Step 5             |
| `YOUR_SITEKEY`     | Widget site key from Step 4                 |
