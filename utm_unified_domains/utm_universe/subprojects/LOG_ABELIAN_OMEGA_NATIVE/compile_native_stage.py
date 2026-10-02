#!/usr/bin/env python3
"""Compile a finite Log-Abelian valuation stage into pure-UTM scalar jobs.

The compiler is a host-side packager only. Each nonzero coordinate addition is
executed by the same single-tape TM program in VALUATION_ADD.tm.
"""
import argparse, functools, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TM = HERE / "VALUATION_ADD.tm"
MAX_SUPPORT = 256
MAX_MULTIPLICITY = 100000

def parse_valuation(text):
    raw = json.loads(text)
    if not isinstance(raw, dict) or len(raw) > MAX_SUPPORT:
        raise ValueError(f"valuation must be an object with at most {MAX_SUPPORT} entries")
    out = {}
    for k, v in raw.items():
        i, m = int(k), int(v)
        if i < 0 or m < 0 or m > MAX_MULTIPLICITY:
            raise ValueError("indices and multiplicities must be nonnegative and bounded")
        if m:
            out[i] = m
    return out

def program_text():
    rules = []
    for line in TM.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        left, right = line.split("->",1)
        q, read = left.split()
        q2, write, direction = right.split()
        rules.append(",".join((q,read,q2,write,direction)))
    return ";".join(rules)

def gencode(s):
    return functools.reduce(lambda a,b:a*257+b+1, s.encode(), 1)

def compile_bundle(left, right, stage=0):
    keys = sorted(set(left) | set(right))
    program = program_text()
    jobs = []
    for i in keys:
        m, n = left.get(i,0), right.get(i,0)
        jobs.append({
            "coordinate": i,
            "left": m,
            "right": n,
            "input": "1"*m + "#" + "1"*n,
            "expected_unary_length": m+n,
            "program": program,
            "GPROGRAM": str(gencode(program))
        })
    return {
        "protocol":"UTM-Native-Log-Omega-Stage/1.0",
        "stage":int(stage),
        "finite":True,
        "pure_utm_core":True,
        "host_compiler_role":"finite job packaging only",
        "operation":"componentwise valuation addition",
        "algebra":"(v+w)_i=v_i+w_i",
        "jobs":jobs,
        "actual_infinite_physical_compute":False
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--left",required=True,help='JSON object, e.g. {"0":2,"3":1}')
    ap.add_argument("--right",required=True)
    ap.add_argument("--stage",type=int,default=0)
    ns=ap.parse_args()
    print(json.dumps(compile_bundle(parse_valuation(ns.left),parse_valuation(ns.right),ns.stage),
                     separators=(",",":")))

if __name__=="__main__":
    main()
