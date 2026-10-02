# LOG_ABELOMEGA_NATIVE

This is the UTM-Universe-native finite-stage realization of the Log-Abelian / UTM-omega model.

## Pure-UTM core

The fixed machine `VALUATION_ADD.tm` computes one scalar valuation coordinate:

```text
input   = 1^m#1^n
output  = 1^(m+n)
```

It is compiled to the transition-table format consumed by the repository's fixed deterministic single-tape `UTM.sh`. Therefore the coordinate-addition operation itself is executed inside the UTM rather than emulated by Python.

For a finite-support valuation vector, `compile_native_stage.py` emits a finite job bundle: one UTM job for each coordinate in the union of the two supports. `run_native_stage.py` schedules those jobs and verifies their tapes.

The host tools package and schedule finite jobs; they do not provide the arithmetic semantics.

## Example

```sh
cd utm_unified_domains/utm_universe/subprojects/LOG_ABELIAN_OMEGA_NATIVE
python3 run_native_stage.py \
  --left '{"0":2,"3":1}' \
  --right '{"0":3,"2":2}' \
  --stage 42
```

The coordinate results implement:

```text
(v+w)_i = v_i + w_i
```

which is commutative and is the exact discrete counterpart of the finite-support logarithmic relation

```text
Lambda(v+w)=Lambda(v)+Lambda(w).
```

## UTM-omega boundary

A UTM-omega computation is a potentially unbounded sequence of such finite stages. No invocation executes an actually infinite stage, and this subproject does not introduce a halting oracle or hypercomputation.
