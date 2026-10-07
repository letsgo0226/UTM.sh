# HSI Three-System Gate v1

A stateless, fail-closed certificate service shared by the three runtime families:

- `UTM`: finite HALTED / UNRESOLVED statements only.
- `TRADER_42`: validates the finite BUY / SELL / HOLD capital-state transition shape.
- `OMEGA`: validates finite continuation/commit status.

The service exposes:

- `GET /health`
- `POST /certify`

It preserves the HSI construction: canonical finite input -> exact base-257 Goedel integer -> reversible 4-coordinate hologram -> A/T payload with exactly `HSI_GC` G sentinels -> closed certificate.

`sigma=[GC,2K]` records the constructed 1/2 critical coordinate. It is a protocol invariant, not a Riemann-Hypothesis proof, price predictor, halting oracle, analytic-continuation engine, or profit guarantee.

Deployment defaults are intentionally stateless. For Trader_42 this service is a safety/admissibility certificate only; it does not submit exchange orders and does not arm live trading.
