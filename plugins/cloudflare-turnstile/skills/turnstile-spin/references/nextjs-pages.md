# Next.js (Pages Router)

For older Next.js projects using `pages/` rather than `app/`. The widget renders client-side; siteverify lives in the API route.

```tsx title="pages/signup.tsx"
import Script from "next/script";

export default function SignupPage() {
	return (
		<>
			<Script src="https://challenges.cloudflare.com/turnstile/v0/api.js" />
			<form action="/api/signup" method="POST">
				<input name="email" type="email" required />
				<div
					className="cf-turnstile"
					data-sitekey="YOUR_SITEKEY"
					data-action="turnstile-spin-v2"
				/>
				<button type="submit">Sign up</button>
			</form>
		</>
	);
}
```

API route (canonical siteverify):

```ts title="pages/api/signup.ts"
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
	req: NextApiRequest,
	res: NextApiResponse,
) {
	const token = req.body["cf-turnstile-response"] ?? req.body.token;
	const remoteip =
		(req.headers["x-forwarded-for"] as string | undefined)?.split(",")[0] ??
		req.socket.remoteAddress;

	const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			secret: process.env.TURNSTILE_SECRET!,
			response: token,
			...(remoteip ? { remoteip } : {}),
		}),
	});
	const data = await verify.json();
	if (!data.success) {
		return res.status(403).json({ error: "Verification failed" });
	}
	// process signup
	return res.json({ ok: true });
}
```

## Substitutions

| Placeholder         | Replace with                                                         |
| ------------------- | -------------------------------------------------------------------- |
| `YOUR_SITEKEY`      | The widget site key from Step 8                                      |
| `TURNSTILE_SECRET`  | Env-var name. Value is the secret captured in Step 8, kept off disk. |
