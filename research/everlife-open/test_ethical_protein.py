import copy
import json
import unittest
from pathlib import Path
from ethical_protein import review

SPEC=json.loads((Path(__file__).resolve().parent/"ethical_protein_transition.json").read_text(encoding="utf-8"))
class EthicalProteinTests(unittest.TestCase):
    def test_three_tracks_are_research_only(self):
        r=review(SPEC)
        self.assertEqual(len(r["tracks"]),3)
        self.assertFalse(r["zero_suffering_established"])
        self.assertFalse(r["research_findings_empirically_verified"])
        self.assertEqual(r["individual_health_records"],0)
        self.assertFalse(r["external_apply"])

    def test_cannot_claim_zero_harm(self):
        d=copy.deepcopy(SPEC)
        d["automatically_claims_zero_harm"]=True
        with self.assertRaisesRegex(ValueError,"unsafe"):
            review(d)

    def test_fbs_and_donor_require_audit(self):
        for field in ("fetal-bovine-serum", "donor-animal","sentience"):
            d=copy.deepcopy(SPEC)
            d["ethical_audit_criteria"]=[x for x in d["ethical_audit_criteria"] if x["id"]!=field]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"ethical audit"):
                review(d)

    def test_no_unauthorized_interventions(self):
        for field in ("human_participant_intervention_enabled","live_animal_experiments_enabled",
                      "individualized_diet_or_supplement_dosing_enabled", "health_data_collection_enabled",
                      "deployment_enabled"):
            d=copy.deepcopy(SPEC);d[field]=True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"unsafe"):
                review(d)

    def test_no_empirical_overclaim(self):
        d=copy.deepcopy(SPEC)
        d["empirical_hypotheses"][0]["assertion"]="PROVEN"
        with self.assertRaisesRegex(ValueError,"unverified"):
            review(d)

if __name__ == "__main__":
    unittest.main()
