# Identity-gated edge migration plan

- Organization and plan owner:
- Date and configuration revision:
- Requested scope:
- Cloudflare account and DNS provider scopes:
- Existing IaC tool, provider version, and state owner:
- Status: Draft

## Summary

Record the migration goal, inventory coverage, classification counts, selected origin pattern, and pilot. Distinguish confirmed facts from proposals and unresolved decisions.

## Inventory

### Sources and coverage

| Provider and account | Zone/view | Method and collection time | Coverage and gaps |
|---|---|---|---|

### Applications and routes

| Hostname and source/view | Protocol and destination | Alternate routes | Owner | Existing authentication and callers | Protect/Public/Unknown | Evidence and notes |
|---|---|---|---|---|---|---|

New rows start as Unknown. Preserve previous classifications and owner decisions when refreshing the inventory.

## Configuration decisions

| Topic | Proposed or approved choice | Rationale and current source | Owner and prerequisites | Status |
|---|---|---|---|---|

Cover application scope, human and machine authentication, session lifecycle, origin restrictions, JWT validation, application sign-in, personalized caching, request filtering, and operational ownership where relevant. Record unanswered questions as unresolved rather than accepted defaults.

### Per-application plan

| Application | Access scope and policies | Origin connection and restrictions | Identity validator and app sign-in | Dependencies | Pilot or rollout wave |
|---|---|---|---|---|---|

## Pilot and cutover

- Current route and any existing direct-origin exposure:
- Target route and the owner of each change:
- Application, policy, origin, DNS, and logging prerequisites:
- Sequence that establishes protection before publishing the new route:
- Temporary exposure, mitigation, owner, and deadline, if unavoidable:
- Pilot scope, intended users/clients, and entry/exit criteria:
- Failure thresholds and a recovery procedure that preserves protection:
- Rollout waves and required approvals:

## Validation

All results start as **not tested**. Include a working legitimate-user control, denial cases, direct-origin attempts, validator-specific checks, and application authorization. Add machine callers, session lifecycle, caching, and failover where applicable.

| Case | Persona and test location | Expected result | Observed result and timestamp | Evidence | Status |
|---|---|---|---|---|---|

Record what was actually tested. A generated configuration or successful redirect is not production acceptance. Store evidence references without cookies, tokens, private keys, or unredacted browser archives.

## Implementation artifacts

Complete this section only if artifact generation was requested.

- Paths to generated or modified configuration:
- Existing resources/state imported or extended:
- Schemas and provider versions verified:
- Formatting/validation commands run and their results:
- Changes requiring separate deployment approval:
- Secret-store references, not secret values:

## Open questions and next actions

| Question, dependency, or risk | Owner | Next action | Target date |
|---|---|---|---|

## Sources

Record the current product documentation and the date consulted. Identify draft or unavailable sources explicitly.
