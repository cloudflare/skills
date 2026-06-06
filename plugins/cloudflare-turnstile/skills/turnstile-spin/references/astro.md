# Astro

For Astro projects. The widget renders in a page; siteverify lives in an Astro Action, an API route, or a Pages Function. Astro frontmatter reads the sitekey from env at build time; the secret stays server-only.

```astro title="src/pages/signup.astro"
---
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
		<form action="/api/signup" method="POST">
			<input name="email" type="email" required />
			<div
				class="cf-turnstile"
				data-sitekey={SITEKEY}
				data-action="turnstile-spin-v2"
			/>
			<button type="submit">Sign up</button>
		</form>
	</body>
</html>
```

In your `.env`:

```text
PUBLIC_TURNSTILE_SITEKEY=YOUR_SITEKEY
TURNSTILE_SECRET=YOUR_SECRET
```

The `PUBLIC_` prefix is mandatory for client-exposed variables in Astro. The secret has **no** prefix; it stays server-only.

## API route (canonical siteverify)

```ts title="src/pages/api/signup.ts"
import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ request, clientAddress }) => {
	const form = await request.formData();
	const token = form.get("cf-turnstile-response") as string;

	const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			secret: import.meta.env.TURNSTILE_SECRET,
			response: token,
			remoteip: clientAddress,
		}),
	});
	const { success } = await verify.json();
	if (!success) return new Response("forbidden", { status: 403 });

	// process signup
	return Response.json({ ok: true });
};
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
		handler: async (input, ctx) => {
			const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
				method: "POST",
				headers: { "Content-Type": "application/x-www-form-urlencoded" },
				body: new URLSearchParams({
					secret: import.meta.env.TURNSTILE_SECRET,
					response: input["cf-turnstile-response"],
					remoteip: ctx.clientAddress,
				}),
			});
			const data = await verify.json();
			if (!data.success) throw new Error("Verification failed");
			// process signup
		},
	}),
};
```

## Substitutions

| Placeholder         | Replace with                                                         |
| ------------------- | -------------------------------------------------------------------- |
| `YOUR_SITEKEY`      | The widget site key from Step 8                                      |
| `YOUR_SECRET`       | The secret captured in Step 8. Stays in env, never inlined.          |
