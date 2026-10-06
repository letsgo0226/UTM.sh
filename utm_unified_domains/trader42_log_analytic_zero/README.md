# Trader_42 Log-Analytic Zero Kernel 1.1

A bounded, stateless mathematical model verifier. This service never places orders and cannot authorize real-world trades. Its outputs do not establish market profit probabilities.

## Fixes and compatibility

- `/evaluate` requires all five scalar fields; missing fields return HTTP 400.
- `/transition` requires actual JSON booleans. Strings and numeric flags return HTTP 400.
- Zero residual claims alone return `UNDETERMINED` with `admissible_candidate=false`.
- Only checked evidence can produce `CERTIFIED_MODEL_CANDIDATE` or `CERTIFIED_MODEL_TRANSITION`.
- The old unqualified `CERTIFIED_CANDIDATE` label is no longer emitted.
- Numeric probability output is approximate. Exact zero status is `formal_probability_one`; nonzero values are never displayed as 1.0.
- Replay receipts contain inputs, results and a hash; they are unsigned and are not mathematical proofs by virtue of encoding.

These are intentional breaking corrections to version 1.0's fail-open defaults.

## Supported evidence

An analytic witness is a polynomial with rational coefficients in ascending order, the source polynomial, the candidate polynomial, a rational complex evaluation point, and target domain `C`. The verifier checks coefficient identity and evaluates the candidate exactly at that point, checking against submitted G. This proves only the submitted polynomial identity and its evaluation on C. General maximal continuation, optimal trading strategy search and other function classes remain unimplemented and return `UNDETERMINED`.

A risk witness supplies a modeled long-only balance state before, action and state after. The verifier computes BUY/SELL/HOLD balance arithmetic and verifies nonnegative balances and equality with the claimed state after. This is a simulation invariant check, not an exchange risk assessment. Provided balances, prices and fees are unauthenticated user inputs; no broker data is fetched.

Example verified model candidate:

```json
{
  "g_re":"0", "g_im":"0",
  "continuation_residual":"0", "risk_residual":"0", "certificate_residual":"0",
  "analytic_witness": {
    "kind":"polynomial", "source_coefficients":["-1","1"],
    "candidate_coefficients":["-1","1"], "z_re":"1", "z_im":"0", "target_domain":"C"
  },
  "risk_witness": {
    "state_before":{"cash":"100","base":"0"},
    "action":{"side":"BUY","quantity":"2","price":"10","fee":"1"},
    "state_after":{"cash":"79","base":"2"}
  }
}
```

A submitted zero-only request with no witnesses is valid input but uncertified. An unsupported analytic class remains unknown. Contradictory evidence or nonzero residuals return HOLD.

`/transition` also requires `invariant_before`, `guard_passed` and `transition_preserves_invariant` as JSON booleans. A verified model transition additionally requires the risk witness and agreement between submitted flags and computed facts. True flags alone are never certified.

## API and bounds

- GET `/health`: protocol and deployment commit, when available.
- GET `/manifest`: scope and limits.
- POST `/evaluate`, `/transition`, `/encode`.
- Input objects only; duplicate keys, NaN/Infinity, missing bodies and oversized documents are rejected.
- Request maximum: 16 KiB; codec input maximum: 1024 UTF-8 bytes.
- Scalar input: 80 characters, exponent magnitude at most 64, rational precision at most 256 bits.
- Intermediate arithmetic: at most 2048 bits; polynomial arrays: 1–32 coefficients.
- JSON maximum depth: 16; document node budget: 1024.
- At most 16 simultaneous request handlers; sockets have a 5-second timeout.
- Large replay receipts omit the integer encoding and retain the receipt/hash, explicitly marking the omission.

The simulator API is public and stateless. These resource bounds do not replace production ingress protection or authentication. Existing UTM-Universe resident/job authorization, infrastructure persistence and existing live trader configuration are separate concerns; this module does not modify them.

## Verification

Run `python3 -m unittest -v test_core.py`. Tests exercise missing evidence, missing fields, wrong JSON types, forged claims, polynomial mismatch, complex roots, balance overdrafts, receipt tampering, extreme scalars and actual HTTP error responses.

Four deployments use the same repository branch: Railway services in UTM-Universe, trader-42-tm and blue-pleiadian-prime-trader, plus the Render mirror. The PR stays draft and the existing trader remains independent.
