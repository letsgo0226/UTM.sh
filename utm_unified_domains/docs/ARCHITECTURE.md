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

## Cross-domain target semantics

Every domain should keep these layers separate:

`P_target_goal=1 -> C_target in {0,1} -> P_empirical_hat in [0,1] or null`

The first value is a declared goal, the second is a certificate for finite checks actually performed, and the third is a data-derived estimate only when an operational empirical procedure exists. See `TARGET_SEMANTICS.md`.
