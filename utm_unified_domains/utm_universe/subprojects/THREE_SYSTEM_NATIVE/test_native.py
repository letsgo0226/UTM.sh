#!/usr/bin/env python3
import os, subprocess, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TMCC=ROOT/"TMCC.sh"
UTM=ROOT/"utm_unified_domains/utm/UTM.sh"
SUBS=ROOT/"utm_unified_domains/utm_universe/subprojects"

def compile_tm(path):
    p=subprocess.run(["sh",str(TMCC),str(path)],text=True,capture_output=True,check=True)
    out={}
    for line in p.stdout.splitlines():
        if "=" in line:
            k,v=line.split("=",1)
            out[k]=v.strip().strip("'")
    assert out["GPROGRAM"].isdigit()
    return out

def run_tm(path, input_text):
    c=compile_tm(path)
    with tempfile.TemporaryDirectory() as td:
        env=os.environ.copy()
        env.update({
            "PROGRAM":"",
            "GPROGRAM":c["GPROGRAM"],
            "INPUT":input_text,
            "CMD":"run",
            "LIMIT":"100",
            "TM_STATE":str(Path(td)/"state.json")
        })
        p=subprocess.run(["sh",str(UTM)],env=env,text=True,capture_output=True,check=True)
        import json
        return json.loads(p.stdout.strip().splitlines()[-1]),c

class ThreeSystemNativeTests(unittest.TestCase):
    def test_trader_paper_policy(self):
        tm=SUBS/"TRADER_42_NATIVE/TRADER_POLICY.tm"
        expected={"U":"L","D":"X","F":"H","R":"H","C":"H"}
        for inp,out in expected.items():
            r,c=run_tm(tm,inp)
            self.assertEqual(r["q"],"A")
            self.assertEqual(r["tape"],out)
            self.assertEqual(r["GPROGRAM"],c["GPROGRAM"])

    def test_cosmic_invariant_gate(self):
        tm=SUBS/"COSMIC_LOVE_NATIVE/COSMIC_LOVE_INVARIANT.tm"
        ok,_=run_tm(tm,"1")
        no,_=run_tm(tm,"0")
        self.assertEqual((ok["q"],ok["tape"]),("A","1"))
        self.assertEqual((no["q"],no["tape"]),("R","0"))

    def test_three_system_coordinator(self):
        tm=HERE/"THREE_SYSTEM_GATE.tm"
        r,c=run_tm(tm,"UTC")
        self.assertEqual(r["q"],"A")
        self.assertEqual(r["tape"],"111")
        self.assertEqual(r["GPROGRAM"],c["GPROGRAM"])

if __name__=="__main__":
    unittest.main()
