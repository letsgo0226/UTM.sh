#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import immortality_continuity as m

class HouseholdContinuityTests(unittest.TestCase):
    def test_all_household_subjects_supported(self):
        self.assertEqual(set(m.SUBJECTS),{"human","companion_feline","companion_canine","other_companion_animal","ai_system"})
    def test_biological_candidate_stays_formal(self):
        c=m.generate_candidate("cat-1","companion_feline","test a welfare-preserving longevity hypothesis")
        v=m.verify_candidate(c)
        self.assertTrue(v["verified"])
        self.assertEqual(v["status"],"FORMAL_CANDIDATE")
        self.assertFalse(v["real_world_validated"])
        self.assertFalse(v["biological_immortality_established"])
    def test_ai_continuity_does_not_claim_consciousness(self):
        c=m.generate_candidate("ai-1","ai_system","test portable state and lineage continuity",{
            "state_integrity":True,"memory_integrity":True,"lineage":True,
            "regression":True,"migration_recovery":True,"rollback":True})
        v=m.verify_candidate(c)
        self.assertEqual(v["status"],"EVIDENCE_GATE_COMPLETE")
        self.assertFalse(v["ai_consciousness_established"])
        self.assertFalse(v["ai_personal_identity_established"])
        self.assertFalse(v["real_world_validated"])
    def test_best_verified_is_not_treatment_ranking(self):
        a=m.generate_candidate("a","human","formal hypothesis",{"mechanism":True},stage=1)
        b=m.generate_candidate("b","human","formal hypothesis",{"mechanism":True,"safety":True},stage=2)
        r=m.best_verified_so_far([a,b])
        self.assertEqual(r["candidate"]["candidate_id"],"b")
        self.assertIn("not comparative efficacy",r["ranking_semantics"])
        self.assertFalse(r["real_world_validated"])
    def test_intervention_candidate_rejected(self):
        c=m.ContinuityCandidate("x","human","unsafe boundary test",{},generates_real_world_intervention=True)
        self.assertFalse(m.verify_candidate(c)["verified"])

if __name__=="__main__": unittest.main()
