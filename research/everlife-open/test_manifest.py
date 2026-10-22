import copy
import hashlib
import json
import unittest
from unittest.mock import patch
from make_manifest import create, verify

class MachineManifestTests(unittest.TestCase):
    def test_local_sha256_manifest(self):
        manifest = create({"GITHUB_SHA":"a"*40,"GITHUB_RUN_ID":"123"})
        self.assertTrue(verify(manifest))
        self.assertEqual(len(manifest["artifacts"]),4)
        self.assertEqual(manifest["observer"]["deployment_changes"],0)
        self.assertFalse(manifest["machine"]["physical_infinity_claim"])
        self.assertEqual(manifest["provenance"]["github_event_revision"],"a"*40)

    def test_reject_tampered_artifact_digest(self):
        manifest = create()
        tampered = copy.deepcopy(manifest)
        tampered["artifacts"]["control-plane.json"]["sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError,"digest mismatch"):
            verify(tampered)

    def test_unverified_provenance_does_not_invent_sha(self):
        manifest = create({"GITHUB_SHA":"not-a-real-sha","GITHUB_RUN_ID":"nonsense"})
        self.assertIsNone(manifest["provenance"]["github_event_revision"])
        self.assertIsNone(manifest["provenance"]["github_run_id"])

    def test_scope_is_always_readonly(self):
        manifest=create()
        self.assertEqual(manifest["control_boundary"],"read-only; UTM/trading services unchanged")
        self.assertEqual(manifest["evidence"]["biomedical"],"NOT_VALIDATED")

if __name__=="__main__":
    unittest.main()
