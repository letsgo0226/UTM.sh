# Architecture

Fixed layer:

`UTM.sh + TMCC/UASM/UMAC/UMACR`

Mutable/domain layer:

`Cosmic | Trader | Music | OCR/TTS`

Formal target:

`Domain source -> compiler -> PROGRAM/GPROGRAM -> fixed UTM -> output tape`

Current practical bridge:

`fixed UTM control plane + external domain runtime`

This distinction is intentional. Encoding source bytes as `GDOMAIN` is reversible data representation, while compiling domain semantics to transition rules is the actual UTM compilation problem.
