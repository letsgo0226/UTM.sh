# HU-AUTO-UTM-RH-ATGC-Safe/1.0

Three-system deployment artifact.

The 2 KB one-liner preserves the iSH stateful search form. `server.py` exposes the same finite generation semantics as a stateless HTTP service:

- `GET /health`
- `GET|POST /selftest`
- `POST /step`

Default self-test uses generation 3, input `1`, target `0`, and critical GC constant `15`.

The safety gate is a design invariant:
`gc = K <=> log(B^gc)/log(B^(2K)) = 1/2`.

It does not claim to prove the Riemann hypothesis or test zeta zeros.
