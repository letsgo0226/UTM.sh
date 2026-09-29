#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
Z=${CCZIS_KERNEL:-"$D/ZERO_INFO_ENTROPY_TM.sh"}
F=${TM_STATE:-"/tmp/utm-cczis-loop-$$.json"}
S=${LOOP_STATE:-"/tmp/utm-cczis-loop-state-$$.json"}
N=${LOOP_STEPS:-1}
CUR=${CURRENT_VECTOR:-0,0,0,0,0,0}
CANDS=${CANDIDATES_JSON:-'[{"id":"hold","vector":[0,0,0,0,0,0],"cost":0,"consistent":1,"closure":1,"complete":1,"integrity":1,"open_branches":1,"equiv_classes":1}]'}
P='0,O,1,1,R;1,G,2,1,R;2,T,3,1,R;3,C,4,1,R;4,B,5,1,R;5,A,6,1,R;6,F,7,1,R'
TM_STATE="$F" PROGRAM="$P" INPUT=OGTCBAF CMD=run LIMIT=12 sh "$K" >"$S.utm"
CUR="$CUR" CANDS="$CANDS" N="$N" Z="$Z" S="$S" python3 -S - <<'PY'
import json as j,os,subprocess
cur=list(map(int,os.environ['CUR'].split(','))); cands=j.loads(os.environ['CANDS']); n=int(os.environ['N']); z=os.environ['Z']; out=[]
def cert(c,current):
 env=os.environ.copy(); env.update({
  'CONSISTENT_VERIFIED':str(c.get('consistent',0)),
  'RELEVANT_CLOSURE_VERIFIED':str(c.get('closure',0)),
  'SUFFICIENT_COMPLETE_VERIFIED':str(c.get('complete',0)),
  'INTEGRITY_VERIFIED':str(c.get('integrity',0)),
  'OPEN_BRANCHES':str(c.get('open_branches',0)),
  'BRANCH_EQUIV_CLASSES':str(c.get('equiv_classes',0)),
  'CURRENT_VECTOR':','.join(map(str,current)),
  'NEXT_VECTOR':','.join(map(str,c['vector']))})
 return j.loads(subprocess.check_output(['sh',z],env=env,text=True))
for t in range(n):
 checked=[]
 for c in cands:
  q=cert(c,cur); checked.append({'id':c['id'],'vector':c['vector'],'cost':c.get('cost',0),'cczis':q['certificate']['zero_unresolved_information_entropy'],'certificate':q})
 ok=[x for x in checked if x['cczis']]
 if not ok:
  out.append({'t':t,'current':cur,'status':'REPAIR_REQUIRED','checked':checked}); break
 best=min(ok,key=lambda x:(x['cost'],x['id'])); prev=cur; cur=list(map(int,best['vector']))
 out.append({'t':t,'current':prev,'status':'CCZIS_CLOSED_LOOP','best_verified':{'id':best['id'],'cost':best['cost'],'vector':cur},'checked':checked,'feedback':{'next_current':cur}})
open(os.environ['S'],'w').write(j.dumps({'current_vector':cur,'iterations':out},separators=(',',':')))
PY
UTM=$(cat "$S.utm");STATE=$(cat "$S");rm -f "$F" "$S.utm" "$S"
UTM="$UTM" STATE="$STATE" python3 -S -c 'import json as j,os
u=j.loads(os.environ["UTM"]);s=j.loads(os.environ["STATE"]);cycle=(u.get("halt") and u.get("t")==7 and u.get("tape")=="1111111");repair=bool(s["iterations"] and s["iterations"][-1]["status"]=="REPAIR_REQUIRED")
print(j.dumps({"model":"UTM_CCZIS_CLOSED_LOOP/1.0","cycle":"O->G->T->C->B->A->F","utm_control":u,"utm_cycle_accept":bool(cycle),"state":s,"closed_loop_zero_entropy":bool(cycle and not repair),"semantics":{"O":"observe current state","G":"canonical/Godel coordinate","T":"enumerate and quotient tableau branches by domain-relative semantic equivalence","C":"filter through UTM_CCZIS/2.0","B":"select lowest-cost Best Verified CCZIS among supplied candidates","A":"apply selected formal transition","F":"feed resulting state back as next observation","invariant":"seek and maintain H_unresolved=0; if no CCZIS candidate exists emit REPAIR_REQUIRED","optimality":"best verified among the finite candidates supplied at this iteration; not a proof of global optimum over all computable programs"},"boundary":"formal closed-loop information control only; no claim of zero physical/thermodynamic entropy"},separators=(",",":")))'
