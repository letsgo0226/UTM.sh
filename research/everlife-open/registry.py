"""Everlife Open: a bounded, deterministic public research registry.
Purely synthetic formal model. No medical, veterinary or trading action.
"""
import json
import math
import hashlib
from pathlib import Path
from itertools import product

HERE = Path(__file__).resolve().parent
V = {(r, b) for r in range(2, 5) for b in range(4)}

def transition(x, action, shock, refill):
    r, b = x
    r = max(0, r - shock)
    if action > min(1, b + refill, 4 - r):
        return None
    return (r + action, min(3, b + refill - action))

def kernel(refill):
    k = set(V)
    history = [len(k)]
    while True:
        n = {x for x in k if any(all(transition(x, a, w, refill) in k for w in (0, 1)) for a in (0, 1))}
        if n == k:
            return k, history
        k = n
        history.append(len(k))

def exhaustive(refill):
    safe_union = set()
    for actions in product((0, 1), repeat=len(V)):
        policy = dict(zip(sorted(V), actions))
        k = set(V)
        while True:
            n = {x for x in k if all(transition(x, policy[x], w, refill) in k for w in (0, 1))}
            if n == k: break
            k = n
        safe_union.update(k)
    return safe_union

def encode257(data):
    n = 1
    for b in data:
        n = 257*n+b+1
    return n

def decode257(n):
    out = []
    while n > 1:
        n, r = divmod(n, 257)
        if r == 0: raise ValueError('invalid digit')
        out.append(r-1)
    return bytes(out[::-1])

def atgc(data):
    return ''.join('TC' if b & (1 << i) else 'AG' for b in data for i in range(7, -1, -1))

def decode_atgc(s):
    if len(s) % 16 or any(s[i:i+2] not in ('AG', 'TC') for i in range(0, len(s), 2)):
        raise ValueError('invalid symbol code')
    return bytes(int(''.join('1' if s[k:k+2]=='TC' else '0' for k in range(j,j+16,2)),2) for j in range(0,len(s),16))

def reversible_u(q, h, tape, z):
    c=decode257(4448070169)
    v=c[2*q+int(h in tape)]
    return (v%3, h+1-2*q, tape, z*(1j if q==0 else -1j))

def build():
    seed=b'Everlife-GSH-GSSG-toy'
    assert decode257(encode257(seed)) == seed
    assert decode_atgc(atgc(seed)) == seed
    assert all(reversible_u(*reversible_u(q,h,t,1))==(q,h,t,1) for q in (0,1) for h in (0,1) for t in ((),(0,)))
    records={}
    for refill in (0,1):
        k,h=kernel(refill)
        assert k == exhaustive(refill)
        records[str(refill)]={'safe_kernel_size':len(k),'initial_safe_states':12,
            'elimination_history':h,'exhaustive_policies_tested':4096}
    assert records['0']['safe_kernel_size']==0 and records['1']['safe_kernel_size']==12
    raw=Path(__file__).read_bytes()
    return {
        'schema':'Everlife-Open-Registry/1.0',
        'published_status':'FORMAL_MODEL_VERIFIED_NOT_BIOLOGICALLY_VALIDATED',
        'updated_by':'deterministic source, finite exhaustive tests',
        'research_fields':['human_healthspan','feline_welfare','canine_welfare','environment','ai_system_continuity'],
        'species':{k:{'validation':None,'dosing':None} for k in ('human','cat','dog')},
        'model':{'type':'dimensionless finite state GSH/GSSG-inspired toy',
                 'replenished_and_finite':records,'empirical_estimate':None,
                 'clinical_or_veterinary_efficacy':None},
        'formal':{'G257_roundtrip':True,'ATGC_roundtrip':True,'U2_finite_involution':True,
                  'finite_policy_enumeration':True,'universal_halting_solver':False,
                  'bounded_does_not_mean_nonhalting':True,
                  'conditional_information_entropy_zero_does_not_mean_physical_entropy_zero':True,
                  'Landauer_310K_J_per_unbiased_erased_bit':1.380649e-23*310*math.log(2)},
        'sdgs':{'thematic_alignment':[3,9,12,13,15,17],'verified_UN_indicator_results':None},
        'ai_continuity':{'source_and_provenance_preservation':True,
                         'autonomous_self_replication':False,
                         'model_weights_preserved':False,
                         'authorized_shutdown_required':True},
        'safety':{'medical_or_veterinary_use':False,'no_untested_dose':True,
                  'no_automated_trades':True,'no_unauthorized_deploy':True},
        'provenance':{'sha256_registry_source':hashlib.sha256(raw).hexdigest(),
                      'evidence_kind':'synthetic_finite_test_not_experiment'},
        'license_metadata':'CC0-1.0'
    }

if __name__=='__main__':
    p=HERE/'public'/'latest.json'
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(build(),indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    print('VERIFIED synthetic registry:',p)
