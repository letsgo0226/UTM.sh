#!/usr/bin/env python3
"""UCBC finite verifier.

Exact identity is carried by integers and symbolic relations.
Real logarithm/base recovery is diagnostic and never authoritative.
"""
from decimal import Decimal, getcontext
import math

getcontext().prec = 80

def is_prime(n):
    n=int(n)
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d=3
    while d*d <= n:
        if n%d == 0: return False
        d += 2
    return True

def validate_prime_pair(a,b):
    a,b=int(a),int(b)
    if not is_prime(a) or not is_prime(b):
        raise ValueError("a and b must be prime")
    return a,b

def symbolic_certificate(a,b,c):
    a,b=validate_prime_pair(a,b)
    c=Decimal(str(c))
    if c <= 0 or c == 1:
        raise ValueError("c must be >0 and !=1")
    product=a*b
    return {
        "valid": True,
        "a": str(a),
        "b": str(b),
        "ab": str(product),
        "base_c": str(c),
        "x": f"log_{c}({a})",
        "y": f"log_{c}({b})",
        "z": f"log_{c}({product})",
        "identity": f"log_{c}({product}) = log_{c}({a}) + log_{c}({b})",
        "unordered_prime_decode": sorted([a,b]),
        "c_role": "shared-compatibility-codec-base",
        "c_alone_is_payload_code": False
    }

def candidate_base(a,x):
    a=float(a); x=float(x)
    if a <= 0 or x == 0 or not math.isfinite(x):
        raise ValueError("a must be >0 and x finite/nonzero")
    return math.exp(math.log(a)/x)

def numeric_compatibility(a,b,x,y,rel_tol=1e-12,abs_tol=1e-12):
    a,b=validate_prime_pair(a,b)
    c1=candidate_base(a,x)
    c2=candidate_base(b,y)
    ok=math.isclose(c1,c2,rel_tol=rel_tol,abs_tol=abs_tol)
    c=(c1+c2)/2 if ok else None
    z=float(x)+float(y)
    product_check = None if not ok else math.isclose(
        math.exp(math.log(c)*z), a*b, rel_tol=rel_tol, abs_tol=abs_tol
    )
    return {
        "compatible_numeric": ok,
        "candidate_c_from_ax": c1,
        "candidate_c_from_by": c2,
        "shared_c_numeric": c,
        "sum_coordinate": z,
        "product_relation_numeric": product_check,
        "authoritative": False,
        "note": "numeric real-log verification is diagnostic only"
    }

def exact_rational_compatibility(a,b,x_num,x_den,y_num,y_den):
    """Exact test for rational x,y using integer arithmetic.

    x=p/q, y=r/s. A shared base requires a^(q*r)=b^(s*p).
    Distinct primes therefore cannot pass for nonzero rational x,y.
    """
    a,b=validate_prime_pair(a,b)
    p,q,r,s=map(int,(x_num,x_den,y_num,y_den))
    if q==0 or s==0 or p==0 or r==0:
        raise ValueError("rational coordinates must be finite and nonzero")
    if q<0: p,q=-p,-q
    if s<0: r,s=-r,-s
    if p*r <= 0:
        return {"compatible_exact":False,"reason":"x and y must have the same sign"}
    left_exp=q*abs(r)
    right_exp=s*abs(p)
    compatible = pow(a,left_exp) == pow(b,right_exp)
    return {
        "compatible_exact": compatible,
        "equation": f"{a}^{left_exp} = {b}^{right_exp}",
        "authoritative": True
    }
