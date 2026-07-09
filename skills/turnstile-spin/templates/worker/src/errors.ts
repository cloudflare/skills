/**
 * Error formatting + helpers. Keep error responses consistent with
 * Cloudflare's documented siteverify shape so callers can use one handler.
 */

import type { ErrorCode, SiteverifyResponse } from './types.js';

export class SiteverifyError extends Error {
	constructor(
		public readonly status: number,
		public readonly code: ErrorCode,
		message: string,
	) {
		super(message);
		this.name = 'SiteverifyError';
	}
}

/** Build a siteverify-shaped response for a Worker-level failure. */
export function errorResponse(code: ErrorCode, durationMs: number, workerVersion: string): SiteverifyResponse {
	return {
		success: false,
		'error-codes': [code],
		_worker: {
			duration_ms: durationMs,
			worker_version: workerVersion,
		},
	};
}
