#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
K=${UTM_KERNEL:-"$D/../utm/UTM.sh"}
POLICY=${UTM_DEPLOY_POLICY:-"$D/../deploy/UTM_DEPLOYMENT_GATEWAY_POLICY.json"}
F=${TM_STATE:-"/tmp/utm-deploy-gate-$$.json"}
P='0,P,1,1,R;1,V,2,1,R;2,C,3,1,R;3,A,4,1,R'
PROP=${PROPOSAL_JSON:-'{}'}
CUR_REV=${CURRENT_REVISION:-0}
CUR_DIGEST=${CURRENT_PARENT_DIGEST:-GENESIS}
PROP="$PROP" POLICY="$POLICY" CUR_REV="$CUR_REV" CUR_DIGEST="$CUR_DIGEST" python3 -S - <<'PY' >"$F.meta"
import json as j,os,hashlib,re
from pathlib import Path
p=j.loads(os.environ['PROP']);pol=j.loads(Path(os.environ['POLICY']).read_text());reasons=[]
if not isinstance(p,dict):reasons.append('proposal_not_object')
req=pol['required_fields']
for k in req:
 if k not in p:reasons.append('missing:'+k)
if p.get('action') not in pol['allowed_actions']:reasons.append('action_not_allowed')
try:
 if int(p.get('base_revision',-1))!=int(os.environ['CUR_REV']):reasons.append('base_revision_mismatch')
except:reasons.append('invalid_base_revision')
if str(p.get('parent_digest',''))!=os.environ['CUR_DIGEST']:reasons.append('parent_digest_mismatch')
if not isinstance(p.get('settings'),dict):reasons.append('settings_not_object')
cert=p.get('condition_certificate',{})
if not isinstance(cert,dict):reasons.append('condition_certificate_not_object');cert={}
for k,v in pol['condition_certificate'].items():
 if cert.get(k) is not v:reasons.append('condition_failed:'+k)
forbidden=set(pol['forbidden_keys'])
secret_pat=re.compile(r'(password|passwd|secret|token|api[_-]?key|private[_-]?key)',re.I)
def walk(x,path=''):
 if isinstance(x,dict):
  for k,v in x.items():
   kp=f'{path}.{k}' if path else k
   if k in forbidden:reasons.append('forbidden_key:'+kp)
   if secret_pat.search(k) and not (k.endswith('_ref') or k.endswith('_reference')):reasons.append('raw_secret_forbidden:'+kp)
   walk(v,kp)
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,f'{path}[{i}]')
walk(p.get('settings',{}))
canon=j.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
digest=hashlib.sha256(canon.encode()).hexdigest()
ok=not reasons
print(j.dumps({'protocol':pol['protocol'],'verified':ok,'reasons':sorted(set(reasons)),'proposal_digest':digest,'base_revision':p.get('base_revision'),'parent_digest':p.get('parent_digest'),'next_revision':int(os.environ['CUR_REV'])+1 if ok else int(os.environ['CUR_REV']),'continuation':pol['continuation'],'authorization':pol['authorization'],'boundary':pol['boundary']},separators=(',',':'),ensure_ascii=False))
PY
META=$(cat "$F.meta"); rm -f "$F.meta"
OK=$(META="$META" python3 -S -c 'import os,json;print(1 if json.loads(os.environ["META"])["verified"] else 0)')
[ "$OK" = 1 ] && X=PVCA || X=xxxx
U=$(TM_STATE="$F" PROGRAM="$P" INPUT="$X" CMD=run LIMIT=8 sh "$K");rm -f "$F"
U="$U" META="$META" python3 -S - <<'PY'
import json as j,os
u=j.loads(os.environ['U']);m=j.loads(os.environ['META']);accept=(u.get('halt') and u.get('t')==4 and u.get('tape')=='1111' and m['verified'])
print(j.dumps({'model':'UTM_GUARDED_DEPLOYMENT_ENTRY/1.0','utm_control':u,'utm_accept':bool(accept),'certificate':m,'semantics':{'P':'proposal schema/base/parent admitted','V':'all declared conditions verified','C':'immutable integrity certificate formed','A':'eligible for separately authorized commit; not external apply'},'boundary':'A valid certificate does not itself modify GitHub, Railway, secrets, or host code.'},separators=(',',':'),ensure_ascii=False))
PY