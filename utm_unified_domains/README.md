# Unified UTM Domain Pack

This pack combines one fixed TM interpreter/toolchain with four existing domain runtimes:

- `cosmic-love-infinity-tm.sh` — restored legacy self-evolving prime/Gödel core.
- `Trader_42.sh` — restored persistent prime/Gödel TM core (from the prior `42.sh`).
- `music-generator.sh` — the unbounded-action music generator supplied in the current conversation.
- `ocr-tts.sh` — OCR/TTS consensus program; portable version prefers `espeak-ng` and falls back to `espeak`.

## Important boundary

`utm/UTM.sh` is a fixed deterministic single-tape TM interpreter. A program is *purely inside the UTM* only after its algorithm has been compiled into the transition-table format consumed by `UTM.sh`.

The four scripts under `domains/` are currently domain runtimes. Music uses Python/wave; OCR uses Tesseract/eSpeak; the restored Cosmic/Trader scripts use Python. Therefore the package is presently a **UTM-controlled / UTM-toolchain architecture**, not a claim that Tesseract, eSpeak, Python, or all four full algorithms have already been compiled into one TM transition table.

`examples/domain-control.tm` demonstrates the common control plane:

`Enumerate -> Validate -> Purpose -> Commit`

Compile it with:

```sh
sh tools/build-control.sh
```

The compiler prints both `PROGRAM=...` and reversible base-257 `GPROGRAM=...`.

## Quick test

```sh
sh tests/smoke-test.sh
```

## Run domains

```sh
sh tools/run-domain.sh trader
printf 'cosmic love\n5\n' | sh tools/run-domain.sh music
sh tools/run-domain.sh ocr
```

The restored Cosmic program recursively re-executes and self-rewrites by design; run it only in a disposable copy/directory if you want to preserve the original file.

## Reversible source certificate

To assign any source file a reversible natural-number representation without SHA/hash:

```sh
sh tools/source-godel.sh domains/music-generator.sh
```

This produces a `GDOMAIN` base-257 source encoding. `GDOMAIN` is an identity/certificate for source bytes; it does **not** magically make the source executable by `UTM.sh`. Executability requires compilation of the source semantics into TM transitions.

## OCR on iSH

The portable OCR script supports either `espeak-ng` or legacy `espeak`. PDF OCR additionally requires `pdftoppm`. Keep Alpine/iSH repositories consistent; do not mix branches merely to obtain a newer speech package.

## Zero-entropy terminology

The reported `H_* = 0` values are structural/task-relative uniqueness checks inside the declared candidate/equivalence system. They are not claims of zero thermodynamic entropy or guaranteed external correctness/profit.
