#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/ssr-utm-$$.json"}
P='0,G,1,1,R;1,S,2,1,R;2,R,3,1,R;3,H,4,1,R'
U=$(TM_STATE="$F" PROGRAM="$P" INPUT=GSRH CMD=run LIMIT=8 sh "$K")
rm -f "$F"
U="$U" python3 -S -c 'import json as j,os,math;from fractions import Fraction as F
P=(2,3,5,7,11,13);a=[0]*6;G0=math.prod(P);G=math.prod(p**(x+1) for p,x in zip(P,a));R=F(G,G0);u=j.loads(os.environ["U"]);ok=u.get("halt") and u.get("tape")=="1111" and u.get("t")==4
Q={"godel":{"finite":"G(a)/G0","boundary":"a=(0,...,0)","extension":[R.numerator,R.denominator],"proof_kind":"exact rational identity"},"stirling":{"coordinate":"u=1/n","finite":"Gamma(1/u)/(sqrt(2*pi)*(1/u)^(1/u-1/2)*exp(-1/u))","boundary":"u=0","extension":[1,1],"proof_kind":"asymptotic limit theorem"},"riemann":{"coordinate":"u=s-1","finite":"u*zeta(1+u)","boundary":"u=0","extension":[1,1],"proof_kind":"Laurent/residue limit at zeta pole s=1"},"schwarzschild":{"coordinate":"rho=1-rs/r","finite":"rho*g_rr","g_rr":"1/rho","boundary":"rho=0","extension":[1,1],"proof_kind":"algebraic identity in Schwarzschild coordinates; horizon is a coordinate singularity"}}
print(j.dumps({"model":"COMPACTIFIED_SINGULAR_LIMIT_TM","kernel":"UTM.sh","utm":u,"utm_accept":bool(ok),"channel_order":"GSRH = Godel, Stirling, Riemann, Schwarzschild-horizon","boundary_vector":[[1,1]]*4,"boundary_invariant":[1,1],"identity":"R_Godel=R_Stirling(0)=R_Riemann(0)=R_Schwarzschild(0)=1","compactification":"infinity -> u=0 for Stirling; pole/horizon coordinates -> 0 in their local charts","information_function":"I_boundary=sum_i |log R_i|","information":"0 at the normalized boundary fixed point","zero_information_fixed_point":True,"exactness":"exact rational/algebraic boundary values plus analytic/asymptotic theorems; no floating-point evaluation","scope":"formal normalization certificate only; not a proof of the Riemann hypothesis, not a physical identification of the three theories, and not thermodynamic zero entropy","channels":Q},separators=(",",":")))'