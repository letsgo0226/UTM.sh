from __future__ import annotations
import hashlib,json,math,sys
from fractions import Fraction
from typing import Any
if hasattr(sys,"set_int_max_str_digits"): sys.set_int_max_str_digits(0)
PROTOCOL="Trader42-Log-Analytic-Zero/1.0"
def canonical(x:Any)->str:return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def encode_text(s:str)->int:
    n=1
    for b in s.encode():n=n*257+b+1
    return n
def decode_text(n:int)->str:
    if not isinstance(n,int) or n<1:raise ValueError("positive integer required")
    a=[]
    while n>1:
        n,r=divmod(n,257)
        if not 1<=r<=256:raise ValueError("invalid code")
        a.append(r-1)
    return bytes(reversed(a)).decode()
def cert(x:Any)->dict[str,Any]:
    s=canonical(x);g=encode_text(s)
    return {"godel":str(g),"roundtrip":decode_text(g)==s,"sha256":hashlib.sha256(s.encode()).hexdigest(),"sha256_identity":False}
def q(v:Any)->Fraction:
    try:return Fraction(str(v))
    except Exception as e:raise ValueError("exact rational value required") from e
def evaluate(d:dict[str,Any])->dict[str,Any]:
    gr,gi=q(d.get("g_re",0)),q(d.get("g_im",0));y=gr*gr+gi*gi
    rs={k:q(d.get(k,0)) for k in ("continuation_residual","risk_residual","certificate_residual")}
    if y<0 or any(v<0 for v in rs.values()):raise ValueError("residuals must be nonnegative")
    zero=y==0;safe=all(v==0 for v in rs.values());admissible=zero and safe
    out={"protocol":PROTOCOL,"g":{"re":str(gr),"im":str(gi)},"y_abs_g_sq":str(y),
         "formal_probability":1.0 if zero else math.exp(-float(y)),
         "formal_probability_one":zero,"continuation_zero":rs["continuation_residual"]==0,
         "risk_zero":rs["risk_residual"]==0,"certificate_zero":rs["certificate_residual"]==0,
         "admissible_candidate":admissible,"decision":"CERTIFIED_CANDIDATE" if admissible else "HOLD",
         "order_execution":False,"real_world_profit_guaranteed":False,
         "meaning":"p_formal=exp(-|G|^2); p_formal=1 iff G=0. This is a formal acceptance condition, not a market guarantee."}
    out["certificate"]=cert(out);return out
def transition(d:dict[str,Any])->dict[str,Any]:
    init=bool(d.get("invariant_before"));guard=bool(d.get("guard_passed"));pres=bool(d.get("transition_preserves_invariant"))
    after=init and guard and pres
    out={"protocol":PROTOCOL,"invariant_before":init,"guard_passed":guard,"transition_preserves_invariant":pres,
         "invariant_after_certified":after,"profit_guaranteed":False}
    out["certificate"]=cert(out);return out
def encode_payload(x:Any)->dict[str,Any]:
    s=canonical(x);g=encode_text(s)
    return {"protocol":PROTOCOL,"operation":"godel-encode","godel":str(g),"roundtrip":decode_text(g)==s,"certificate":cert(x)}
def manifest()->dict[str,Any]:
    return {"protocol":PROTOCOL,"equations":["p_formal=exp(-|G|^2)","G=0 <=> p_formal=1",
      "P_total=max(P_AC,P_risk,P_cert,|G|^2)"],"endpoints":["/health","/manifest","/evaluate","/transition","/encode"],
      "boundaries":{"verification_only":True,"places_orders":False,"real_world_profit_guarantee":False,
      "probability_one_is_formal":True,"unsupported_general_maximal_continuation_is_not_inferred":True}}
