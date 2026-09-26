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
