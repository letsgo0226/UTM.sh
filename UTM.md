# UTM.sh

Stateful universal Turing machine interpreter (Python one-liner in a bash wrapper).
The transition table is given as text (`PROGRAM`) or as its Gödel number (`GPROGRAM`, base-257 encoding of the program bytes); tape/state persist in a JSON file between calls.

Env:

| Var | Default | Meaning |
|-----|---------|---------|
| `CMD` | `step` | `step` (one transition), `run` (until halt or `LIMIT`), `reset` (reload `INPUT`, no step), `encode` (no step; print state + `GPROGRAM`) |
| `PROGRAM` | `""` | rules `q,s,q',w,D;...` with `D ∈ {L,R,other=stay}` |
| `GPROGRAM` | `""` | Gödel number of `PROGRAM` (used only if `PROGRAM` is empty) |
| `INPUT` / `START` / `BLANK` | `""` / `0` / `_` | initial tape, start state, blank symbol |
| `LIMIT` | `10000` | max transitions for `CMD=run` |
| `TM_STATE` | `utm.json` | state file |

Output: `{"q","h","t","halt","tape","GPROGRAM"}`. The machine halts when no rule matches `(q, tape[h])`.

## Certified demo (binary increment)

```sh
PROG='0,0,0,0,R;0,1,0,1,R;0,_,1,_,L;1,1,1,0,L;1,0,2,1,L;1,_,2,1,L'
rm -f utm.json
PROGRAM="$PROG" INPUT=1011 CMD=reset bash UTM.sh
PROGRAM="$PROG" CMD=run bash UTM.sh
# {"q":"2","h":0,"t":8,"halt":true,"tape":"1100","GPROGRAM":"18284878…084658"}
```

`111 → 1000` (`h=-2`), `LIMIT=3 → t=3,h=3,halt=false`, empty program → `{"q":"0","h":0,"t":0,"halt":true,"tape":"_","GPROGRAM":"1"}`.

## Resident

- Daemon: `UTM_DAEMON.sh` (default **1s**): `CMD=step` on a persistent state, each step checked against the exact 8-step trace; on halt it asserts `tape=1100` and resets.
  Every 3 steps a **replay-reconstruct** re-derives the current state from `reset` via the `GPROGRAM` decode path (`CF`) and runs a full `CMD=run` certificate (`CR`).
  KILL switch: `touch run/KILL` (or `UTM_KILL=1`).
- Actions: `.github/workflows/UTM.yml` (`*/5`, `workflow_dispatch`, `push`).

## Bound

`C` / `CF` / `CR` and `open=1` are formal machine credentials computed by the daemon/CI from UTM.sh output (trace equality, Gödel round-trip, halting on the demo input). They certify this interpreter on this program only — not a TOE, RH, or physical claim.
