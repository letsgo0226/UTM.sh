# UTM Unified Goal Solver — UTM Universe Subproject

A machine-readable UTM subproject inside `utm_unified_domains`.

It unifies the recurring formal goals into five layers: societal/world, sovereignty/habitat, knowledge/memory, UTM meta-system, and formal research targets.

## Finite solver

- `GET /health` — liveness
- `GET /.well-known/utm-universe.json` — AI-readable UTM discovery
- `GET /goals` — complete Goal Kernel
- `GET /solve` — exact search over the declared finite 0/1-rule policy DSL
- `GET /certificate` — current finite model certificate
- `POST /resident/admit` — admit a data-only capsule; arbitrary host-code fields are rejected
- `GET /resident/<resident_id>` — inspect an admitted capsule

The runtime preserves the common semantics used by the unified domain pack:

```text
P_target_goal = 1
C_target      = finite bounded-computation certificate
P_empirical_hat = null
A_target      = 1
G_target      = 1
```

`P_target_goal=1` is a declared formal objective. `C_target=1` means a current finite computation found a feasible candidate in its declared scope. Neither field is a probability or guarantee of real-world peace, physical zero entropy, immortality, AI consciousness, or cosmological control.

## UTM-Ω Infinite Continuation resident

`omega_worker.py` upgrades the search to a potentially unbounded continuation process. It does **not** claim infinite physical compute.

The schedule has two interleaved streams:

1. an accelerated shortlex program-prefix scan; and
2. a Cantor dovetail over every finite `(program, model, depth, seed)` tuple.

Every individual stage is finite. There is no built-in final stage. Therefore the formal computation is potentially unbounded while the physical runtime remains finite at every moment.

The worker reports:

```text
compute_mode = potentially-unbounded-hybrid-dovetail
potentially_unbounded = true
actual_infinite_physical_compute = false
ENUM_COMPLETE = 0
best_observed = best completed finite work item so far
```

The production mirror runs inside the existing `cosmic-love-infinity-tm` Railway container and repeatedly admits/updates the data-only resident:

```text
agent_id = utm-omega-goal-solver
program_id = UTM-Omega-Infinite-Continuation-Solver/1.0
```

Its public UTM address is therefore:

```text
/resident/utm-omega-goal-solver
```

This avoids provisioning another Railway service and makes the solver a resident subproject of the existing `akashic-utm-main` world.

## Local

```sh
python3 app.py
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/solve
```

To run the Ω resident against an existing UTM API:

```sh
UTM_API=http://127.0.0.1:8080 python3 omega_worker.py
```

The implementation uses the Python standard library only.
