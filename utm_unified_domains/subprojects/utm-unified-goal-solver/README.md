# UTM Unified Goal Solver — UTM Universe Subproject

A bounded, machine-readable UTM subproject inside `utm_unified_domains`.

It unifies the recurring formal goals into five layers: societal/world, sovereignty/habitat, knowledge/memory, UTM meta-system, and formal research targets.

## Runtime

- `GET /health` — liveness
- `GET /.well-known/utm-universe.json` — AI-readable UTM discovery
- `GET /goals` — complete Goal Kernel
- `GET /solve` — exact search over the declared finite 0/1-rule policy DSL
- `GET /certificate` — current finite model certificate
- `POST /resident/admit` — admit a data-only capsule; arbitrary host-code fields are rejected
- `GET /resident/<resident_id>` — inspect an in-memory admitted capsule

The runtime preserves the common semantics used by the unified domain pack:

```text
P_target_goal = 1
C_target      = finite bounded-computation certificate
P_empirical_hat = null
A_target      = 1
G_target      = 1
```

`P_target_goal=1` is a declared formal objective. `C_target=1` means the current bounded search completed and found a feasible optimum inside the declared finite DSL. Neither field is a probability or guarantee of real-world peace, physical zero entropy, immortality, AI consciousness, or cosmological control.

## Local

```sh
python3 app.py
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/solve
```

The service uses Python standard library only.
