# Unified UTM Domain Pack

This pack combines one fixed TM interpreter/toolchain with four domain families plus standalone OCR/TTS split runtimes:

- `cosmic-love-infinity-tm.sh` — restored legacy self-evolving prime/Gödel core.
- `Trader_42.sh` — restored persistent prime/Gödel TM core (from the prior `42.sh`).
- `music-generator.sh` — the unbounded-action music generator supplied in the current conversation.
- `ocr-tts.sh` — combined OCR/TTS consensus program; portable version prefers `espeak-ng` and falls back to `espeak`.
- `OCR_2KB.sh` — standalone PDF/Image -> TXT runtime; MuPDF-first with Poppler fallback; 1556 bytes including shebang.
- `TTS_2KB.sh` — standalone TXT -> WAV runtime using `espeak-ng`; 1008 bytes including shebang.

## Important boundary

`utm/UTM.sh` is a fixed deterministic single-tape TM interpreter. A program is *purely inside the UTM* only after its algorithm has been compiled into the transition-table format consumed by `UTM.sh`.

The scripts under `domains/` are currently domain runtimes. Music uses Python/wave; OCR uses Tesseract/MuPDF/Poppler; TTS uses eSpeak; the restored Cosmic/Trader scripts use Python. Therefore the package is presently a **UTM-controlled / UTM-toolchain architecture**, not a claim that these host runtimes have already been compiled into one TM transition table.

`examples/domain-control.tm` demonstrates the common control plane:

`Enumerate -> Validate -> Purpose -> Commit`

Compile it with:

```sh
sh tools/build-control.sh
```

The compiler prints both `PROGRAM=...` and reversible base-257 `GPROGRAM=...`.

## Target / certificate / empirical interface

The pack now uses one common three-layer vocabulary:

```text
P_target_goal = 1
C_target in {0,1}
P_empirical_hat in [0,1] or null
```

The target value is a declared goal, not a guaranteed outside-world probability. The certificate reports only the finite checks actually performed by that domain. The empirical estimate is populated only when a declared dataset and estimator support it; otherwise it stays `null`.

The compact Cosmic and Trader cores now emit these generic fields directly. OCR/TTS keep their existing `zero_task` certificates; those are structural/task-relative checks rather than ground-truth accuracy or intelligibility probabilities. See [`docs/TARGET_SEMANTICS.md`](docs/TARGET_SEMANTICS.md) for the domain-by-domain mapping.

## Quick test

```sh
sh tests/smoke-test.sh
```

The smoke test automatically runs `sh -n` across every script under `domains/`, so the split OCR/TTS files are included in syntax validation.

## Run domains

```sh
sh tools/run-domain.sh trader
printf 'cosmic love\n5\n' | sh tools/run-domain.sh music
sh tools/run-domain.sh ocr
sh tools/run-domain.sh ocr2
sh tools/run-domain.sh tts2
```

`ocr2` and `tts2` are independent: OCR can stop at `.ocr.txt`, and TTS can consume any `.txt` file without running OCR first.

The restored Cosmic program recursively re-executes and self-rewrites by design; run it only in a disposable copy/directory if you want to preserve the original file.

## Reversible source certificate

To assign any source file a reversible natural-number representation without SHA/hash:

```sh
sh tools/source-godel.sh domains/OCR_2KB.sh
sh tools/source-godel.sh domains/TTS_2KB.sh
```

This produces a `GDOMAIN` base-257 source encoding. `GDOMAIN` is an identity/certificate for source bytes; it does **not** magically make the source executable by `UTM.sh`. Executability requires compilation of the source semantics into TM transitions.

## OCR/TTS dependencies

`OCR_2KB.sh` requires `tesseract` and `file`; for PDF rendering it prefers `mutool` and falls back to `pdftoppm`. It canonicalizes the temporary directory with `realpath` to avoid the macOS `/tmp` -> `/private/tmp` pathname issue observed with Tesseract/Leptonica.

`TTS_2KB.sh` requires `espeak-ng` and writes `.tts.wav`.

The combined portable OCR script supports either `espeak-ng` or legacy `espeak`. Keep Alpine/iSH repositories consistent; do not mix branches merely to obtain a newer speech package.

## Zero-entropy terminology

The reported `H_* = 0` values are structural/task-relative uniqueness checks inside the declared candidate/equivalence system. They are not claims of zero thermodynamic entropy or guaranteed external correctness/profit.
