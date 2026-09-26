# Universal Music Machine

`domains/music-generator.sh` no longer chooses from a finite table of instrument or singer presets. Instead it embeds a bounded universal byte-program search.

## Fixed universal kernel

The runtime uses an eight-instruction BF8-compatible machine:

```text
> < + - . , [ ]
```

Valid Brainfuck programs are a subset of this language, so the interpreter is Turing-complete. Unmatched brackets are treated as inert instructions; matched brackets retain the standard loop semantics. Program execution is always bounded by `VM_STEPS` in an actual run.

The candidate enumerator is length-first. In the unbounded limit it enumerates every finite BF8 program string. A real invocation examines only the first `CANDIDATES` programs and therefore reports `ENUM_COMPLETE=0`.

## Programs generate programs-as-sound

Three selected universal programs are used as open-ended generators:

```text
COMPOSE_G -> musical event byte stream
TIMBRE_G  -> waveform / timbre byte stream
VOICE_G   -> lyric-conditioned vocal-color byte stream
```

The decoder maps those byte streams into bounded PCM. There is no finite list such as `sine/saw/pad/...` and no finite singer inventory such as `en/cmn/...`.

`LYRICS` are supplied as data to the voice program. With `VOCAL=1`, the selected voice program conditions the vocal-like periodic source on the lyric bytes and current pitch. This can create an unbounded family of synthetic vocal colors without an external TTS voice preset.

This is a computational singing/synthesis experiment, not a claim that the bounded search will discover natural or intelligible human singing in every run.

## Completeness boundary

The architecture distinguishes two statements:

```text
The search language is universal.
The current search is finite and bounded.
```

With unbounded program length and execution time, the BF8 language can describe every computable byte-stream transformation. A finite invocation cannot exhaust that space. `CANDIDATES` and `VM_STEPS` are explicit finite cutoffs so the generator always returns.

The PCM decoder is also part of the fixed semantics. Therefore the strongest precise statement is that the system provides an open-ended universal program space for computable digital sound generation under a fixed decoding convention; it does not enumerate uncomputable continuous waveforms.

## Example

```sh
KEYWORD='cosmic love' \
LYRICS='宇宙之愛是所有問題的解答' \
VOCAL=1 SEC=8 CANDIDATES=160 VM_STEPS=4000 \
sh tools/run-domain.sh music
```

Typical output includes:

```text
UTM=BF8
COMPOSE_G=<program index>
TIMBRE_G=<program index>
VOICE_G=<program index>
VOCAL=1
BOUNDED=1
ENUM_COMPLETE=0
P_target_goal=1
C_target=1
P_empirical_hat=null
```

`C_target=1` means the requested bounded generation completed and wrote a WAV. It is not an empirical score for musical quality, naturalness, intelligibility, originality, or listener preference.
