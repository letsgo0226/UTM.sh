import copy
import json
import unittest
from pathlib import Path
from nutrition_study import review

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "nutrition_cognition_odor_study.json").read_text(encoding="utf-8"))

class NutritionStudyTests(unittest.TestCase):
    def test_protocol_is_research_only_without_human_data(self):
        result = review(SPEC)
        self.assertEqual(result["status"], "RESEARCH_PROTOCOL_VALIDATED_METADATA_ONLY")
        self.assertFalse(result["human_data_collected"])
        self.assertFalse(result["medical_conclusions"])
        self.assertFalse(result["external_apply"])
        self.assertEqual(result["spiritual_vibration_mechanism"],
                         "NOT_OPERATIONALIZED_OR_EMPIRICALLY_ESTABLISHED")
        self.assertTrue(result["requires_human_review"])

    def test_no_private_health_observations_in_public_protocol(self):
        altered = copy.deepcopy(SPEC)
        altered["participant_name"] = "any-identifying-string"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            review(altered)
        altered = copy.deepcopy(SPEC)
        altered["candidate_outcomes"][0]["value"] = 7
        with self.assertRaisesRegex(ValueError, "observation"):
            review(altered)

    def test_rejects_automatic_medical_or_dose_recommendation(self):
        for forbidden in ("clinical_diagnosis_enabled", "automated_nutrition_or_supplement_dosing",
                          "high_dose_supplements_recommended", "external_apply_enabled",
                          "human_data_collection_enabled"):
            altered = copy.deepcopy(SPEC)
            altered[forbidden] = True
            with self.subTest(forbidden=forbidden), self.assertRaisesRegex(ValueError, "unsafe"):
                review(altered)

    def test_cannot_promote_unmeasured_claims(self):
        altered = copy.deepcopy(SPEC)
        altered["hypotheses"][0]["status"] = "EMPIRICALLY_PROVEN"
        with self.assertRaisesRegex(ValueError, "mislabeled"):
            review(altered)

        altered = copy.deepcopy(SPEC)
        altered["symbolic_interpretation"]["status"] = "VALIDATED_BRAIN_FREQUENCY"
        with self.assertRaisesRegex(ValueError, "overclaimed"):
            review(altered)

    def test_requires_confounders_consent_and_separate_odor_endpoints(self):
        altered = copy.deepcopy(SPEC)
        altered["consent_required_before_human_data_collection"] = False
        with self.assertRaisesRegex(ValueError, "consent"):
            review(altered)
        altered = copy.deepcopy(SPEC)
        altered["candidate_outcomes"] = [v for v in altered["candidate_outcomes"] if v["id"] != "breath_odor"]
        with self.assertRaisesRegex(ValueError, "independent"):
            review(altered)

if __name__ == "__main__":
    unittest.main()
