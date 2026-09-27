#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/recursive-dimension-utm-$$.json"}
P='0,R,1,1,R;1,D,2,1,R;2,I,3,1,R;3,T,4,1,R'
X=${RECURSIVE_CERT_INPUT:-RDIT}
U=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=8 sh "$K")
rm -f "$F"
U="$U" X="$X" python3 -S -c 'import json as j,os
u=j.loads(os.environ["U"]);x=os.environ["X"];ok=x=="RDIT" and u.get("halt") and u.get("tape")=="1111" and u.get("t")==4
print(j.dumps({"model":"RECURSIVE_DIMENSION_GUARD_TM","recursive_dimension":"delta","input":x,"utm":u,"accept":bool(ok),"obligations":{"R":"bounded recursion/cycle check","D":"dimension-index consistency","I":"interpreter-state-lineage binding","T":"thermodynamic-information guard inherited"},"scope":"bounded computational nesting certificate only; does not prove the observed physical world is simulated or that an infinite hierarchy exists"},separators=(",",":")))'
