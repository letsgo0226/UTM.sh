#!/usr/bin/env python3
import math,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify_residents as vr
import principle_vector as pv
import infinite_deployment as idep
class OmegaResidents(unittest.TestCase):
    def test_registry_admitted(self):
        c=vr.verify_registry(); self.assertTrue(c["verified"],c["checks"]); self.assertEqual(c["status"],"OMEGA_ADMITTED"); self.assertEqual(c["resident_count"],9); self.assertFalse(c["actual_infinite_physical_compute"])
    def test_required_modules_present(self):
        ids=set(vr.verify_registry()["resident_ids"])
        for x in ("utm-principle-vector-v0.1","utm-infinite-deployment-continuation-v0.1","utm-log-abelian-native-v1.0","utm-three-universe-axiom-layer-v1.0","utm-omega-unbounded-compute-v1.0"): self.assertIn(x,ids)
    def test_principle_vector_invariant(self):
        s0=pv.PrincipleVectorState(0,0,pv.ComplexNode(1,math.pi/4),pv.ComplexNode(2,-math.pi/4)); s1=pv.chronon_step(s0,1,towel=pv.ComplexNode(1,math.pi/4+pv.TAU)); self.assertTrue(pv.validate_transition(s0,s1))
    def test_infinite_deployment_certificate(self):
        c=idep.next_candidate("0"*64,0,"omega-resident-test","resident-stage","configure",{"mode":"formal-only"}); cert=idep.certify(c); self.assertTrue(cert.verified,cert.reasons); self.assertFalse(cert.actual_infinite_physical_compute)
    def test_stage_extension_remains_finite(self):
        a={"stage":1,"resource_budget":10,"resource_used":1,"valuation":{"0":1},"oracle":None}; b={"stage":2,"resource_budget":10,"resource_used":2,"valuation":{"0":1,"1":1},"oracle":None}; self.assertTrue(vr.extend_stage(a,b)["valid_extension"])
if __name__=="__main__": unittest.main()
