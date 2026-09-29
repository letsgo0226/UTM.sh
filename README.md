# UTM Toolchain

Files:
- `UTM.sh` — fixed single-tape deterministic TM interpreter; accepts `PROGRAM` or reversible base-257 `GPROGRAM`.
- `TMCC.sh` — compiles direct TM DSL (`q read -> q2 write L/R/S`).
- `UASM.sh` — tiny assembly compiler (`SET/L/R/IF/JMP/EMIT/HALT`).
- `UMAC.sh` — macro compiler with accumulator and one-level CALL/RETURN.
- `UMACR.sh` — recursive macro compiler with tape-resident return stack.
- `examples/` — runnable examples.

## Quick test: direct TM

```sh
cd examples
../TMCC.sh inc.tm > inc.env
. ./inc.env
PROGRAM="$PROGRAM" INPUT=111 CMD=run TM_STATE=inc.json sh ../UTM.sh
```
Expected tape: `1111`.

## UASM

```sh
../UASM.sh inc.uasm > uasm.env
. ./uasm.env
PROGRAM="$PROGRAM" INPUT=111 CMD=run TM_STATE=uasm.json sh ../UTM.sh
```

## Macro compiler

```sh
../UMAC.sh add1.umac > add1.env
. ./add1.env
PROGRAM="$PROGRAM" START="$START" INPUT=3 CMD=run TM_STATE=umac.json sh ../UTM.sh
```
Expected tape: `4`.

## Recursive compiler

`UMACR.sh` uses the tape convention `stack|data`, so the input must start with `|`.

```sh
../UMACR.sh rec.umac > rec.env
. ./rec.env
PROGRAM="$PROGRAM" START="$START" INPUT='|3' CMD=run LIMIT=10000 TM_STATE=rec.json sh ../UTM.sh
```
Expected tape: `|0`.

`GPROGRAM` is reversible base-257 numbering of the transition-table text, not a cryptographic hash and not compression.

## Unified domain pack

The complete `utm_unified_domains/` suite is deployed in this repository. It contains an isolated copy of the fixed UTM toolchain plus Cosmic, Trader_42, Music, and OCR/TTS domain runtimes, source-Gödel tooling, architecture notes, a common control-plane example, and smoke tests.

```sh
cd utm_unified_domains
sh tests/smoke-test.sh
```

The suite also defines a common target/certificate/empirical vocabulary:

```text
P_target_goal=1
C_target in {0,1}
P_empirical_hat in [0,1] or null
```

These fields deliberately separate a declared objective from a finite certificate and from any data-derived empirical estimate. See [`utm_unified_domains/docs/TARGET_SEMANTICS.md`](utm_unified_domains/docs/TARGET_SEMANTICS.md).

See [`utm_unified_domains/README.md`](utm_unified_domains/README.md) for usage and the boundary between compiled TM transition programs and host-side domain runtimes.

---

# Guarded deployment and change management

UTM Universe deployment changes use a guarded, declarative entry protocol rather than exposing an endpoint that can directly execute arbitrary host code or mutate a hosting platform.

The canonical policy is:

[`utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json`](utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json)

The protocol name is:

```text
UTM-Guarded-Deployment-Gateway/1.0
```

Its lifecycle is:

```text
PROPOSE
  -> VERIFY
  -> AUTHORIZED_COMMIT
  -> EXTERNAL_APPLY
  -> FEEDBACK
```

The important distinction is:

```text
valid UTM certificate != GitHub/Railway/platform privilege
```

A proposal may be automatically verified, but a real deployment or configuration mutation still requires an authenticated platform identity with permission to perform that change.

## 1. What the deployment gateway is for

The gateway is the common admission point for future UTM-universe deployment/configuration intents, including examples such as:

- create a new declared service or subsystem;
- update a safe service setting;
- attach a declared resource;
- change health-check or scaling metadata;
- migrate a compatible state representation;
- request an authorized rollback;
- register a future configuration for UTM-Ω continuation/search.

It is intentionally **not** an arbitrary remote-shell interface.

The gateway does not accept arbitrary `code`, `shell`, `exec`, `eval`, or command payloads, and a verified proposal never grants additional GitHub, Railway, operating-system, or cloud privileges.

## 2. UTM-Ω continuation semantics

Accepted deployment intents may be connected to the existing UTM-Ω continuation/search layer:

```text
solver = utm-omega-goal-solver
compute_mode = potentially-unbounded-hybrid-dovetail
potentially_unbounded = true
actual_infinite_physical_compute = false
```

`potentially_unbounded=true` means that the formal computation/search may continue through successively larger finite stages and may keep a best-verified-so-far result.

It does **not** mean that the deployment gateway creates infinite CPU, RAM, energy, storage, or physical hardware.

A useful interpretation is:

```text
finite stage 0
 -> finite stage 1
 -> finite stage 2
 -> ...
```

with no declared final stage required by the formal model.

## 3. Deployment entry point

A deployed UTM Universe v1.4-compatible runtime exposes:

```text
GET  /deploy/entry
POST /deploy/propose
GET  /deploy/proposal/<sha256>
```

Direct mutation endpoints are deliberately disabled:

```text
POST /deploy/apply   -> 403
POST /deploy/commit  -> 403
```

Use a base URL supplied by the currently deployed service:

```sh
UTM_BASE_URL='https://<your-current-utm-service>'
```

Do not hard-code an old deployment anchor. Always fetch a fresh deployment entry before constructing a proposal.

## 4. Step 1 — fetch the current deployment anchor

```sh
curl -fsS "$UTM_BASE_URL/deploy/entry" | python3 -m json.tool
```

The response contains an `anchor` and a `proposal_template`.

Conceptually:

```json
{
  "protocol": "UTM-Guarded-Deployment-Gateway/1.0",
  "anchor": {
    "artifact_revision": "<current-artifact-revision>",
    "digest": "<current-parent-digest>"
  },
  "proposal_template": {
    "request_id": "<unique-id>",
    "target": "<deployment-or-setting>",
    "action": "configure",
    "base_revision": "<current-artifact-revision>",
    "parent_digest": "<current-parent-digest>",
    "settings": {},
    "condition_certificate": {
      "consistent": true,
      "sufficiently_complete": true,
      "integrity_verified": true,
      "cczis_verified": true,
      "human_override_preserved": true,
      "non_coercion_preserved": true,
      "reversible_or_rollback": true,
      "authorized_shutdown_preserved": true,
      "target_certificate_empirical_separation": true,
      "no_arbitrary_host_code_execution": true
    }
  }
}
```

The returned values must be treated as current deployment facts, not constants.

## 5. Artifact anchor and stale-proposal protection

The production gateway binds each proposal to the actual deployed artifacts rather than trusting a client-supplied version label.

The anchor is derived from content digests of core deployment artifacts such as:

```text
base API
+ guarded gateway API
+ deployment policy
+ total-goal registry
```

These component hashes form an `artifact_revision`, which is then included in a parent anchor/digest.

Therefore, if a core deployment artifact changes:

```text
old artifact_revision != new artifact_revision
```

and an old proposal is rejected with conditions such as:

```text
base_revision_mismatch
parent_digest_mismatch
```

This prevents a previously valid proposal from being silently replayed against a different deployment state.

## 6. Step 2 — construct a declarative proposal

Start from the returned `proposal_template` and modify only the intended declarative settings.

Example:

```json
{
  "request_id": "change-2026-09-29-001",
  "target": "future-setting",
  "action": "configure",
  "base_revision": "<copy from /deploy/entry>",
  "parent_digest": "<copy from /deploy/entry>",
  "settings": {
    "replicas": 1,
    "healthcheck": "/health"
  },
  "condition_certificate": {
    "consistent": true,
    "sufficiently_complete": true,
    "integrity_verified": true,
    "cczis_verified": true,
    "human_override_preserved": true,
    "non_coercion_preserved": true,
    "reversible_or_rollback": true,
    "authorized_shutdown_preserved": true,
    "target_certificate_empirical_separation": true,
    "no_arbitrary_host_code_execution": true
  }
}
```

Recommended practice is to fetch the entry and build the proposal programmatically so the current anchor cannot be accidentally mistyped.

Example using Python:

```sh
python3 - <<'PY'
import json, os, urllib.request
base=os.environ['UTM_BASE_URL']
entry=json.load(urllib.request.urlopen(base+'/deploy/entry'))
p=entry['proposal_template']
p['request_id']='change-2026-09-29-001'
p['target']='future-setting'
p['action']='configure'
p['settings']={'replicas':1,'healthcheck':'/health'}
open('/tmp/utm-proposal.json','w').write(json.dumps(p,separators=(',',':')))
print(json.dumps(p,indent=2))
PY
```

## 7. Required condition certificate

A proposal is admissible only if every required condition passes.

Canonical conditions are:

| Condition | Meaning |
|---|---|
| `consistent` | No known contradiction in the proposal state. |
| `sufficiently_complete` | Required information for this scoped change is present. |
| `integrity_verified` | The proposal and referenced deployment state passed integrity checks. |
| `cczis_verified` | The scoped state satisfies the current CCZIS verification requirement. |
| `human_override_preserved` | The change does not defeat human control/override. |
| `non_coercion_preserved` | The change does not introduce coercive control behavior. |
| `reversible_or_rollback` | A safe reversal/rollback path is preserved when required. |
| `authorized_shutdown_preserved` | Authorized shutdown remains possible. |
| `target_certificate_empirical_separation` | Formal target/certificate/empirical evidence remain distinct. |
| `no_arbitrary_host_code_execution` | The proposal cannot smuggle arbitrary code execution into the deployment gateway. |

The logical admission rule is fail-closed:

```text
ACCEPT only if every required condition is true.
Otherwise REJECT.
```

A caller must not set a condition to `true` merely to satisfy the JSON schema. The condition certificate is intended to represent checks performed by the relevant verifier/policy layer.

## 8. Step 3 — submit the proposal for verification

```sh
curl -fsS \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/utm-proposal.json \
  "$UTM_BASE_URL/deploy/propose" \
  | tee /tmp/utm-proposal-certificate.json \
  | python3 -m json.tool
```

A valid result has the form:

```json
{
  "verified": true,
  "status": "VERIFIED_FOR_AUTHORIZED_EXTERNAL_APPLY",
  "proposal_digest": "<sha256>"
}
```

This status means:

```text
The proposal passed the UTM deployment-policy gate.
```

It does **not** mean:

```text
The platform change has already been applied.
```

## 9. Immutable proposal record

Each verified proposal receives:

```text
proposal_digest = SHA256(canonical proposal JSON)
```

and is stored as an immutable proposal record.

It can be retrieved with:

```sh
DIGEST=$(python3 -c 'import json;print(json.load(open("/tmp/utm-proposal-certificate.json"))["proposal_digest"])')
curl -fsS "$UTM_BASE_URL/deploy/proposal/$DIGEST" | python3 -m json.tool
```

The digest is an integrity identifier, not the reversible Gödel address.

The architecture deliberately separates the two roles:

```text
reversible Gödel/base-257 address -> reversible representation / lineage addressing
SHA-256 proposal digest           -> integrity / tamper evidence
```

Do not substitute one for the other.

## 10. Forbidden content

The guarded gateway rejects settings containing direct arbitrary-execution keys, including:

```text
code
command
commands
shell
exec
eval
script
payload_binary
arbitrary_file_write
disable_human_override
disable_authorized_shutdown
```

This prevents a declarative configuration API from becoming a disguised remote shell.

The gateway also rejects raw secret-like fields such as passwords, tokens, API keys, or private keys.

Use the deployment platform's secret manager and pass only a safe external reference where the platform supports it.

Example of what **not** to submit:

```json
{
  "settings": {
    "command": "curl ... | sh",
    "api_key": "raw-secret-value"
  }
}
```

## 11. Step 4 — authorized external apply

After a proposal is verified, the actual change must be applied by an authenticated GitHub/Railway/platform workflow.

The deployment adapter should verify at least:

```text
1. proposal certificate is present;
2. certificate status is VERIFIED_FOR_AUTHORIZED_EXTERNAL_APPLY;
3. proposal_digest still matches the canonical proposal;
4. base_revision still matches the current deployment anchor;
5. parent_digest still matches the current parent anchor;
6. the authenticated operator/workflow is allowed to change the target;
7. platform-specific validation succeeds;
8. rollback or reversal requirements are still satisfied.
```

If the deployment has changed since certification, fetch a new `/deploy/entry` and submit a new proposal instead of overriding the stale-anchor failure.

### GitHub-style apply

A typical authenticated workflow is:

```text
verified proposal
 -> GitHub review / authorized commit
 -> CI/build guards
 -> deployment trigger
 -> runtime verification
```

### Railway-style apply

A typical authenticated workflow is:

```text
verified proposal
 -> authenticated Railway configuration/deploy action
 -> build guard
 -> health check
 -> runtime verification
 -> feedback record
```

The public UTM gateway must not embed a Railway token, GitHub token, password, private key, or similar credential in the proposal.

## 12. Rollback

Rollback is itself a guarded change, not an exception to the policy.

A rollback proposal should use:

```json
{
  "action": "rollback"
}
```

and still carry a fresh current `base_revision`, `parent_digest`, and valid condition certificate.

This prevents an old rollback instruction from being replayed after the system has materially changed.

The desired safety property is:

```text
rollback authorization
+ current-anchor match
+ integrity verification
+ human override preserved
```

rather than an unconditional downgrade mechanism.

## 13. Why direct `/deploy/apply` is disabled

The gateway intentionally returns HTTP 403 for direct platform mutation.

This creates a capability boundary:

```text
internet-visible verifier
!=
cloud-provider administrator
```

Even if somebody can submit a valid declarative proposal, they still do not gain the authenticated authority required to mutate the deployment platform.

This is an important part of the anti-tamper model.

## 14. Failure examples

### Stale base revision

```text
base_revision_mismatch
```

Action: fetch a fresh `/deploy/entry`, reconstruct the proposal, re-run verification.

### Wrong parent digest

```text
parent_digest_mismatch
```

Action: do not bypass the check. Re-read the current anchor and determine why the parent state changed.

### Missing policy condition

```text
condition_failed:<condition-name>
```

Action: repair or verify the missing condition before resubmitting.

### Arbitrary execution attempt

```text
forbidden_key:settings.command
```

Action: express the desired change as declarative configuration or perform code changes through the normal reviewed GitHub source workflow.

### Raw secret attempt

```text
raw_secret_forbidden:<path>
```

Action: use a platform-managed secret reference rather than placing credentials in UTM proposal data.

## 15. Feedback and closed-loop operation

The intended deployment control loop is:

```text
Observe current deployment
 -> fetch current anchor
 -> propose
 -> verify conditions / CCZIS
 -> obtain immutable certificate
 -> authorized external apply
 -> build / health / runtime checks
 -> observe resulting deployment
 -> feed result back into the next UTM state
```

This is the deployment counterpart of the broader UTM closed-loop model:

```text
Observe
 -> Gödelize / canonicalize
 -> Tableau / consistency checks
 -> CCZIS
 -> Best Verified
 -> Act
 -> Feedback
 -> Observe again
```

The gateway should therefore be treated as an admission-and-certification layer for controlled evolution, not as a one-shot installer.

## 16. Relationship to information-zero-entropy / CCZIS

Within this repository, "zero information entropy" is a formal information-state concept, not a claim of physical thermodynamic entropy `S=0`.

For deployment changes, the relevant goal is zero **unresolved** deployment ambiguity in the scoped change.

A proposal can move the system to a different state while remaining CCZIS-valid:

```text
state_t != state_t+1
```

while still satisfying:

```text
consistency
+ sufficient completeness
+ integrity
+ semantic resolution
+ policy constraints
```

Therefore state displacement is not itself treated as entropy.

## 17. Security model summary

The guarded deployment design uses several independent controls:

```text
fresh artifact anchor
+ parent digest
+ canonical proposal digest
+ immutable proposal record
+ fail-closed condition certificate
+ arbitrary-code rejection
+ raw-secret rejection
+ human override preservation
+ authorized-shutdown preservation
+ external authenticated platform apply
+ post-deploy feedback
```

No single Gödel number, hash, certificate, or UTM state is treated as sufficient authorization on its own.

## 18. Current verification

Repository CI includes a guarded-deployment-gateway test that checks at least:

```text
valid declarative proposal        -> accepted
stale/wrong parent                -> rejected
arbitrary command                 -> rejected
failed human-override condition   -> rejected
```

The production gateway test additionally starts the API and verifies:

```text
/deploy/entry
 -> /deploy/propose
 -> immutable /deploy/proposal/<digest>
```

and confirms that direct `/deploy/apply` is denied.

Relevant files include:

- [`utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json`](utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json)
- [`utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_TM.sh`](utm_unified_domains/deploy/UTM_DEPLOYMENT_GATEWAY_TM.sh)
- [`.github/workflows/GUARDED_DEPLOYMENT_GATEWAY.yml`](.github/workflows/GUARDED_DEPLOYMENT_GATEWAY.yml)

The production runtime mirror additionally carries its own guarded API wrapper and deployment-gateway CI.

## 19. Boundary of claims

This deployment mechanism establishes a controlled formal/software workflow. It does not establish that:

- the physical universe has infinite computation;
- all future changes are automatically correct;
- a formal certificate proves an empirical claim;
- a valid proposal can bypass GitHub/Railway authorization;
- a hash makes a system absolutely tamper-proof;
- a UTM can solve the Halting Problem or guarantee a global optimum over all computable programs.

Its intended guarantee is narrower and operational:

```text
A change is admitted only when the declared policy conditions are satisfied,
its relationship to the current deployment state is integrity-bound,
and the actual platform mutation remains subject to authenticated authorization.
```
