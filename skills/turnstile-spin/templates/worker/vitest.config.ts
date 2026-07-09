import { defineConfig } from 'vitest/config';

export default defineConfig({
	test: {
		globals: true,
		// We run unit tests under Node (mocking fetch) and integration tests
		// hit real network. Workers test pool would let us run against the
		// real Workers runtime; defer that to fast-follow.
		environment: 'node',
		include: ['test/**/*.test.ts'],
	},
});
