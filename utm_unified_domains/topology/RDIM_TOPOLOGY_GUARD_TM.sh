#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/rdim-topology-utm-$$.json"}
P='0,S,1,1,R;1,H,2,1,R;2,E,3,1,R;3,T,4,1,R'
X=${RDIM_CERT_INPUT:-SHET}
U=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=8 sh "$K")
rm -f "$F"
U="$U" X="$X" python3 -S -c 'import json as j,os
u=j.loads(os.environ["U"]);x=os.environ["X"];ok=x=="SHET" and u.get("halt") and u.get("tape")=="1111" and u.get("t")==4
print(j.dumps({"model":"RDIM_TOPOLOGY_GUARD_TM","manifold":"M_delta","input":x,"utm":u,"accept":bool(ok),"obligations":{"S":"bootstrap/continuation seed identified","H":"finality/fencing horizon defined","E":"acyclic parent-child embedding identified","T":"thermodynamic-information and tamper-evident lineage inherited"},"scope":"bounded computational topology certificate only; does not establish physical nested dimensions, simulation status, or an infinite tower"},separators=(",",":")))'
