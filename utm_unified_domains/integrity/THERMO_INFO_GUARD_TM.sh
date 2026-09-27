#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/thermo-info-utm-$$.json"}
P='0,A,1,1,R;1,I,2,1,R;2,D,3,1,R;3,L,4,1,R'
A=${APPEND_ONLY:-0};I=${INTEGRITY_VERIFIED:-0};DUR=${DURABLE_COPY_VERIFIED:-0};L=${LANDAUER_ACCOUNTED:-0}
X="$( [ "$A" = 1 ] && printf A || printf x )$( [ "$I" = 1 ] && printf I || printf x )$( [ "$DUR" = 1 ] && printf D || printf x )$( [ "$L" = 1 ] && printf L || printf x )"
U=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=8 sh "$K")
rm -f "$F"
U="$U" X="$X" python3 -S -c 'import json as j,os,math
u=j.loads(os.environ["U"]);x=os.environ["X"];ok=(x=="AIDL" and u.get("halt") and u.get("tape")=="1111" and u.get("t")==4)
k=1.380649e-23;T=float(os.getenv("THERMAL_MODEL_K","300"));b=k*T*math.log(2)
print(j.dumps({"model":"THERMO_INFO_GUARD_TM","input":x,"utm":u,"utm_accept":bool(ok),"obligations":{"A":"append-only committed history","I":"lineage/integrity verification passes","D":"at least one durable copy verified under the declared fault model","L":"Landauer lower-bound accounting is recorded"},"thermodynamics":{"temperature_model_k":T,"landauer_j_per_irreversibly_erased_bit":b,"claim":"logical accounting only; UTM does not measure or control physical heat or thermodynamic entropy"},"loss_scope":"acceptance does not imply absolute no-loss; independent replicas/backups are required for correlated-failure resistance"},separators=(",",":")))'
