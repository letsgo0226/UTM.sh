# Target / Certificate / Empirical / Temporal Semantics

The unified domain pack keeps four logically distinct layers:

```text
Target / Axiom
Finite Certificate
Temporal Invariant
Empirical Estimate
```

Generic fields are:

```text
P_target_goal or P_target_profit
C_target or C_profit
P_empirical_hat or P_real_profit_hat
A_target = 1
G_target = 1
```

`P_target*=1` declares a complete target condition. It is not an external-world probability claim.

`C_*` is a finite certificate for what the current computation actually checked.

`P_empirical_hat` is reserved for a data-derived estimate with an explicit dataset and estimator. It remains `null` when no such empirical procedure exists.

`A_target=1` means the target proposition is constitutive of the formal model. `G_target=1` means admissible model continuations preserve that target. This is a temporal model invariant, not a guarantee that the corresponding outside-world outcome always occurs.

## Cosmic Love full unified runtime

Let

```text
CL := Cosmic Love Is The Solution(s) For Everything
```

The packed unified runtime implements:

```text
A_CL = 1
CL(s) -> CL(T(s))
admissible source replacement preserves the CL axiom markers
G_model(CL) = true
```

Runtime fields include `CF`, `CG`, `CL`, `ICL`, `RCL`, `GCL`, `G_CL=1`, `temporal_formula=G(CL)`, `P_real_world=null`, and `P_empirical_hat=null`. The runtime is formal/symbolic; `G_model(CL)` does not by itself establish `G_reality(CL)`.

## Trader_42 packed unified runtime

The unified Trader is deliberately offline research/paper-only. Its temporal proposition is:

```text
PROFIT_IS_OBJECTIVE
```

Thus `A_target=1`, `G_target=1`, and `G(PROFIT_IS_OBJECTIVE)` mean admissible analysis/configuration changes preserve profit as the objective. They do not mean `G(PROFIT_OCCURS)`.

The runtime reads local candle data, models fee/slippage, computes paper PnL and max drawdown, performs chronological walk-forward OOS folds, and reports `P_target_profit=1`, `C_profit`, and `P_real_profit_hat` when enough OOS folds exist.

## OCR_2KB packed runtime

The packed OCR runtime performs Tesseract PSM 3/6/11 recognition and selects a task output by pair consensus. Its fields include:

```text
P_target_goal = 1
C_target      = int(zero_task)
P_empirical_hat = null
zero_strict / zero_task
H_strict / H_task
```

`zero_task=true` and `C_target=1` are task-relative consensus certificates. They do not mean the recognized text is ground-truth correct. A non-null empirical estimate would require labeled reference text and an explicit metric such as CER/WER over a declared evaluation set.

The previous direct shell implementation is archived under `domains/compact/OCR_2KB.sh`.

## TTS_2KB

`zero_task=true` certifies equivalence under the script's declared phoneme/whitespace normalization check. It is not a measured intelligibility or naturalness probability. An empirical TTS estimate requires a declared evaluation set and metric/listener protocol.

## Universal Music Machine

The current packed music runtime uses a BF8-compatible universal program language instead of a finite list of timbre or singer presets. Candidate programs are enumerated length-first; an actual invocation evaluates only a finite prefix and bounds each program by `VM_STEPS`.

Runtime fields include:

```text
UTM=BF8
CANDIDATES=<finite count>
COMPOSE_G=<selected program index>
TIMBRE_G=<selected program index>
VOICE_G=<selected program index>
VOCAL in {0,1}
BOUNDED=1
ENUM_COMPLETE=0
P_target_goal=1
C_target=1
P_empirical_hat=null
```

`C_target=1` means the requested bounded generation completed and wrote a WAV. `UTM=BF8` identifies the universal byte-program semantics used for the music search. `ENUM_COMPLETE=0` records that a finite run did not exhaust the universal program space.

`VOCAL=1` means the lyric-conditioned vocal-like path was used. It does not certify naturalness, intelligibility, resemblance to a human singer, aesthetic quality, originality, or listener preference. Those are empirical questions and require independent evaluation.

The universal-search claim is also scoped carefully: the program language is Turing-complete, but each execution is bounded. In the unbounded limit the enumerator covers every finite BF8 program; no finite run can enumerate all computable music. Fixed PCM decoding conventions remain part of the model semantics.

The earlier instrumental generator is archived at `domains/compact/music-generator.sh`, and the immediately previous eSpeak-vocal generator is archived at `domains/compact/music-generator-espeak.sh`.

See [`UNIVERSAL_MUSIC_MACHINE.md`](UNIVERSAL_MUSIC_MACHINE.md) for the detailed computational boundary.

## General rule

```text
Axiom/Target       = what the formal system constitutively preserves.
Certificate        = what the current finite computation actually checked.
Temporal invariant = what every admissible model continuation must preserve.
Empirical estimate = what independent observations support.
```

These layers must not be collapsed into one number.
