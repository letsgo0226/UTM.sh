# UTM Persistence Envelope

`UTM-Persistence-Envelope/1.0` is a bounded verification layer for previously deployed UTM services and archives.

The protocol does not require every older service to be rewritten. Each service is represented through an adapter, and the envelope evaluates declared residuals for state, transition, handoff, recovery, and policy.

The fleet condition is:

```text
P_fleet = max(node residuals, handoff residuals)
Persistence condition: P_fleet = 0
```

A zero residual means that the checked finite evidence exactly matches the declared invariant for that verification event. It does **not** prove future fault-freedom, physical immortality, consciousness continuity, RH, ASI, oracle access, or hypercomputation.

Adapters:

- `utm-universe`
- `riemann-proof-utm`
- `utm-single-function`
- `utm-scholar-loop`
- `dropbox-exact-search`
- `source-runtime`

API:

- `GET /health`
- `GET /manifest`
- `GET /catalog`
- `POST /verify/state`
- `POST /verify/transition`
- `POST /verify/handoff`
- `POST /verify/recovery`
- `POST /verify/policy`
- `POST /adapter/verify`
- `POST /fleet/verify`
- `POST /certificate`
- `POST /certificate/verify`

All checks are finite and bounded. Certificates use reversible base-257 encoding of canonical JSON; cryptographic hashes are not treated as the authoritative identity of a state.
