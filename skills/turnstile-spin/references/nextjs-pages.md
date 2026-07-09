# Next.js (Pages Router)

For older Next.js projects using `pages/` rather than `app/`. The form posts directly to the Worker; no React state required.

```tsx title="pages/signup.tsx"
import Script from "next/script";

export default function SignupPage() {
	return (
		<>
			<Script src="https://challenges.cloudflare.com/turnstile/v0/api.js" />
			<form action="https://YOUR_WORKER_URL/" method="POST">
				<input name="email" type="email" required />
				<div
					className="cf-turnstile"
					data-sitekey="YOUR_SITEKEY"
					data-action="turnstile-spin-v1"
				/>
				<button type="submit">Sign up</button>
			</form>
		</>
	);
}
```

## Variant: API route on your own backend

If you want to call siteverify from your own API route (e.g. you have application logic between siteverify and the actual signup), proxy the call through `pages/api/signup.ts`:

```ts title="pages/api/signup.ts"
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
	req: NextApiRequest,
	res: NextApiResponse,
) {
	const token = req.body["cf-turnstile-response"] ?? req.body.token;
	const verify = await fetch("https://YOUR_WORKER_URL/", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ token }),
	});
	const data = await verify.json();
	if (!data.success) {
		return res.status(403).json({ error: "Verification failed" });
	}
	// process signup
	return res.json({ ok: true });
}
```

Note: This pattern uses the Spin Worker as a siteverify proxy from your Node backend. It still works, just adds a hop. For pure SPA-style forms, the direct-post pattern above is simpler.

## Substitutions

| Placeholder        | Replace with                                |
| ------------------ | ------------------------------------------- |
| `YOUR_WORKER_URL`  | Deployed Worker URL from Step 5             |
| `YOUR_SITEKEY`     | Widget site key from Step 4                 |
