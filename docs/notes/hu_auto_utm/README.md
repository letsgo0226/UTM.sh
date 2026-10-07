# HU-AUTO-UTM/1.0

This note archives the 2 KB one-line iSH prototype for a pure-Turing-machine-style automatic executor.

## Artifact

`HU_AUTO_UTM_2K_oneline.sh`

- Size: 1158 bytes
- Physical lines: 1
- Host: Python 3 on iSH or any POSIX shell with Python 3
- Generated programs: finite binary single-tape Turing-machine descriptions
- Search: Cantor-enumerated transition tables
- Scheduling: diagonal dovetailing
- State persistence: `hu_tm.state`

## Model

The host Python process is only the simulator. The searched/generated programs themselves are Turing-machine transition descriptions rather than shell commands.

The recurrence is:

[
mathrm{HU!-!AUTO!-!UTM}
=
mathrm{Verify}
circ
mathrm{Dovetail}
circ
U
circ
mathrm{Enumerate}.
]

Each generation enumerates finite candidate TM descriptions, simulates them for a dovetailed finite budget, and records candidates that halt with the requested finite target output.

## Usage

```sh
chmod +x HU_AUTO_UTM_2K_oneline.sh
./HU_AUTO_UTM_2K_oneline.sh
```

Override the input and finite target:

```sh
TM_WORD=1 TM_TARGET=0 ./HU_AUTO_UTM_2K_oneline.sh
```

Use a different persistent generation counter:

```sh
TM_STATE=my_tm.state ./HU_AUTO_UTM_2K_oneline.sh
```

Adjust generation delay:

```sh
TM_SLEEP=0.05 ./HU_AUTO_UTM_2K_oneline.sh
```

## Boundaries

The certificate explicitly retains:

```text
host_shell_exec = 0
global_halting_decider = 0
global_arithmetic_complete = 0
self_awareness = 0
```

Enumerating every finite TM description does not provide a universal halting decider. A non-halting candidate is not classified as non-halting merely because it has not halted yet.

This is therefore an open-ended enumerative program synthesizer and simulator, not a universal solver or oracle.
