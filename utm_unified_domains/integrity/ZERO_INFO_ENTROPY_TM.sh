#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/utm-cczis-$$.json"}
P='0,C,1,1,R;1,K,2,1,R;2,S,3,1,R;3,E,4,1,R;4,I,5,1,R'
CONS=${CONSISTENT_VERIFIED:-0};CLOS=${RELEVANT_CLOSURE_VERIFIED:-0};COMP=${SUFFICIENT_COMPLETE_VERIFIED:-0};INT=${INTEGRITY_VERIFIED:-0}
B=${OPEN_BRANCHES:-0};EC=${BRANCH_EQUIV_CLASSES:-0};DET=${DETERMINISTIC_VERIFIED:-0};REV=${REVERSIBLE_VERIFIED:-0}
V0=${CURRENT_VECTOR:-0,0,0,0,0,0};V1=${NEXT_VECTOR:-$V0}
META=$(V0="$V0" V1="$V1" B="$B" EC="$EC" python3 -S -c 'import json as j,os
from fractions import Fraction as F
P=(2,3,5,7,11,13)
def v(k):
 x=tuple(map(int,os.environ[k].split(",")));assert len(x)==len(P);return x
a,b=v("V0"),v("V1");d=tuple(y-x for x,y in zip(a,b));r=F(1,1)
for p,e in zip(P,d):r*=F(p**e,1) if e>=0 else F(1,p**(-e))
c=(r-1)/(r+1);terms=[]
for p,e in zip(P,d):
 if e:terms.append(("+" if e>0 and terms else "")+str(e)+"*ln("+str(p)+")")
nb=int(os.environ["B"]);ec=int(os.environ["EC"]);h="0" if ec==1 else ("ln("+str(ec)+")" if ec>1 else "undefined(no semantic branch class)")
print(j.dumps({"primes":P,"current":a,"next":b,"delta":d,"ratio":[r.numerator,r.denominator],"log_ratio_symbolic":"".join(terms) or "0","compactified_signed":[c.numerator,c.denominator],"state_displacement_zero":all(e==0 for e in d),"open_branches":nb,"semantic_equivalence_classes":ec,"unresolved_entropy_symbolic":h},separators=(",",":")))')
EQ=$(META="$META" python3 -S -c 'import json,os;m=json.loads(os.environ["META"]);print(1 if m["open_branches"]>=1 and m["semantic_equivalence_classes"]==1 else 0)')
X="$( [ "$CONS" = 1 ] && printf C || printf x )$( [ "$CLOS" = 1 ] && printf K || printf x )$( [ "$COMP" = 1 ] && printf S || printf x )$( [ "$EQ" = 1 ] && printf E || printf x )$( [ "$INT" = 1 ] && printf I || printf x )"
OUT=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=10 sh "$K");rm -f "$F"
OUT="$OUT" META="$META" X="$X" CONS="$CONS" CLOS="$CLOS" COMP="$COMP" EQ="$EQ" INT="$INT" DET="$DET" REV="$REV" python3 -S -c 'import json as j,os
u=j.loads(os.environ["OUT"]);m=j.loads(os.environ["META"]);cons=os.environ["CONS"]=="1";clos=os.environ["CLOS"]=="1";comp=os.environ["COMP"]=="1";eq=os.environ["EQ"]=="1";integ=os.environ["INT"]=="1";cczis=cons and clos and comp and eq and integ;accept=(os.environ["X"]=="CKSEI" and u.get("halt") and u.get("tape")=="11111" and u.get("t")==5)
print(j.dumps({"model":"UTM_CCZIS/2.0","name":"Consistency-Complete Zero Information State","utm":u,"godel_log_coordinate":m,"certificate":{"consistent":cons,"relevant_closure":clos,"sufficiently_complete":comp,"single_relevant_semantic_class":eq,"integrity":integ,"zero_unresolved_information_entropy":cczis,"utm_accept":bool(accept)},"diagnostics":{"deterministic_verified":os.environ["DET"]=="1","reversible_verified":os.environ["REV"]=="1","state_displacement_zero":m["state_displacement_zero"]},"semantics":{"H_unresolved":"0 iff the admissible open branches form exactly one equivalence class relative to the declared problem domain","sufficient_completeness":"all information obligations required by the declared problem domain are resolved or explicitly classified as unknown/undecidable","delta_L":"sum_i delta_i*ln(p_i); information-state displacement, not entropy","compactification":"c=(R-1)/(R+1)=tanh(delta_L/2); exact rational via R","cczis":"consistency AND relevant closure AND sufficient completeness AND one relevant semantic branch class AND integrity","change_not_entropy":True},"boundary":"formal, scope-relative information certificate only; not absolute logical completeness and not zero physical/thermodynamic entropy"},separators=(",",":")))'
