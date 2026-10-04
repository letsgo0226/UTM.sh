#!/usr/bin/env python3
import math,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify_residents as vr
import principle_vector as pv
import infinite_deployment as idep
import full_sync as fs
class OmegaResidents(unittest.TestCase):
    def test_registry_admitted(self):
        c=vr.verify_registry(); self.assertTrue(c["verified"],c["checks"]); self.assertEqual(c["status"],"OMEGA_ADMITTED"); self.assertEqual(c["resident_count"],20); self.assertFalse(c["actual_infinite_physical_compute"])
    def test_required_modules_present(self):
        ids=set(vr.verify_registry()["resident_ids"])
        for x in ("utm-principle-vector-v0.1","utm-infinite-deployment-continuation-v0.1","utm-log-abelian-native-v1.0","utm-three-universe-axiom-layer-v1.0","utm-omega-unbounded-compute-v1.0","utm-app-immortality-research-v1.0","utm-app-cultured-meat-v1.0","utm-app-vegetarian-nutrition-v1.0","utm-app-contraception-zero-harm-v1.0","utm-app-birth-zero-injury-v1.0","utm-omega-resident-admission-v1.0","utm-omega-full-sync-v1.0","utm-federated-compute-fabric-v1.0","utm-field-node-bootstrap-v1.0","utm-field-seed-v1.0","utm-seed-one-liner-v1.0"): self.assertIn(x,ids)
    def test_principle_vector_invariant(self):
        s0=pv.PrincipleVectorState(0,0,pv.ComplexNode(1,math.pi/4),pv.ComplexNode(2,-math.pi/4)); s1=pv.chronon_step(s0,1,towel=pv.ComplexNode(1,math.pi/4+pv.TAU)); self.assertTrue(pv.validate_transition(s0,s1))
    def test_infinite_deployment_certificate(self):
        c=idep.next_candidate("0"*64,0,"omega-resident-test","resident-stage","configure",{"mode":"formal-only"}); cert=idep.certify(c); self.assertTrue(cert.verified,cert.reasons); self.assertFalse(cert.actual_infinite_physical_compute)
    def test_admission_one_liner_under_2kb(self):
        p=HERE.parents[1]/"protocols"/"UTM-OMEGA-RESIDENT-ADMISSION-1.0.one-liner.sh"; m=HERE.parents[1]/"protocols"/"UTM-OMEGA-RESIDENT-ADMISSION-1.0.json"; self.assertLess(len(p.read_bytes()),2048); self.assertEqual(__import__("json").loads(m.read_text())["one_liner_bytes_utf8"],len(p.read_bytes())); self.assertIn("/resident/admit",p.read_text()); self.assertIn("/resident/resume",p.read_text())
    def test_admission_bound_to_independent_runtime(self):
        import json
        m=json.loads((HERE.parents[1]/"protocols"/"UTM-OMEGA-RESIDENT-ADMISSION-1.0.json").read_text()); b=m["deployment_binding"]; self.assertEqual(b["canonical_runtime_endpoint"],"https://utm-universe-production.up.railway.app"); self.assertEqual(b["railway_deployment_status"],"SUCCESS"); self.assertEqual(b["github_live_smoke_status"],"SUCCESS"); self.assertTrue(b["discovery_remains_dynamic"]); self.assertFalse(b["hardcoded_runtime_in_one_liner"])
    def test_field_node_one_liner_under_2kb(self):
        import json
        p=HERE.parents[1]/"protocols"/"UTM-FIELD-NODE-BOOTSTRAP-1.0.one-liner.sh"; m=json.loads((HERE.parents[1]/"protocols"/"UTM-FIELD-NODE-BOOTSTRAP-1.0.json").read_text()); self.assertLess(len(p.read_bytes()),2048); self.assertEqual(m["one_liner_utf8_bytes"],len(p.read_bytes())-1); s=p.read_text(); self.assertIn("server.py",s); self.assertIn("compute_fabric.py",s); self.assertIn("FEDERATION_PEERS",s); self.assertNotIn("FEDERATION_TOKEN\",\"n",s)
    def test_field_seed_trust_boundary(self):
        import json
        m=json.loads((HERE.parents[1]/"protocols"/"UTM-FIELD-SEED-1.0.json").read_text()); self.assertTrue(m["trust_model"]["public_standalone_generation"]); self.assertTrue(m["trust_model"]["private_federation_membership"]); self.assertFalse(m["trust_model"]["federation_secret_committed"]); self.assertFalse(m["propagation_semantics"]["autonomous_physical_resource_creation"])
    def test_utm_seed_one_liner(self):
        import json
        p=HERE.parents[1]/"protocols"/"UTM-SEED-ONE-LINER-1.0.one-liner.sh"; m=json.loads((HERE.parents[1]/"protocols"/"UTM-SEED-ONE-LINER-1.0.json").read_text()); b=p.read_bytes(); self.assertLess(len(b),2048); self.assertEqual(m["one_liner_utf8_bytes"],len(b)-1); self.assertEqual(m["machine"]["default_result"],"FIELD"); self.assertEqual(m["machine"]["default_transition_count"],5); self.assertFalse(m["boundaries"]["actual_infinite_physical_compute"]); self.assertIsNone(m["boundaries"]["oracle"]); self.assertFalse(m["node_generation"]["federation_secret_embedded"])
    def test_full_sync_bundle_covers_previous_residents(self):
        import json,re
        p=HERE.parents[1]/"protocols"/"UTM-OMEGA-FULL-SYNC-1.0.json"; x=json.loads(p.read_text()); c=vr.verify_registry(); ids=set(c["resident_ids"])-{"utm-omega-full-sync-v1.0"}; self.assertEqual({z["id"] for z in x["components"]},ids); self.assertEqual(x["component_count"],19); self.assertTrue(re.fullmatch(r"[0-9a-f]{40}",x["sync_source_commit"])); self.assertTrue(x["execution_target"]["every_executed_stage_is_finite"]); self.assertFalse(x["execution_target"]["actual_infinite_physical_compute"])
    def test_full_sync_is_fixed_point(self):
        x=fs.evaluate(); self.assertTrue(x["verified"],x["reasons"]); self.assertEqual(x["status"],"OMEGA_FULL_SYNC_FIXED_POINT"); self.assertEqual(x["stage"],11); self.assertEqual(x["aggregate_coordinate"],15); self.assertFalse(x["allocate_new_resident"]); self.assertFalse(x["advance_stage"])
    def test_full_sync_detects_content_change(self):
        import json
        r=vr.load_registry(); m=json.loads((HERE.parents[1]/"protocols"/"UTM-OMEGA-FULL-SYNC-1.0.json").read_text()); m["components"][0]["source_blob_sha"]="0"*40; x=fs.evaluate(r,m); self.assertFalse(x["verified"]); self.assertEqual(x["status"],"OMEGA_FULL_SYNC_ADVANCE_REQUIRED"); self.assertTrue(x["advance_stage"]); self.assertEqual(x["next_stage_if_changed"],12); self.assertFalse(x["allocate_new_resident"])
    def test_stage_extension_remains_finite(self):
        a={"stage":1,"resource_budget":10,"resource_used":1,"valuation":{"0":1},"oracle":None}; b={"stage":2,"resource_budget":10,"resource_used":2,"valuation":{"0":1,"1":1},"oracle":None}; self.assertTrue(vr.extend_stage(a,b)["valid_extension"])
if __name__=="__main__": unittest.main()
