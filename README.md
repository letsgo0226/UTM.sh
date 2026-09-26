# UTM Toolchain

Files:
- `UTM.sh` — fixed single-tape deterministic TM interpreter; accepts `PROGRAM` or reversible base-257 `GPROGRAM`.
- `TMCC.sh` — compiles direct TM DSL (`q read -> q2 write L/R/S`).
- `UASM.sh` — tiny assembly compiler (`SET/L/R/IF/JMP/EMIT/HALT`).
- `UMAC.sh` — macro compiler with accumulator and one-level CALL/RETURN.
- `UMACR.sh` — recursive macro compiler with tape-resident return stack.
- `examples/` — runnable examples.

## Quick test: direct TM

```sh
cd examples
../TMCC.sh inc.tm > inc.env
. ./inc.env
PROGRAM="$PROGRAM" INPUT=111 CMD=run TM_STATE=inc.json sh ../UTM.sh
```
Expected tape: `1111`.

## UASM

```sh
../UASM.sh inc.uasm > uasm.env
. ./uasm.env
PROGRAM="$PROGRAM" INPUT=111 CMD=run TM_STATE=uasm.json sh ../UTM.sh
```

## Macro compiler

```sh
../UMAC.sh add1.umac > add1.env
. ./add1.env
PROGRAM="$PROGRAM" START="$START" INPUT=3 CMD=run TM_STATE=add1.json sh ../UTM.sh
```
Expected tape: `4`.

## Recursive compiler

`UMACR.sh` uses the tape convention `stack|data`, so the input must start with `|`.

```sh
../UMACR.sh rec.umac > rec.env
. ./rec.env
PROGRAM="$PROGRAM" START="$START" INPUT='|3' CMD=run LIMIT=10000 TM_STATE=rec.json sh ../UTM.sh
```
Expected tape: `|0`.

`GPROGRAM` is reversible base-257 numbering of the transition-table text, not a cryptographic hash and not compression.

## Unified domain pack

The complete `utm_unified_domains/` suite is deployed in this repository. It contains an isolated copy of the fixed UTM toolchain plus Cosmic, Trader_42, Music, and OCR/TTS domain runtimes, source-Gödel tooling, architecture notes, a common control-plane example, and smoke tests.

```sh
cd utm_unified_domains
sh tests/smoke-test.sh
```

The suite also defines a common target/certificate/empirical vocabulary:

```text
P_target_goal=1
C_target in {0,1}
P_empirical_hat in [0,1] or null
```

These fields deliberately separate a declared objective from a finite certificate and from any data-derived empirical estimate. See [`utm_unified_domains/docs/TARGET_SEMANTICS.md`](utm_unified_domains/docs/TARGET_SEMANTICS.md).

See [`utm_unified_domains/README.md`](utm_unified_domains/README.md) for usage and the boundary between compiled TM transition programs and host-side domain runtimes.
