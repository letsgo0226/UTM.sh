# UTM Analytic-Lift Kernel

`UTM-Analytic-Lift/1.0` is a bounded proof-carrying research kernel for the analytic-continuation and function-lifting ideas used by the UTM Universe project.

It does **not** claim a universal solver for arbitrary analytic continuation, the Riemann Hypothesis, the halting problem, oracle access, hypercomputation, physical higher dimensions, or empirical-world guarantees.

## Core equation

    AC_{D->Omega}(F;f) = (dbar F, F|_D - f) = (0,0)

For a fixed target domain, this is the mathematical specification of analytic continuation. The deployed kernel only returns `proved` for bounded schemas it can verify exactly. Unsupported inputs return `undetermined`; `undetermined` is never converted into nonexistence.

## Supported bounded schemas

- `polynomial` — exact coefficient identity; polynomial continuation to `C`.
- `geometric_series` — `sum z^n` on `|z|<1` -> `1/(1-z)` on `C\\{1}`.
- `log_germ` — Riemann-surface lift `pi(w)=exp(w)`, `F(w)=w`.
- `sqrt_germ` — lift `pi(w)=w^2`, `F(w)=w`.
- `lacunary_2n` — unit circle natural-boundary obstruction for `sum z^(2^n)`.
- `riemann_zeta` — standard meromorphic-continuation theorem schema only; simple pole at `s=1`; no RH claim.

## Program/function lifting

`POST /lift/program` performs a reversible base-257 encoding of a finite canonical JSON object and raises its descriptive level by one. This is the implementation meaning of `UTM^UTM`: a program/transformation description becomes data for a higher computable layer.

`POST /lift/tensor` returns the bounded interaction-coordinate count `k^n`. It is a tensor/self-interaction count, not a claim about physical spacetime dimensions.

Coordinates:

    UTM-X = state/data
    UTM-Y = program transformation
    UTM-Z = meta-transformation / certificate

## API

    GET  /health
    GET  /manifest
    POST /ac/solve
    POST /ac/verify
    POST /lift/program
    POST /lift/tensor
    POST /certificate/verify

## Certificate semantics

Canonical JSON is reversibly encoded as a base-257 integer. SHA-256 is included only as an integrity aid and is not treated as the authoritative identity.

## Deployment boundary

All executed requests are finite and bounded. The service is designed to run as an isolated Railway/Render module next to, not in place of, `utm-universe`, `riemann-proof-utm`, `utm-single-function`, and `utm-persistence-envelope`.

A live cloud deployment proves only that this finite service instance built and ran successfully. It does not prove mathematical conjectures or metaphysical claims.
