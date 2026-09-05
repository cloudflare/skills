---
name: web-perf
description: Analyzes web performance using Chrome DevTools MCP. Measures Core Web Vitals (LCP, INP, CLS) and supplementary metrics (FCP, TBT, Speed Index), identifies render-blocking resources, network dependency chains, layout shifts, caching issues, and accessibility gaps. Use when asked to audit, profile, debug, or optimize page load performance, Lighthouse scores, or site speed. Biases towards retrieval from current documentation over pre-trained knowledge.
---

# Web Performance

Your knowledge of web performance metrics, thresholds, and tooling APIs may be outdated. **Prefer retrieval over pre-training** when citing specific numbers or recommendations.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| web.dev | `https://web.dev/articles/vitals` | Core Web Vitals thresholds, definitions |
| Chrome DevTools docs | `https://developer.chrome.com/docs/devtools/performance` | Tooling APIs, trace analysis |
| Lighthouse scoring | `https://developer.chrome.com/docs/lighthouse/performance/performance-scoring` | Score weights, metric thresholds |

## Choose the Work and Evidence

Match the workflow to the request:

- **Audit:** investigate the requested pages and user journeys, then deliver prioritized findings supported by measurements or inspected code.
- **Diagnose:** trace the reported symptom to its cause. Investigate other areas only when the evidence points there.
- **Optimize or fix:** diagnose, implement authorized changes, verify the affected behavior, and remeasure. Recommendations alone do not complete an implementation request.

Discover available browser and performance tool capabilities and inspect their schemas before calling them. The Chrome DevTools examples below apply only when those tools are available; use the actual tool names and parameters exposed by the environment.

If Chrome DevTools MCP is unavailable, continue with a capable browser tool, supplied traces, Lighthouse reports, or source and build output as appropriate. Source inspection can establish implementation defects but cannot establish measured runtime improvements. Ask for missing access or a measurement artifact only when it blocks the remaining work, and complete independent analysis or edits meanwhile. Do not invent metrics or require a tool installation merely to begin.

## Key Guidelines

- **Ground findings**: Verify claims against network requests, DOM, traces, or code. Distinguish measured results, tool estimates, and hypotheses requiring runtime validation.
- **Verify before recommending**: Confirm something is unused before suggesting removal.
- **Quantify impact**: Use estimated savings from insights. Don't prioritize changes with 0ms impact.
- **Skip non-issues**: If render-blocking resources have 0ms estimated impact, note but don't recommend action.
- **Be specific**: Say "compress hero.png (450KB) to WebP" not "optimize images".
- **Prioritize relevant impact**: Do not infer overall performance from one fast load; evaluate the pages, devices, and interactions covered by the request.

## Quick Reference

| Task | Tool Call |
|------|-----------|
| Load page | `navigate_page(url: "...")` |
| Start trace | `performance_start_trace(autoStop: true, reload: true)` |
| Analyze insight | `performance_analyze_insight(insightSetId: "...", insightName: "...")` |
| List requests | `list_network_requests(resourceTypes: ["Script", "Stylesheet", ...])` |
| Request details | `get_network_request(reqid: <id>)` |
| A11y snapshot | `take_snapshot(verbose: true)` |

## Investigation Options

Select the checks that can resolve the requested question; these are not mandatory phases. A broad audit may use several, while a targeted fix may need only a trace and the affected source. Record a baseline before editing when the runtime is available. Note the page or journey, build, viewport, device/CPU and network settings, and cache state so later measurements are comparable.

### Performance Trace

1. Navigate to the target URL:
   ```
   navigate_page(url: "<target-url>")
   ```

2. Start a performance trace for the relevant load or interaction. For a reload trace:
   ```
   performance_start_trace(autoStop: true, reload: true)
   ```

3. Wait for trace completion, then retrieve results. A reload alone does not establish a cold cache; explicitly control cache state when comparing cold loads. For interaction responsiveness, record the affected interaction rather than inferring it from load metrics.

**Troubleshooting:**
- If trace returns empty or fails, verify the page loaded correctly with `navigate_page` first
- If insight names don't match, inspect the trace response to list available insights

### Core Web Vitals Analysis

Use available trace insights to investigate the relevant metrics. Keep lab measurements separate from field data and identify their source. A load trace without representative interactions cannot establish INP; do not substitute TBT for it.

**Note:** Insight names may vary across Chrome DevTools versions. If an insight name doesn't work, check the `insightSetId` from the trace response to discover available insights.

Common insight names:

| Metric | Insight Name | What to Look For |
|--------|--------------|------------------|
| LCP | `LCPBreakdown` | Time to largest contentful paint; breakdown of TTFB, resource load, render delay |
| CLS | `CLSCulprits` | Elements causing layout shifts (images without dimensions, injected content, font swaps) |
| Render Blocking | `RenderBlocking` | CSS/JS blocking first paint |
| Document Latency | `DocumentLatency` | Server response time issues |
| Network Dependencies | `NetworkRequestsDepGraph` | Request chains delaying critical resources |

Example:
```
performance_analyze_insight(insightSetId: "<id-from-trace>", insightName: "LCPBreakdown")
```

**Key thresholds (good/needs-improvement/poor):**
- TTFB: < 800ms / < 1.8s / > 1.8s
- FCP: < 1.8s / < 3s / > 3s
- LCP: < 2.5s / < 4s / > 4s
- INP: < 200ms / < 500ms / > 500ms
- TBT: < 200ms / < 600ms / > 600ms
- CLS: < 0.1 / < 0.25 / > 0.25
- Speed Index: < 3.4s / < 5.8s / > 5.8s

### Network Analysis

Inspect the relevant network requests to identify optimization opportunities:
```
list_network_requests(resourceTypes: ["Script", "Stylesheet", "Document", "Font", "Image"])
```

**Look for:**

1. **Render-blocking resources**: JS/CSS in `<head>` without `async`/`defer`/`media` attributes
2. **Network chains**: Resources discovered late because they depend on other resources loading first (e.g., CSS imports, JS-loaded fonts)
3. **Missing preloads**: Critical resources (fonts, hero images, key scripts) not preloaded
4. **Caching issues**: Missing or weak `Cache-Control`, `ETag`, or `Last-Modified` headers
5. **Large payloads**: Uncompressed or oversized JS/CSS bundles
6. **Unused preconnects**: Check whether the origin is used in the relevant loads or interactions before removing a hint. No request in one trace does not prove it is unused across the application. If requests exist but load late, the preconnect may still be valuable.

For detailed request info:
```
get_network_request(reqid: <id>)
```

### DOM and Accessibility Checks

Use a DOM or accessibility snapshot when it helps locate shifting elements, inspect the affected controls, or verify that a performance change preserves usability. Run a broader accessibility audit when requested. An accessibility tree can reveal missing names or structural issues, but contrast and keyboard behavior require appropriate visual/style inspection or interaction checks; do not claim those checks from a snapshot alone.

### Codebase Analysis

**Skip if auditing a third-party site without codebase access.**

Inspect the code responsible for the observed bottleneck. Broaden into framework or bundler configuration when the evidence calls for it.

#### Detect Framework & Bundler

Search for configuration files to identify the stack:

| Tool | Config Files |
|------|--------------|
| Webpack | `webpack.config.js`, `webpack.*.js` |
| Vite | `vite.config.js`, `vite.config.ts` |
| Rollup | `rollup.config.js`, `rollup.config.mjs` |
| esbuild | `esbuild.config.js`, build scripts with `esbuild` |
| Parcel | `.parcelrc`, `package.json` (parcel field) |
| Next.js | `next.config.js`, `next.config.mjs` |
| Nuxt | `nuxt.config.js`, `nuxt.config.ts` |
| SvelteKit | `svelte.config.js` |
| Astro | `astro.config.mjs` |

Also check `package.json` for framework dependencies and build scripts.

#### Tree-Shaking & Dead Code

- **Webpack**: Check for `mode: 'production'`, `sideEffects` in package.json, `usedExports` optimization
- **Vite/Rollup**: Tree-shaking enabled by default; check for `treeshake` options
- **Look for**: Barrel files (`index.js` re-exports), large utility libraries imported wholesale (lodash, moment)

#### Unused JS/CSS

- Check for CSS-in-JS vs. static CSS extraction
- Look for PurgeCSS/UnCSS configuration (Tailwind's `content` config)
- Identify dynamic imports vs. eager loading

#### Polyfills

- Check for `@babel/preset-env` targets and `useBuiltIns` setting
- Look for `core-js` imports (often oversized)
- Check `browserslist` config for overly broad targeting

#### Compression & Minification

- Check for `terser`, `esbuild`, or `swc` minification
- Look for gzip/brotli compression in build output or server config
- Check for source maps in production builds (should be external or disabled)

## Complete an Optimization or Fix

Implement the supported changes within the user's requested scope. Preserve application behavior and accessibility, and honor an explicit request to review before edits. Do not stop after presenting proposed fixes when implementation is authorized.

Run the checks relevant to the change: exercise the affected page or interaction and use the project's build or tests where they can catch regressions. Fix regressions caused by the change and repeat the affected checks without asking for approval at each iteration.

Remeasure against the baseline using comparable page content, journey, build mode, device, throttling, and cache conditions. When run-to-run variation makes a claimed gain uncertain, repeat enough comparable runs to assess it; report variability instead of claiming precision the evidence does not support. Investigate unexpected regressions and revise or revert the responsible change before reporting completion.

If runtime access or representative measurement is unavailable, complete the supported local changes and checks, then state exactly which behavior or performance claim remains unverified. Report measured results separately from expected improvements and do not label an implementation end-to-end verified while those checks are pending.

## Report the Result

For an audit or diagnosis, lead with the supported findings, their evidence, and prioritized next actions. Include only relevant measured metrics; identify whether values are lab or field data and whether savings are estimates.

For an optimization or fix, lead with what changed and why. Include comparable before/after measurements where available, the behavior and build checks performed, and any remaining blockers or measurement limits. Link the changed source where useful. Omit unperformed checks and unavailable metrics rather than filling a fixed report template.
