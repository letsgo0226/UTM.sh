#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify_applications as v

class LifeApplications(unittest.TestCase):
    def test_bundle_is_formally_admitted(self):
        c=v.verify_bundle()
        self.assertTrue(c["verified"],c["results"])
        self.assertEqual(c["status"],"OMEGA_ADMITTED")
        self.assertEqual(c["application_count"],5)
        self.assertIsNone(c["P_empirical_hat"])
        self.assertFalse(c["real_world_validated"])
        self.assertFalse(c["actual_infinite_physical_compute"])
    def test_all_targets_preserve_empirical_boundary(self):
        for a in v.load_all():
            self.assertEqual(a["P_target_goal"],1)
            self.assertEqual(a["C_target"],1)
            self.assertIsNone(a["P_empirical_hat"])
            self.assertFalse(a["empirical_claim"])
            self.assertFalse(a["real_world_validated"])
            self.assertTrue(a["external_evidence_required"])
            self.assertFalse(a["execution_boundary"]["generates_real_world_intervention"])
            self.assertFalse(a["execution_boundary"]["authorizes_clinical_use"])
            self.assertFalse(a["execution_boundary"]["medical_action_enabled"])
    def test_household_immortality_scope(self):
        a={x["app_id"]:x for x in v.load_all()}["IMMORTALITY_RESEARCH"]
        ids={x["id"] for x in a["subject_scope"]["classes"]}
        self.assertEqual(ids,{"human","companion_feline","companion_canine","other_companion_animal","ai_system"})
        self.assertFalse(a["execution_boundary"]["ai_consciousness_claim_enabled"])
        self.assertFalse(a["execution_boundary"]["ai_personhood_claim_enabled"])
        self.assertFalse(a["execution_boundary"]["biological_immortality_claim_enabled"])
    def test_absolute_targets_are_not_real_world_guarantees(self):
        by_id={a["app_id"]:a for a in v.load_all()}
        self.assertIn("NOT_ESTABLISHED",by_id["IMMORTALITY_RESEARCH"]["target_semantics"]["real_world_claim"])
        self.assertIn("NOT_ESTABLISHED",by_id["CONTRACEPTION_ZERO_HARM"]["target_semantics"]["real_world_claim"])
        self.assertIn("NOT_ESTABLISHED",by_id["BIRTH_ZERO_INJURY"]["target_semantics"]["real_world_claim"])

if __name__=="__main__":
    unittest.main()
