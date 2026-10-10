# HSI–Cosmic Love / XY Analytic UTM — UTM review adapter

Source of truth: https://github.com/letsgo0226/Notes/pull/4

This branch adds the exact 1,810-byte XY/2K shell One-Liner as a **review-only** artifact. The original HSI domain gate (hsi-utm-gate) remains unchanged.

## Domain-specific contract
Finite computation only; lack of a halt witness remains UNRESOLVED. No universal halting decision.

## Review-only invocation

```sh
HSI_STATE=xy-review.state HSI_PROGRAM=2 HSI_WORD=1 sh hsi_xy_analytic_2k/hsi_cl_xy_2k.sh
```

Output x/y are reversible finite Gödel encodings. D0 is a finite Dirichlet residual. Analytic interpolation is described in the Notes repository's XY_SPEC.md and is not a universal analytic continuation, safe program, or nonhalting decider.

This commit does not change Railway service configs, the production branch, environment variables, broker credentials, volume settings or domain gates. Release to Railway requires an explicit separate review and post-deploy observation.
