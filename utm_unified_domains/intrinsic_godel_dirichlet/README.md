# HU-AUTO-UTM-Intrinsic-Godel-Dirichlet/1.0

The machine's own program identifier and instantaneous configuration are treated as the object of Gödel encoding.

For a configuration `C_n=(p,q,h,M)`, the service computes a canonical representation, a reversible base-257 Gödel code, executes one finite TM transition, persists/reloads the predicted next state, and checks exact equality of the predicted and observed Gödel codes.

The Dirichlet critical residual is represented semantically by the exact condition

`E_1/2=0 iff the prime-valuation vectors of predicted and observed Gödel states match`.

The service does not claim a global halting decider, Gödel consistency proof, or self-awareness.

Endpoints:
- `GET /health`
- `GET /selftest`
- `POST /step`
