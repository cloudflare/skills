# Gateway, TLS, and DLP

## Assessment

Ask only the prompts relevant to the task.

- Traffic controls: DNS categories, HTTP URL/path inspection, L4 ports/protocols, egress IP requirements, custom lists, and allow/block exceptions. Retrieve [Gateway traffic policy](https://developers.cloudflare.com/cloudflare-one/traffic-policies/) docs for current selectors and order of enforcement.
- Identity: whether Gateway policies need user or group selectors, and whether users will be authenticated through WARP/IdP context. Check [Gateway identity selectors](https://developers.cloudflare.com/cloudflare-one/traffic-policies/identity-selectors/) and [SCIM provisioning](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/scim/) when groups are involved.
- TLS inspection: root CA deployment path, certificate-pinned applications, compliance exceptions, and FIPS requirements. Retrieve [TLS decryption](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/tls-decryption/) docs before enabling.
- DLP: sensitive data types, channels to inspect, TLS inspection readiness, DLP profiles, payload logging requirements, and false-positive tolerance. Retrieve [DLP](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/) docs before creating enforcement.

## Guardrails

- `dns.domains` matches a domain and subdomains; `dns.fqdn` is exact-match only.
- DNS pre-resolution selectors and post-resolution selectors do not behave like a single strict precedence list. Retrieve current evaluation docs before changing rule order.
- HTTP Do Not Inspect rules run before HTTP Allow/Block/Isolate behavior. A later block rule will not override an earlier inspection bypass.
- Certificate-pinned apps need Do Not Inspect exceptions before broad TLS inspection. Deploy the Cloudflare root CA to managed devices before enabling inspection.
- DLP profiles are detection definitions only. They do nothing until referenced by Gateway HTTP policies or CASB scan settings. Rules with body inspection may be evaluated multiple times in a single pass.
- Start DLP with payload logging where appropriate, tune false positives, then block.
- Gateway Network policies are strict L4 controls. Identity-aware L4 matching requires authenticated device context.

## Validation

- Gateway: verify rule type, action, traffic expression, precedence/evaluation phase, referenced lists, and Gateway settings before enabling broadly.
- TLS/DLP: test Do Not Inspect exceptions and root CA trust before enabling inspection; test DLP with known samples and monitor false positives before blocking.
