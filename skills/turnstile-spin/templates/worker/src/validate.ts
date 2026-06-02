/**
 * Calls Cloudflare's siteverify endpoint. One retry on transient (5xx + network)
 * failures, with a tight timeout. Returns the upstream JSON unmodified plus
 * Worker metadata.
 */

import { SiteverifyError } from './errors.js';
import type { Env, SiteverifyRequest, SiteverifyResponse } from './types.js';

const SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';
const UPSTREAM_TIMEOUT_MS = 5000;
const RETRY_ON_STATUSES = new Set([500, 502, 503, 504]);

export interface ValidateResult {
	response: SiteverifyResponse;
	upstreamStatus: number;
	durationMs: number;
}

/**
 * Validate a Turnstile token against Cloudflare's siteverify endpoint.
 *
 * @throws SiteverifyError on Worker-level failures (missing secret, unreachable upstream, timeout)
 */
export async function validate(req: SiteverifyRequest, env: Env, workerVersion: string): Promise<ValidateResult> {
	if (!env.TURNSTILE_SECRET_KEY) {
		throw new SiteverifyError(500, 'missing-input-secret', 'TURNSTILE_SECRET_KEY not configured');
	}
	if (!req.token) {
		throw new SiteverifyError(400, 'missing-token', 'token is required');
	}

	const body = new FormData();
	body.append('secret', env.TURNSTILE_SECRET_KEY);
	body.append('response', req.token);
	if (req.remoteip) body.append('remoteip', req.remoteip);
	if (req.idempotency_key) body.append('idempotency_key', req.idempotency_key);

	const start = Date.now();
	let lastErr: unknown = null;
	for (let attempt = 0; attempt < 2; attempt++) {
		try {
			const result = await fetchWithTimeout(SITEVERIFY_URL, body, UPSTREAM_TIMEOUT_MS);
			const durationMs = Date.now() - start;
			if (result.status >= 200 && result.status < 300) {
				const data = (await result.json()) as SiteverifyResponse;
				data._worker = {
					duration_ms: durationMs,
					worker_version: workerVersion,
				};
				// Hostname-mismatch defense. If the customer set EXPECTED_HOSTNAME,
				// reject responses whose hostname doesn't match — defends against
				// cross-site token replay even if a token leaks.
				if (data.success && env.EXPECTED_HOSTNAME && data.hostname && data.hostname !== env.EXPECTED_HOSTNAME) {
					const rejected: SiteverifyResponse = {
						...data,
						success: false,
						'error-codes': ['hostname-mismatch'],
					};
					return { response: rejected, upstreamStatus: result.status, durationMs };
				}
				return { response: data, upstreamStatus: result.status, durationMs };
			}
			if (!RETRY_ON_STATUSES.has(result.status) || attempt === 1) {
				// Don't retry on 4xx, return the upstream body as-is so customers
				// see exactly what siteverify said.
				const data = (await result.json().catch(() => ({}))) as Partial<SiteverifyResponse>;
				const response: SiteverifyResponse = {
					success: false,
					'error-codes': data['error-codes'] ?? ['bad-request'],
					...data,
					_worker: { duration_ms: durationMs, worker_version: workerVersion },
				};
				return { response, upstreamStatus: result.status, durationMs };
			}
			// 5xx + first attempt: retry
		} catch (err) {
			lastErr = err;
			if (attempt === 1) break;
		}
	}

	if (lastErr instanceof DOMException && lastErr.name === 'AbortError') {
		throw new SiteverifyError(504, 'upstream-timeout', `Upstream timeout after ${UPSTREAM_TIMEOUT_MS}ms`);
	}
	throw new SiteverifyError(502, 'upstream-unreachable', `Upstream siteverify unreachable: ${String(lastErr)}`);
}

async function fetchWithTimeout(url: string, body: FormData, timeoutMs: number): Promise<Response> {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, {
			method: 'POST',
			body,
			signal: controller.signal,
		});
	} finally {
		clearTimeout(timer);
	}
}
