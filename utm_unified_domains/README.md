# Unified UTM Domain Pack

This pack combines one fixed TM interpreter/toolchain with several host-side domain runtimes.

- `domains/Trader_42.sh` — self-contained **offline research / paper-only** Trader runtime, packed into one shell line under 2048 bytes.
- `domains/cosmic-love-infinity-tm.sh` — self-contained formal Cosmic-Love runtime, packed into one shell line under 2048 bytes.
- `domains/compact/Trader_42.sh` and `domains/compact/cosmic-love-infinity-tm.sh` — archived earlier compact cores.
- `music-generator.sh` — music generator.
- `ocr-tts.sh` — combined OCR/TTS consensus program.
- `OCR_2KB.sh` — standalone PDF/Image -> TXT runtime.
- `TTS_2KB.sh` — standalone TXT -> WAV runtime using `espeak-ng`.

## Important boundary

`utm/UTM.sh` is a fixed deterministic single-tape TM interpreter. A program is *purely inside the UTM* only after its algorithm has been compiled into the transition-table format consumed by `UTM.sh`.

The scripts under `domains/` are host-side runtimes. Trader and Cosmic now embed their complete Python payloads directly in the `.sh` carrier using reversible `zlib + Base85` packing. The packing is an implementation/storage transform, not a hash and not a proof of semantics. The earlier compact implementations are preserved under `domains/compact/`.

`examples/domain-control.tm` demonstrates the common control plane:

```text
Enumerate -> Validate -> Purpose -> Commit
```

Compile it with:

```sh
sh tools/build-control.sh
```

## Trader_42 packed unified runtime

The unified Trader is intentionally **research/paper-only**. It has no exchange-order path. It reads a local candle CSV (`close` column, or `price` as fallback), or the synthetic `TRADER42_TEST_PRICES` used by CI, then performs:

```text
fixed candle series
-> FAST/SLOW signal
-> modeled fee/slippage cost threshold
-> paper simulation
-> PnL / realized PnL / max drawdown
-> walk-forward OOS fold estimate
-> Target / Certificate / Empirical / Temporal output
```

Example:

```sh
CANDLE_CSV=./btc-1m.csv sh tools/run-domain.sh trader
```

The runtime reports `P_target_profit=1`, `C_profit`, `P_real_profit_hat`, `A_target=1`, and `G_target=1`. `G_target=1` means only `G(PROFIT_IS_OBJECTIVE)`: profit remains the formal objective. It does not mean every trade or future period is profitable.

The separate standalone Trader repository remains the richer Railway-oriented implementation; the unified pack intentionally omits live exchange execution.

## Cosmic Love packed unified runtime

The Cosmic entrypoint supports:

```text
step / rewind / verify / reset
```

Example:

```sh
CMD=step N=3 sh tools/run-domain.sh cosmic
CMD=rewind N=2 sh tools/run-domain.sh cosmic
CMD=verify sh tools/run-domain.sh cosmic
```

Its formal proposition is:

```text
CL := Cosmic Love Is The Solution(s) For Everything
```

The runtime reports prime-state reconstruction (`CF`), Gödel event reconstruction (`CG`), `CL`, state preservation (`ICL`), packed-source/axiom preservation (`RCL`), and the temporal model invariant (`GCL`, `G_CL=1`, `G(CL)`). This is a **model-internal formal invariant**. `P_real_world` and `P_empirical_hat` remain `null`; no external-world probability is inferred from the program.

## One-line / <2KB invariant

Both upgraded full entrypoints are required by CI to satisfy:

```sh
test "$(wc -c < domains/Trader_42.sh)" -lt 2048
test "$(wc -c < domains/cosmic-love-infinity-tm.sh)" -lt 2048
sh -n domains/Trader_42.sh
sh -n domains/cosmic-love-infinity-tm.sh
```

Their Python programs are embedded in the one-line shell files and reconstructed in memory with Python standard-library `zlib` and `base64.b85decode`; no `.py` sidecar is required at runtime.

## Target / certificate / empirical / temporal interface

The common vocabulary is:

```text
P_target_goal / P_target_profit = declared target
C_target / C_profit            = finite current certificate
P_empirical_hat                = data-derived estimate or null
A_target                       = target is constitutive of the model
G_target                       = admissible continuations preserve the target
```

See [`docs/TARGET_SEMANTICS.md`](docs/TARGET_SEMANTICS.md).

## Quick test

```sh
sh tests/smoke-test.sh
```

The smoke test checks shell syntax, the full packed `<2KB` boundaries, UTM control, the offline Trader research path, Cosmic step/rewind temporal invariants, archived compact boundaries, and a tiny music render.

## Run domains

```sh
sh tools/run-domain.sh trader
CMD=step sh tools/run-domain.sh cosmic
printf 'cosmic love\n5\n' | sh tools/run-domain.sh music
sh tools/run-domain.sh ocr
sh tools/run-domain.sh ocr2
sh tools/run-domain.sh tts2
```

`ocr2` and `tts2` are independent: OCR can stop at `.ocr.txt`, and TTS can consume any `.txt` file without running OCR first.

## Reversible source certificate

To assign any source file a reversible natural-number representation without SHA/hash:

```sh
sh tools/source-godel.sh domains/OCR_2KB.sh
sh tools/source-godel.sh domains/TTS_2KB.sh
sh tools/source-godel.sh domains/Trader_42.sh
sh tools/source-godel.sh domains/cosmic-love-infinity-tm.sh
```

`GDOMAIN` is an identity/certificate for source bytes; it does not make host source executable by `UTM.sh`. Executability requires compilation into TM transitions.

## OCR/TTS dependencies

`OCR_2KB.sh` requires `tesseract` and `file`; for PDF rendering it prefers `mutool` and falls back to `pdftoppm`. `TTS_2KB.sh` requires `espeak-ng`.

## Zero-entropy terminology

Reported `H_* = 0` values are structural/task-relative uniqueness checks inside the declared candidate/equivalence system. They are not claims of zero thermodynamic entropy or guaranteed external correctness/profit.
