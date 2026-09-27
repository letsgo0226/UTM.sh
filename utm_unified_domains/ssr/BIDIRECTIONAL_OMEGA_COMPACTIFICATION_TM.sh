#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/omega-utm-$$.json"}
N=${OMEGA_DEPTH:-8}
P='0,G,1,1,R;1,S,2,1,R;2,R,3,1,R;3,H,4,1,R'
U=$(TM_STATE="$F" PROGRAM="$P" INPUT=GSRH CMD=run LIMIT=8 sh "$K")
rm -f "$F"
U="$U" N="$N" python3 -S -c 'import json as j,os
u=j.loads(os.environ["U"]);N=max(1,min(256,int(os.environ["N"])));ok=u.get("halt") and u.get("tape")=="1111" and u.get("t")==4
E=lambda s:__import__("functools").reduce(lambda a,b:a*257+b+1,s.encode(),1)
G0=E("P_0")
def row(k):
 g=E("P_%+d"%k);n=abs(k);return {"k":k,"P":"P_%+d"%k,"G":str(g),"L":"log(%s/%s)"%(g,G0),"u":[1 if k>0 else -1,n],"projection":"P_-1","normalized_resource":[1,1]}
plus=[row(n) for n in range(1,N+1)];minus=[row(-n) for n in range(1,N+1)]
print(j.dumps({"model":"BIDIRECTIONAL_OMEGA_COMPACTIFICATION_TM","kernel":"UTM.sh","utm":u,"utm_accept":bool(ok),"depth":N,"substrate":{"name":"P_-1","projection":"pi(P_k)=P_-1","resource_invariant":"C_hat(P_k)=C0","physical_resource_creation":False},"godel_log":{"encoding":"reversible base-257 numbering of finite labels","G0":str(G0),"coordinate":"L(P_k)=log(G(P_k)/G0)","note":"log coordinate is symbolic; it does not create compute"},"expansion":{"law":"S_k=lambda^k*S_0","lambda":"constant > 1","normalized_resource":"C_app(P_k)/lambda^k=C0"},"branches":{"plus":plus,"minus":minus},"compactification":{"u":"sign(k)/abs(k)","plus_limit":"0+","minus_limit":"0-","identification":"0+ ~ 0- ~ Omega","omega":"P_Omega","topology":"one-point compactification of the two unbounded directions"},"potentially_unbounded_hierarchy":True,"actual_infinite_physical_compute":False,"scope":"formal UTM hierarchy and boundary certificate only; not evidence that the physical universe has infinite computation or that distinct coordinate descriptions create independent hardware"},separators=(",",":")))'