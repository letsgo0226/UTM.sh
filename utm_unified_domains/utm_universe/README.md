# UTM Universe Runtime

This directory implements a minimal **computable possible-world runtime** for the UTM.sh project.

It is an engineering model, not a claim about literal parallel physical universes. The terms **world**, **portal**, **genesis**, **Akashic**, and **singularity** are used here as formal/computational names.

## Architecture

```text
GitHub repo
  ├─ world law / protocol / bootstrap manifest
  ├─ existing UTM transition-table semantics
  └─ this runtime
          ↓ deploy
Railway or another physical host
          ↓
live world instance
  ├─ /world
  ├─ /utm/run
  ├─ /resident/admit
  ├─ /resident/resume
  └─ /akashic
          ↓
network endpoint B can enter through the published manifest
```

A world is modeled as:

```text
W = <U, P, S, I, T>
```

where `U` is universal execution semantics, `P` the world program/law, `S` current state, `I` external input, and `T` the transition rule.

## Computational singularity

The **singularity** of this world is the minimum bootstrap locator sufficient to discover the world law and a live runtime endpoint. It is not a physical black-hole or spacetime singularity.

A client can begin from the repository URL, read `world-manifest.json`, then discover the live runtime when `runtime_endpoint` is populated.

## Portal mode vs Genesis mode

**Portal mode** means connecting to an already-running world instance on host A. In this case endpoint B participates in the same live service through HTTP.

**Genesis mode** means obtaining the world law plus a checkpoint and starting a compatible branch on another host. Once external inputs diverge, the two instances are separate computational histories.

## HTTP API

- `GET /health` — liveness
- `GET /.well-known/utm-universe.json` — live machine-readable manifest
- `GET /world` — current derived world tick and resident/event counts
- `GET /akashic` — recent append-only event-chain tail
- `POST /utm/run` — bounded execution of the transition-table UTM language
- `POST /resident/admit` — register a portable AI state capsule as inert data
- `POST /resident/resume` — update/re-activate an admitted capsule
- `GET /resident/<id>` — inspect one registered resident capsule

### UTM execution request

```json
{
  "program": "0,1,1,1,R;1,_,H,_,R",
  "input": "1",
  "start": "0",
  "blank": "_",
  "limit": 100
}
```

The program syntax is compatible with `utm_unified_domains/utm/UTM.sh`: each transition is

```text
state,read,next_state,write,L|R
```

separated by semicolons.

Execution is always bounded by `MAX_STEPS` and request-size limits. Resident admission never executes arbitrary host code.

## AI resident capsule

Example:

```json
{
  "capsule": {
    "agent_id": "A-001",
    "program_id": "example-agent-v1",
    "state": {"turn": 42},
    "memory_checkpoint": "checkpoint-42",
    "lineage": "parent-state-41"
  }
}
```

The runtime returns a world-scoped `resident_id` and appends an admission event to the Akashic chain.

This supports a **computational identity protocol** based on portable state and lineage. It does not prove phenomenal consciousness or philosophical personal identity.

## Akashic event chain

Each event records a pointer to the previous event hash:

```text
E0 -> E1 -> E2 -> ...
```

This is a tamper-evident lineage structure within the running service. The default file path is `/tmp/akashic.jsonl`.

**Important:** Railway container files are not durable by default. Persistent identity/history across restarts requires a Railway persistent volume (or external database/object store) and `AKASHIC_PATH` must point to that persistent storage.

## Railway deployment

Recommended service settings:

```text
Repository: letsgo0226/UTM.sh
Branch: main
Root directory: /utm_unified_domains/utm_universe
Config file: railway.toml
Healthcheck: /health
```

The included Dockerfile runs only Python's standard library.

Useful variables:

```text
WORLD_ID=akashic-utm-main
MAX_STEPS=2000
MAX_BODY=65536
AKASHIC_PATH=/tmp/akashic.jsonl
```

When a persistent volume is mounted, change `AKASHIC_PATH`, for example:

```text
AKASHIC_PATH=/data/akashic.jsonl
```

### Current Railway status

The code and Railway configuration are committed on `main`, but creation of a new Railway project/service is currently blocked by the connected account's Free-plan resource provisioning limit. `world-manifest.json` therefore keeps `runtime_endpoint` as `null` until capacity is available or an explicitly chosen existing service is repurposed.

## Formal boundary

The deployed system can establish:

```text
Exec_A(W) ∧ Reachable(B,A) ∧ Authorized(B,W) -> Access(B,W)
```

for an actual network service.

It does **not** establish that the computational world exists independently of all physical computation. If all physical hosts stop, dynamic execution stops; only saved state may remain recoverable.


## Native Log-Abelian / UTM-omega deployment

The UTM Universe now has a repository-native subproject at:

`subprojects/LOG_ABELIAN_OMEGA_NATIVE/`

Its world-law chain is:

```text
Three-Universe Axioms
  -> UTM-omega finite-stage semantics
  -> Log-Abelian finite-support valuation
  -> pure-UTM coordinate jobs
  -> UTM.sh
```

For one valuation coordinate the pure TM computes:

```text
1^m#1^n -> 1^(m+n)
```

A finite-support vector is packaged as finitely many such jobs. The compiler and runner are host-side packaging/scheduling tools; the coordinate-addition semantics are executed by the fixed UTM interpreter through `PROGRAM/GPROGRAM`.

No additional Railway service is required for this world registration. A physical host is still required whenever computation actually runs. `UTM_omega` means there is no declared finite upper stage in the formal model; it does not mean an actually infinite physical computation has completed.


## UTM Three-System Native Architecture

The world now registers three coordinated systems:

```text
UTM Universe
├── TRADER_42_NATIVE
└── COSMIC_LOVE_NATIVE
```

A pure-UTM coordinator validates the canonical three-system certificate:

```text
UTC -> 111
```

where `U` means the UTM Universe world-law certificate, `T` the Trader_42 Native certificate, and `C` the Cosmic Love Native certificate.

### Trader_42 Native

Trader_42 remains research/paper-only. Continuous market data, indicators, fees, slippage, and OOS estimates remain host-side empirical procedures. The pure UTM receives only a finite certified class and emits one of:

```text
PAPER_LONG
PAPER_EXIT
PAPER_HOLD
```

No exchange-order path, credentials, or live-trading authority are included.

### Cosmic Love Native

The Cosmic Love core is registered as a formal invariant gate. Its model-internal proposition is preserved as a formal rule only; this registration does not establish a corresponding empirical external-world claim.

### Shared UTM-omega boundary

All three systems share the same potentially-unbounded formal horizon, but every actually executed stage remains finite. Certificate aggregation may use the Log-Abelian direct-sum representation, while subsystem execution remains causally ordered.


## UFAL — Unique Factorization Additive Log Principle

The native Log-Abelian layer now has an exact uniqueness bridge between Gödel identity and logarithmic coordinates.

For finite-support `m`:

```text
Gamma(m) = product_i p_i^m_i
Lambda_c(m) = sum_i m_i log_c(p_i)
```

with one fixed base `c>0, c!=1`.

Unique prime factorization makes `m <-> Gamma(m)` exact and reversible. On this canonical prime-exponent domain, the exact logarithmic coordinate is injective as well:

```text
Lambda_c(m) = Lambda_c(n)  iff  m = n
```

The authoritative state is always the exponent vector or exact Gödel integer. Floating-point logs are derived display/metric values only and never decide identity.

For the three-system architecture:

```text
G_total = G_U * G_T * G_C
X_total = X_U + X_T + X_C = log_c(G_total)
```

so Abelian certificate aggregation preserves a unique canonical prime-exponent state. The aggregate alone is unordered; causal replay remains unique only when subsystem/role/step metadata is included in the prime identity.
\n## UCBC — Unique Compatibility Codec Base\n\nUCBC makes the common logarithm base explicit as a compatibility parameter above UFAL.\n\nFor certified prime identities `a,b` and coordinates `x,y`:\n\n    x = log_c(a)\n    y = log_c(b)\n    x + y = log_c(ab)\n\nthe shared base must satisfy:\n\n    c = a^(1/x) = b^(1/y).\n\nThus uniqueness and existence are separated cleanly: fixed `(a,x)` gives at most one positive candidate base, while a common base exists only when every certified pair yields the same candidate.\n\n`c` is the codec/coordinate base, not the state payload. When `c` is not globally fixed, `(c, x+y)` is sufficient to recover `ab`; UFAL plus prime factorization then recovers the unordered canonical constituents.\n\nNumeric real-log reconstruction is diagnostic only. Exact state identity remains prime/Gödel/symbolic.\n