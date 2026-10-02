#!/usr/bin/env python3
"""Execute a compiled finite-stage bundle through the repository UTM.sh."""
import argparse, json, os, subprocess, tempfile
from pathlib import Path
from compile_native_stage import compile_bundle, parse_valuation

HERE=Path(__file__).resolve().parent
UTM=(HERE / "../../../utm/UTM.sh").resolve()

def run_bundle(bundle):
    results=[]
    for job in bundle["jobs"]:
        with tempfile.TemporaryDirectory() as td:
            env=os.environ.copy()
            env.update({
                "GPROGRAM":job["GPROGRAM"],
                "PROGRAM":"",
                "INPUT":job["input"],
                "CMD":"run",
                "LIMIT":"100000",
                "TM_STATE":str(Path(td)/"state.json")
            })
            p=subprocess.run(["sh",str(UTM)],env=env,text=True,capture_output=True,check=True)
            result=json.loads(p.stdout.strip().splitlines()[-1])
            expected="1"*job["expected_unary_length"]
            if not expected:
                expected="_"
            results.append({
                "coordinate":job["coordinate"],
                "result":result,
                "expected_tape":expected,
                "verified":result["halt"] is True and result["tape"]==expected
            })
    return {
        "protocol":bundle["protocol"],
        "stage":bundle["stage"],
        "all_verified":all(r["verified"] for r in results),
        "jobs":results,
        "execution_core":"utm_unified_domains/utm/UTM.sh",
        "physical_host_required":True
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--left",required=True)
    ap.add_argument("--right",required=True)
    ap.add_argument("--stage",type=int,default=0)
    ns=ap.parse_args()
    bundle=compile_bundle(parse_valuation(ns.left),parse_valuation(ns.right),ns.stage)
    print(json.dumps(run_bundle(bundle),separators=(",",":")))

if __name__=="__main__":
    main()
