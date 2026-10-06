import unittest

from core import (
    REQUIRED_POLICIES,
    decode_text,
    encode_text,
    equality_residual,
    fleet_verify,
    verify_adapter,
    verify_certificate,
)


class PersistenceEnvelopeTests(unittest.TestCase):
    def test_codec_roundtrip(self):
        s = "UTM persistence envelope"
        self.assertEqual(decode_text(encode_text(s)), s)

    def test_zero_equality_residual(self):
        self.assertEqual(equality_residual({"x": 1}, {"x": 1})["residual"], 0)

    def test_nonzero_equality_residual(self):
        self.assertEqual(equality_residual({"x": 1}, {"x": 2})["residual"], 1)

    def test_single_function_adapter_zero(self):
        r = verify_adapter("utm-single-function", {
            "authoritative_projection": {"g": ["1", "2"]},
            "portable_projection": {"g": ["1", "2"]},
            "finite": True,
            "oracle": False,
            "hypercomputation": False,
        })
        self.assertTrue(r["zero"])

    def test_riemann_adapter_zero(self):
        r = verify_adapter("riemann-proof-utm", {
            "certificate_recomputable": True,
            "riemann_layer_diagnostic_only": True,
            "rh_proof": False,
            "oracle": False,
            "hypercomputation": False,
        })
        self.assertTrue(r["zero"])

    def test_scholar_adapter_detects_bad_stage(self):
        r = verify_adapter("utm-scholar-loop", {
            "expected_stage": "NOTE",
            "observed_stage": "ARGUE",
            "artifact": "x",
        })
        self.assertFalse(r["zero"])

    def test_exact_search_adapter_zero(self):
        r = verify_adapter("dropbox-exact-search", {
            "expected_file_id": "id:1",
            "observed_file_id": "id:1",
            "expected_rev": "r1",
            "observed_rev": "r1",
            "literal_verified": True,
        })
        self.assertTrue(r["zero"])

    def test_fleet_zero(self):
        bundle = {
            "nodes": [
                {
                    "id": "single",
                    "adapter": "utm-single-function",
                    "payload": {
                        "authoritative_projection": {"x": 1},
                        "portable_projection": {"x": 1},
                        "finite": True,
                        "oracle": False,
                        "hypercomputation": False,
                    },
                },
                {
                    "id": "riemann",
                    "adapter": "riemann-proof-utm",
                    "payload": {
                        "certificate_recomputable": True,
                        "riemann_layer_diagnostic_only": True,
                        "rh_proof": False,
                        "oracle": False,
                        "hypercomputation": False,
                    },
                },
            ],
            "edges": [
                {"source": "single", "target": "riemann", "source_state": {"k": 7}, "target_state": {"k": 7}}
            ],
        }
        r = fleet_verify(bundle)
        self.assertTrue(r["zero"])
        payload = dict(r)
        cert = payload.pop("certificate")
        self.assertTrue(verify_certificate(payload, cert["godel"])["verified"])

    def test_fleet_detects_handoff_residual(self):
        bundle = {
            "nodes": [
                {
                    "id": "a",
                    "adapter": "utm-single-function",
                    "payload": {
                        "authoritative_projection": 1,
                        "portable_projection": 1,
                        "finite": True,
                        "oracle": False,
                        "hypercomputation": False,
                    },
                },
                {
                    "id": "b",
                    "adapter": "source-runtime",
                    "payload": {
                        "expected_commit": "abc",
                        "runtime_commit": "abc",
                        "deployment_status": "SUCCESS",
                    },
                },
            ],
            "edges": [{"source": "a", "target": "b", "source_state": 1, "target_state": 2}],
        }
        self.assertEqual(fleet_verify(bundle)["residual"], 1)

    def test_policy_names_are_nonempty(self):
        self.assertGreater(len(REQUIRED_POLICIES), 0)


if __name__ == "__main__":
    unittest.main()
