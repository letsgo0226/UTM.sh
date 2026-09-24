# UTM.sh

Stateful universal Turing machine one-liner: rules via `PROGRAM` or their Gödel number `GPROGRAM`, `CMD=step|run|reset|encode`, state in `TM_STATE` (default `utm.json`). See [`UTM.md`](UTM.md).

| Artifact | Role |
|----------|------|
| `UTM.sh` | One-liner (~1375B) |
| `UTM_DAEMON.sh` | Resident loop (default 1s, replay-reconstruct every 3 steps) |
| `.github/workflows/UTM.yml` | Actions `*/5` + `workflow_dispatch` + `push` |

```sh
PROG='0,0,0,0,R;0,1,0,1,R;0,_,1,_,L;1,1,1,0,L;1,0,2,1,L;1,_,2,1,L'
rm -f utm.json
PROGRAM="$PROG" INPUT=1011 CMD=reset bash UTM.sh
PROGRAM="$PROG" CMD=run bash UTM.sh          # tape 1011 -> 1100, t=8, halt=true

# resident daemon (log: UTM_daemon.log, KILL: touch run/KILL)
nohup bash UTM_DAEMON.sh 1 >> UTM_daemon.log 2>&1 &

# Actions
gh workflow run UTM.yml -R letsgo0226/UTM.sh
```

Bound: formal machine credentials (`C`/`CF`/`CR`, `open=1`) only — not a TOE/RH/physical claim.
