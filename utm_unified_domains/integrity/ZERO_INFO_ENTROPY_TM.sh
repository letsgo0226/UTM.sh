#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/utm-zero-info-$$.json"}
P='0,D,1,1,R;1,U,2,1,R;2,R,3,1,R;3,G,4,1,R;4,I,5,1,R'
DET=${DETERMINISTIC_VERIFIED:-0};REV=${REVERSIBLE_VERIFIED:-0};INT=${INTEGRITY_VERIFIED:-0};B=${OPEN_BRANCHES:-0}
V0=${CURRENT_VECTOR:-0,0,0,0,0,0};V1=${NEXT_VECTOR:-$V0}
META=$(V0="$V0" V1="$V1" python3 -S -c 'import json as j,os
from fractions import Fraction as F
P=(2,3,5,7,11,13)
def v(k):
 x=tuple(map(int,os.environ[k].split(",")))
 assert len(x)==len(P)
 return x
a,b=v("V0"),v("V1");d=tuple(y-x for x,y in zip(a,b));r=F(1,1)
for p,e in zip(P,d):r*=F(p**e,1) if e>=0 else F(1,p**(-e))
c=(r-1)/(r+1);z=all(e==0 for e in d);terms=[]
for p,e in zip(P,d):
 if e:terms.append(("+" if e>0 and terms else "")+str(e)+"*ln("+str(p)+")")
print(j.dumps({"primes":P,"current":a,"next":b,"delta":d,"ratio":[r.numerator,r.denominator],"log_ratio_symbolic":"".join(terms) or "0","compactified_signed":[c.numerator,c.denominator],"godel_log_displacement_zero":z},separators=(",",":")))')
G=$(META="$META" python3 -S -c 'import json,os;print(1 if json.loads(os.environ["META"])["godel_log_displacement_zero"] else 0)')
[ "$B" = 1 ] && UNI=1 || UNI=0
X="$( [ "$DET" = 1 ] && printf D || printf x )$( [ "$UNI" = 1 ] && printf U || printf x )$( [ "$REV" = 1 ] && printf R || printf x )$( [ "$G" = 1 ] && printf G || printf x )$( [ "$INT" = 1 ] && printf I || printf x )"
OUT=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=10 sh "$K");rm -f "$F"
OUT="$OUT" META="$META" X="$X" DET="$DET" UNI="$UNI" REV="$REV" INT="$INT" python3 -S -c 'import json as j,os
u=j.loads(os.environ["OUT"]);m=j.loads(os.environ["META"]);det=os.environ["DET"]=="1";uni=os.environ["UNI"]=="1";rev=os.environ["REV"]=="1";integ=os.environ["INT"]=="1";cond=det and uni;fix=cond and rev and integ and m["godel_log_displacement_zero"];accept=(os.environ["X"]=="DURGI" and u.get("halt") and u.get("tape")=="11111" and u.get("t\")==5)
print(j.dumps({"model":"UTM_FORMAL_ZERO_INFO_ENTROPY/1.0","utm":u,"godel_log_coordinate":m,"certificate":{"conditional_entropy_zero":cond,"formal_zero_information_fixed_point":fix,"utm_accept":bool(accept)},"semantics":{"H_conditional":"0 iff deterministic_verified=1 and exactly one admissible tableau branch","delta_L":"sum_i delta_i*ln(p_i)","compactification":"c=(R-1)/(R+1)=tanh(delta_L/2); exact rational via R","zero":"fixed-point certificate requires H_conditional=0, reversibility, integrity, and delta_L=0"},"boundary":"formal information certificate only; not a claim of zero physical/thermodynamic entropy"},separators=(",",":")))'
