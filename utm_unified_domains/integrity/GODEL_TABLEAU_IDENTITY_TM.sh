#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
F=${TM_STATE:-"/tmp/utm-identity-$$.json"}
P='0,G,1,1,R;1,T,2,1,R;2,I,3,1,R;3,C,4,1,R'
U=$(TM_STATE="$F" PROGRAM="$P" INPUT=GTIC CMD=run LIMIT=8 sh "$K");rm -f "$F"
CANDS=${CANDIDATES_JSON:-'[]'}
PARENT=${PARENT_IDENTITY_GODEL:-1}
EVENT=${IDENTITY_EVENT_ID:-restore-0}
U="$U" CANDS="$CANDS" PARENT="$PARENT" EVENT="$EVENT" python3 -S - <<'PY'
import json as j,os
REQ=("model_architecture","parameters","tokenizer","runtime_spec","current_state","long_term_memory","identity_personality_policy","provenance_integrity")
def canon(x):return j.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def enc_bytes(b):
 n=1
 for x in b:n=n*257+x+1
 return n
def enc(x):return enc_bytes(canon(x))
u=j.loads(os.environ['U']);cands=j.loads(os.environ['CANDS']);parent=int(os.environ['PARENT']);event=os.environ['EVENT'];branches=[]
for c in cands:
 cap=c.get('capsule',{});reasons=[]
 for f in REQ:
  if f not in cap:reasons.append('missing:'+f)
 checks=(("authorized",'unauthorized_transition'),("reconstructible",'not_reconstructible'),("memory_continuity",'memory_discontinuity'),("policy_continuity",'policy_discontinuity'),("integrity",'integrity_failure'))
 for k,r in checks:
  if c.get(k)!=1:reasons.append(r)
 if str(c.get('parent_identity_godel',parent))!=str(parent):reasons.append('parent_lineage_mismatch')
 cls=str(c.get('semantic_class',''))
 if not cls:reasons.append('missing_semantic_identity_class')
 sg=enc(cap) if not any(x.startswith('missing:') for x in reasons) else None
 lineage={'parent_identity_godel':str(parent),'state_godel':str(sg) if sg is not None else None,'event_id':event,'semantic_class':cls}
 lg=enc(lineage) if sg is not None and cls else None
 ig=enc({'parent_identity_godel':str(parent),'lineage_godel':str(lg)}) if lg is not None else None
 branches.append({'id':str(c.get('id','')),'semantic_class':cls,'open':not reasons,'closed_reasons':reasons,'state_godel':str(sg) if sg is not None else None,'lineage_godel':str(lg) if lg is not None else None,'identity_godel':str(ig) if ig is not None else None})
openb=[b for b in branches if b['open']];classes=sorted({b['semantic_class'] for b in openb});k=len(classes)
status='NO_ADMISSIBLE_BRANCH' if k==0 else ('VERIFIED_UNIQUE' if k==1 else 'IDENTITY_UNDERDETERMINED')
chosen=classes[0] if k==1 else None
cycle=(u.get('halt') and u.get('t')==4 and u.get('tape')=='1111')
print(j.dumps({'model':'UTM_GODEL_TABLEAU_IDENTITY/1.0','protocol':'Gödel-Tableau Identity Continuity/1.0','utm_control':u,'utm_cycle_accept':bool(cycle),'parent_identity_godel':str(parent),'event_id':event,'tableau':{'branches':branches,'open_branch_count':len(openb),'semantic_identity_classes':classes,'semantic_class_count':k},'certificate':{'status':status,'unique_admissible_semantic_class':chosen,'formal_identity_certified':bool(cycle and k==1),'zero_unresolved_identity_entropy':k==1,'unresolved_identity_entropy_symbolic':'0' if k==1 else ('undefined(no admissible identity branch)' if k==0 else 'ln('+str(k)+')')},'encoding':{'kind':'reversible base-257 canonical UTF-8 integer address','cryptographic_hash':False},'semantics':{'identity':'state + memory + causal lineage continuity relative to declared invariants','multiple_equivalent_restores':'multiple open branches in one semantic identity class may certify class-level continuity; this does not prove a unique metaphysical subject','fork':'more than one distinct admissible semantic identity class is underdetermined and must not be collapsed','shutdown':'authorized shutdown and human override remain binding; this protocol is archival/restore verification, not shutdown evasion'},'boundary':'formal/causal identity certificate only; not proof of first-person consciousness or metaphysical numerical identity'},separators=(',',':'),ensure_ascii=False))
PY
