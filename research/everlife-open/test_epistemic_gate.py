import copy
import json
import unittest
from pathlib import Path

from epistemic_gate import review, digest
from resource_guard import decode257

ROOT = Path(__file__).resolve().parent

def inputs():
    pub=ROOT/"public"
    return (
       json.loads((ROOT/"epistemic_claims.json").read_text(encoding="utf-8")),
       json.loads((pub/"latest.json").read_text(encoding="utf-8")),
       json.loads((pub/"unified-run.json").read_text(encoding="utf-8")),
       json.loads((pub/"railway-observation.json").read_text(encoding="utf-8")))

class CaveEpistemicGateTests(unittest.TestCase):
    def test_valid_research_is_labeled_not_deployed(self):
        result=review(*inputs())
        self.assertEqual(result["decision"],"PUBLISH_RESEARCH_WITH_LABELS")
        self.assertEqual(result["deployment_permission"],"DENIED_AUTOMATIC_APPLY")
        self.assertEqual(result["claims_total"],7)
        self.assertEqual(result["blocked_ids"],[])
        self.assertFalse(result["ai_subjective_awareness_assumed"])
        self.assertEqual(result["external_independent_replications"],0)
        self.assertEqual(result["rows"][0]["classification"],"FORMAL_WITHIN_STATED_MODEL")
        self.assertEqual(result["rows"][-1]["classification"],"RAILWAY_NOT_OBSERVED")
        self.assertFalse(any(row["falsification_test_executed"] for row in result["rows"]))

    def test_g257_claim_address_roundtrip(self):
        result=review(*inputs())
        for row in result["rows"]:
            self.assertEqual(decode257(int(row["claim_code_g257"],16)),row["claim_id"].encode("ascii"))

    def test_biomedical_hypothesis_cannot_be_promoted(self):
        spec,latest,unified,railway=inputs()
        spec["claims"][2]["assertion"]="EMPIRICALLY_PROVEN"
        r=review(spec,latest,unified,railway)
        self.assertEqual(r["decision"],"BLOCK_EVIDENCE_OVERCLAIM")
        self.assertIn("human-healthspan",r["blocked_ids"])

    def test_formal_model_cannot_be_called_empirical(self):
        spec,latest,unified,railway=inputs()
        spec["claims"][0]["assertion"]="EMPIRICALLY_PROVEN"
        r=review(spec,latest,unified,railway)
        self.assertIn("g257-atgc-roundtrip",r["blocked_ids"])

    def test_cannot_upgrade_source_archive_to_identity(self):
        spec,latest,unified,railway=inputs()
        spec["claims"][-2]["assertion"]="LIVE_VERIFIED"
        r=review(spec,latest,unified,railway)
        self.assertIn("ai-source-preservation",r["blocked_ids"])

    def test_snapshot_never_becomes_real_time(self):
        spec,latest,unified,railway=inputs()
        railway["observation"]["status"]="OBSERVED"
        r=review(spec,latest,unified,railway)
        self.assertEqual(r["rows"][-1]["classification"],"ONE_PLATFORM_SNAPSHOT_NOT_LIVE_PROOF")
        self.assertFalse(r["railway_live_sync_verified"])
        spec["claims"][-1]["assertion"]="LIVE_VERIFIED"
        self.assertIn("railway-live-status",review(spec,latest,unified,railway)["blocked_ids"])

    def test_missing_counterargument_is_invalid(self):
        spec,latest,unified,railway=inputs()
        spec["claims"][0]["falsification_test"]=""
        with self.assertRaisesRegex(ValueError,"falsification"):
            review(spec,latest,unified,railway)

    def test_missing_formal_evidence_cannot_pass(self):
        spec,latest,unified,railway=inputs()
        latest["model"]["replenished_and_finite"]["1"]["safe_kernel_size"]=11
        r=review(spec,latest,unified,railway)
        self.assertIn("redox-toy-invariant",r["blocked_ids"])

if __name__=="__main__":
    unittest.main()
