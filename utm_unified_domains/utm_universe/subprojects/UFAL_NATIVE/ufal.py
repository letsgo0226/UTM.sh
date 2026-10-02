#!/usr/bin/env python3
"""Exact UFAL finite-state verifier.

Canonical identity is the exponent vector / exact Godel integer.
Logarithms are derived coordinates and are never used as authoritative equality.
"""
import math

MAX_SUPPORT=128
MAX_INDEX=4096
MAX_EXPONENT=100000
_PRIMES=[2]

SYSTEM_IDS={"U":0,"T":1,"C":2}

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d=3
    while d*d <= n:
        if n%d == 0: return False
        d += 2
    return True

def nth_prime(i):
    if not isinstance(i,int) or i < 0 or i > MAX_INDEX:
        raise ValueError(f"prime index must be 0..{MAX_INDEX}")
    c=_PRIMES[-1]+1
    if c%2 == 0: c += 1
    while len(_PRIMES) <= i:
        if is_prime(c): _PRIMES.append(c)
        c += 2
    return _PRIMES[i]

def cantor(a,b):
    if min(a,b) < 0: raise ValueError("Cantor inputs must be nonnegative")
    s=a+b
    return s*(s+1)//2+b

def atom_index(system, role_id, step):
    if system not in SYSTEM_IDS:
        raise ValueError("system must be U, T, or C")
    role_id, step=int(role_id), int(step)
    idx=cantor(cantor(SYSTEM_IDS[system],role_id),step)
    if idx > MAX_INDEX:
        raise ValueError("atom index exceeds finite verifier bound")
    return idx

def atom_prime(system, role_id, step):
    return nth_prime(atom_index(system,role_id,step))

def normalize(v):
    if not isinstance(v,dict) or len(v)>MAX_SUPPORT:
        raise ValueError(f"state must have <= {MAX_SUPPORT} nonzero coordinates")
    out={}
    for k,x in v.items():
        i,e=int(k),int(x)
        if i<0 or i>MAX_INDEX or e<0 or e>MAX_EXPONENT:
            raise ValueError("coordinate or exponent out of range")
        if e: out[i]=e
    return dict(sorted(out.items()))

def godel(v):
    v=normalize(v)
    g=1
    for i,e in v.items():
        g *= nth_prime(i)**e
    return g

def add(a,b):
    a,b=normalize(a),normalize(b)
    keys=set(a)|set(b)
    return {i:a.get(i,0)+b.get(i,0) for i in sorted(keys) if a.get(i,0)+b.get(i,0)}

def decode_system_godel(g):
    n=int(g)
    if n<1: raise ValueError("Godel integer must be >=1")
    out={}
    i=0
    while n>1:
        if i>MAX_INDEX:
            raise ValueError("factor exceeds verifier index bound")
        p=nth_prime(i)
        while n%p==0:
            out[i]=out.get(i,0)+1
            n//=p
            if out[i]>MAX_EXPONENT: raise ValueError("exponent exceeds bound")
        i+=1
        if p*p>n and n>1:
            # Remaining factor must still belong to our canonical enumeration.
            while i<=MAX_INDEX and nth_prime(i)<n:
                i+=1
            if i<=MAX_INDEX and nth_prime(i)==n:
                out[i]=out.get(i,0)+1
                n=1
            elif n>1:
                raise ValueError("noncanonical or out-of-bound prime factor")
    return dict(sorted(out.items()))

def log_coordinate(v, base=math.e):
    v=normalize(v)
    base=float(base)
    if base<=0 or math.isclose(base,1.0):
        raise ValueError("log base must be >0 and !=1")
    d=math.log(base)
    return math.fsum(e*math.log(nth_prime(i))/d for i,e in v.items())

def verify_state(v):
    v=normalize(v)
    G=godel(v)
    decoded=decode_system_godel(G)
    return {
        "valid":decoded==v,
        "vector":{str(k):e for k,e in v.items()},
        "godel":str(G),
        "roundtrip_unique":decoded==v,
        "canonical_truth":"prime-exponent-vector-and-exact-godel",
        "float_log_authoritative":False
    }

def verify_composition(a,b,base=math.e):
    a,b=normalize(a),normalize(b)
    s=add(a,b)
    ga,gb,gs=godel(a),godel(b),godel(s)
    la,lb,ls=log_coordinate(a,base),log_coordinate(b,base),log_coordinate(s,base)
    return {
        "valid":(
            gs==ga*gb and
            decode_system_godel(gs)==s and
            add(a,b)==add(b,a) and
            math.isclose(ls,la+lb,rel_tol=1e-12,abs_tol=1e-12)
        ),
        "sum_vector":{str(k):e for k,e in s.items()},
        "godel_product_identity":gs==ga*gb,
        "unique_decode":decode_system_godel(gs)==s,
        "abelian_vector_sum":add(a,b)==add(b,a),
        "derived_log_homomorphism":math.isclose(ls,la+lb,rel_tol=1e-12,abs_tol=1e-12),
        "note":"log check is diagnostic only; exact identities are decided by integers/vectors"
    }
