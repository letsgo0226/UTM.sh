# Unified UTM Domain Pack

This pack combines one fixed TM interpreter/toolchain with several host-side domain runtimes.

- `domains/Trader_42.sh` — self-contained **offline research / paper-only** Trader runtime, packed into one shell line under 2048 bytes.
- `domains/cosmic-love-infinity-tm.sh` — self-contained formal Cosmic-Love runtime, packed into one shell line under 2048 bytes.
- `domains/OCR_2KB.sh` — self-contained PDF/Image OCR consensus runtime, packed into one shell line under 2048 bytes.
- `domains/music-generator.sh` — self-contained bounded universal-program music + lyric-conditioned vocal-like WAV generator, packed into one shell line under 2048 bytes.
- `domains/TTS_2KB.sh` — standalone TXT -> WAV runtime using `espeak-ng`.
- `domains/ocr-tts.sh` — combined OCR/TTS consensus program.
- `domains/compact/` — archived earlier compact implementations, including the previous instrumental and eSpeak-vocal music generators.

## Important boundary

`utm/UTM.sh` is a fixed deterministic single-tape TM interpreter. A program is *purely inside the UTM* only after its algorithm has been compiled into the transition-table format consumed by `UTM.sh`.

The scripts under `domains/` are host-side runtimes. Trader, Cosmic, OCR, and Music embed their Python payloads directly in their `.sh` carriers using reversible compression/encoding. This is an implementation/storage transform, not a hash and not a proof of semantics.

`examples/domain-control.tm` demonstrates the common control plane:

```text
Enumerate -> Validate -> Purpose -> Commit
```

## Trader_42 packed unified runtime

The unified Trader is intentionally **research/paper-only**. It has no exchange-order path. It reads local candle data (or the synthetic fixture used by CI), then performs FAST/SLOW signaling, fee/slippage modeling, paper simulation, PnL/drawdown accounting, walk-forward OOS estimation, and Target/Certificate/Empirical/Temporal output.

```sh
CANDLE_CSV=./btc-1m.csv sh tools/run-domain.sh trader
```

`G_target=1` means `G(PROFIT_IS_OBJECTIVE)`: profit remains the formal objective. It does not mean every trade is profitable.

## Cosmic Love packed unified runtime

```sh
CMD=step N=3 sh tools/run-domain.sh cosmic
CMD=rewind N=2 sh tools/run-domain.sh cosmic
CMD=verify sh tools/run-domain.sh cosmic
```

The formal proposition is:

```text
CL := Cosmic Love Is The Solution(s) For Everything
```

The runtime reports prime/Gödel reconstruction, `CL`, `ICL`, `RCL`, `GCL`, `A_CL=1`, `G_CL=1`, and `G(CL)`. These are model-internal formal invariants; `P_real_world` and `P_empirical_hat` remain separate.

## OCR_2KB packed runtime

`OCR_2KB.sh` accepts `INPUT`, `OCR_LANG`, and optional `DPI` environment variables, or falls back to an interactive file/language chooser. PDFs are rendered with MuPDF when available and Poppler otherwise. Each page is recognized with Tesseract PSM 3/6/11; pair agreement determines the task-relative consensus output.

```sh
INPUT=book.pdf OCR_LANG=chi_tra sh tools/run-domain.sh ocr2
```

It reports JSON containing `TXT`, `OCR`, `pages`, `ambiguous`, `H_strict`, `H_task`, `zero_strict`, `zero_task`, `P_target_goal`, `C_target`, and `P_empirical_hat`. `zero_task=true` means consensus under the declared rule, not ground-truth OCR accuracy.

## Universal-program music runtime

The current music runtime no longer chooses from a finite instrument or singer preset table. It embeds a bounded BF8-compatible universal byte-program machine using the instruction alphabet:

```text
> < + - . , [ ]
```

Valid Brainfuck programs are included in the language, so the search language is Turing-complete. Candidate programs are enumerated length-first. In the unbounded limit every finite BF8 program appears; an actual run searches only a finite prefix controlled by `CANDIDATES` and bounds each execution by `VM_STEPS`.

Three selected programs play different roles:

```text
COMPOSE_G -> event byte stream
TIMBRE_G  -> generated waveform/timbre byte stream
VOICE_G   -> lyric-conditioned vocal-color byte stream
```

There is therefore no finite `TIMBRES=...` list and no finite `VOICE=en/cmn/...` inventory in the current main runtime. Lyrics are data supplied to the voice program rather than a selector for a preset singer.

```sh
KEYWORD='cosmic love' \
LYRICS='宇宙之愛是所有問題的解答' \
VOCAL=1 SEC=8 CANDIDATES=160 VM_STEPS=4000 \
sh tools/run-domain.sh music
```

The output includes `UTM=BF8`, `COMPOSE_G`, `TIMBRE_G`, `VOICE_G`, `VOCAL`, `BOUNDED=1`, `ENUM_COMPLETE=0`, `P_target_goal=1`, `C_target=1`, and `P_empirical_hat=null`.

`ENUM_COMPLETE=0` is deliberate: universality of the program language does **not** mean a finite invocation exhausts all programs. Likewise, `VOCAL=1` means the lyric-conditioned vocal-like synthesis path was used; it is not a guarantee of natural or intelligible human singing. See [`docs/UNIVERSAL_MUSIC_MACHINE.md`](docs/UNIVERSAL_MUSIC_MACHINE.md).

The immediately previous eSpeak-vocal version is archived under `domains/compact/music-generator-espeak.sh`, while the older instrumental-only generator remains `domains/compact/music-generator.sh`.

## One-line / <2KB invariant

CI requires the four packed main domains to satisfy:

```sh
for f in Trader_42.sh cosmic-love-infinity-tm.sh OCR_2KB.sh music-generator.sh; do
  test "$(wc -c < domains/$f)" -lt 2048
  sh -n "domains/$f"
done
```

Current payloads are self-contained and require no `.py` sidecar at runtime.

## Target / certificate / empirical / temporal interface

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

The smoke test checks shell syntax, all four packed `<2KB` boundaries, UTM control, Trader research/OOS/accounting, Cosmic step/rewind invariants, OCR consensus output, and both instrumental and lyric-conditioned universal-program music paths.

## Run domains

```sh
sh tools/run-domain.sh trader
CMD=step sh tools/run-domain.sh cosmic
KEYWORD='cosmic love' SEC=2 VOCAL=0 sh tools/run-domain.sh music
LYRICS='cosmic love' VOCAL=1 SEC=2 sh tools/run-domain.sh music
sh tools/run-domain.sh ocr2
sh tools/run-domain.sh tts2
```

## Reversible source certificate

```sh
sh tools/source-godel.sh domains/OCR_2KB.sh
sh tools/source-godel.sh domains/TTS_2KB.sh
sh tools/source-godel.sh domains/Trader_42.sh
sh tools/source-godel.sh domains/cosmic-love-infinity-tm.sh
sh tools/source-godel.sh domains/music-generator.sh
```

`GDOMAIN` is a reversible source identity/certificate; it does not make host source executable by `UTM.sh`.

## Dependencies

- `OCR_2KB.sh`: `python3`, `file`, `tesseract`, plus `mutool` or `pdftoppm` for PDFs.
- `music-generator.sh`: `python3` only; no external singer/voice engine is required by the current main runtime.
- `TTS_2KB.sh`: `espeak-ng`.

## Zero-entropy terminology

Reported `H_* = 0` values are structural/task-relative uniqueness checks inside the declared candidate/equivalence system. They are not claims of zero thermodynamic entropy or guaranteed external correctness/profit/aesthetic quality.
