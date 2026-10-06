import copy
import hashlib
import http.client
import json
import threading
import unittest
import core
from server import BoundedServer, H


def claims():
    return {"g_re": "0", "g_im": "0", "continuation_residual": "0",
            "risk_residual": "0", "certificate_residual": "0"}


def risk_witness():
    return {"state_before": {"cash": "100", "base": "0"},
            "action": {"side": "BUY", "quantity": "2", "price": "10", "fee": "1"},
            "state_after": {"cash": "79", "base": "2"}}


def witnessed():
    return {**claims(), "analytic_witness": {"kind": "polynomial",
            "source_coefficients": ["-1", "1"], "candidate_coefficients": ["-1", "1"],
            "z_re": "1", "z_im": "0", "target_domain": "C"}, "risk_witness": risk_witness()}


class T(unittest.TestCase):
    def test_empty_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing required"):
            core.evaluate({})

    def test_each_missing_field_is_rejected(self):
        for key in core.REQUIRED:
            d = claims(); del d[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                core.evaluate(d)

    def test_unsupported_root_payloads(self):
        for value in (None, [], 0, "0", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                core.evaluate(value)

    def test_claims_are_uncertified(self):
        r = core.evaluate(claims())
        self.assertEqual(r["decision"], "UNDETERMINED")
        self.assertFalse(r["admissible_candidate"])
        self.assertIsNone(r["continuation_zero"])
        self.assertFalse(r["certificate_zero"])

    def test_exact_zero_with_independent_witnesses(self):
        r = core.evaluate(witnessed())
        self.assertEqual(r["decision"], "CERTIFIED_MODEL_CANDIDATE")
        self.assertTrue(r["witnesses_verified"])
        self.assertTrue(r["admissible_candidate"])
        self.assertFalse(r["real_world_trade_authorized"])
        self.assertFalse(r["order_execution"])
        self.assertFalse(r["real_world_profit_guaranteed"])

    def test_submitted_risk_residual_blocks(self):
        d = witnessed(); d["risk_residual"] = "1"
        self.assertEqual(core.evaluate(d)["decision"], "HOLD")

    def test_nonzero_control(self):
        d = claims(); d["g_re"] = "1"
        self.assertEqual(core.evaluate(d)["decision"], "HOLD")

    def test_polynomial_mismatch_blocks(self):
        d = witnessed(); d["analytic_witness"]["candidate_coefficients"] = ["-2", "1"]
        self.assertFalse(core.evaluate(d)["admissible_candidate"])

    def test_false_claim_of_root_blocks(self):
        d = witnessed(); d["analytic_witness"]["z_re"] = "2"
        self.assertFalse(core.evaluate(d)["continuation_zero"])

    def test_polynomial_domain_blocks(self):
        d = witnessed(); d["analytic_witness"]["target_domain"] = "restricted"
        self.assertFalse(core.evaluate(d)["admissible_candidate"])

    def test_complex_root(self):
        d = witnessed(); w = d["analytic_witness"]
        w.update(source_coefficients=["1", "0", "1"], candidate_coefficients=["1", "0", "1"], z_re="0", z_im="1")
        self.assertTrue(core.evaluate(d)["admissible_candidate"])

    def test_equal_polynomial_with_trailing_zero(self):
        d = witnessed(); d["analytic_witness"]["candidate_coefficients"].append("0")
        self.assertTrue(core.evaluate(d)["admissible_candidate"])

    def test_unsupported_analytic_class_is_unknown(self):
        d = witnessed(); d["analytic_witness"]["kind"] = "general_maximal_continuation"
        self.assertEqual(core.evaluate(d)["decision"], "UNDETERMINED")

    def test_missing_risk_witness_is_unknown(self):
        d = witnessed(); del d["risk_witness"]
        self.assertEqual(core.evaluate(d)["decision"], "UNDETERMINED")

    def test_overdraft_blocks(self):
        d = witnessed(); d["risk_witness"]["action"]["quantity"] = "20"
        d["risk_witness"]["state_after"] = {"cash": "-101", "base": "20"}
        self.assertFalse(core.evaluate(d)["admissible_candidate"])

    def test_tampered_state_after_blocks(self):
        d = witnessed(); d["risk_witness"]["state_after"]["cash"] = "1000"
        self.assertFalse(core.evaluate(d)["admissible_candidate"])

    def test_overselling_blocks(self):
        w = risk_witness(); w["action"]["side"] = "SELL"
        w["state_after"] = {"cash": "119", "base": "-2"}
        self.assertFalse(core.risk_check(w)["verified"])

    def test_tiny_nonzero_is_not_displayed_as_one(self):
        d = claims(); d["g_re"] = "1e-12"
        r = core.evaluate(d)
        self.assertLess(r["formal_probability"], 1)
        self.assertFalse(r["formal_probability_one"])
        self.assertFalse(r["admissible_candidate"])

    def test_malformed_and_extreme_numbers_rejected(self):
        for value in ("1e400", "1e999999999999", "1/0", "nan", "inf", "x", True, [], {}, "9" * 81):
            with self.subTest(value=value), self.assertRaises(ValueError):
                core.q(value)

    def test_negative_residual_rejected(self):
        d = claims(); d["certificate_residual"] = "-1"
        with self.assertRaises(ValueError): core.evaluate(d)

    def test_false_strings_rejected(self):
        with self.assertRaisesRegex(ValueError, "JSON booleans"):
            core.transition({k: "false" for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")})

    def test_transition_numeric_flags_rejected(self):
        with self.assertRaises(ValueError):
            core.transition({k: 1 for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")})

    def test_true_flags_without_evidence_are_uncertified(self):
        r = core.transition({k: True for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")})
        self.assertFalse(r["invariant_after_certified"])
        self.assertEqual(r["decision"], "UNDETERMINED")

    def test_false_flags_hold(self):
        r = core.transition({k: False for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")})
        self.assertFalse(r["invariant_after_certified"])

    def test_transition_verified_from_state(self):
        d = {k: True for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")}
        d["risk_witness"] = risk_witness()
        self.assertTrue(core.transition(d)["invariant_after_certified"])
        d["risk_witness"]["state_after"]["cash"] = "999"
        self.assertFalse(core.transition(d)["invariant_after_certified"])

    def test_receipt_records_inputs_and_hash(self):
        d = witnessed(); r = core.evaluate(d); c = r["certificate"]
        self.assertEqual(c["receipt"]["inputs"], d)
        self.assertEqual(hashlib.sha256(core.canonical(c["receipt"]).encode()).hexdigest(), c["sha256"])
        self.assertFalse(c["authenticated"])
        self.assertFalse(c["mathematical_proof_by_encoding"])
        tampered = copy.deepcopy(c["receipt"])
        tampered["inputs"]["risk_witness"]["action"]["quantity"] = "3"
        self.assertNotEqual(hashlib.sha256(core.canonical(tampered).encode()).hexdigest(), c["sha256"])

    def test_codec_roundtrip_and_limits(self):
        for x in ({"Trader_42": "zero", "n": 42}, {"繁體中文": "測試"}, None):
            self.assertTrue(core.encode_payload(x)["roundtrip"])
        with self.assertRaises(ValueError): core.encode_payload("a" * 1025)
        with self.assertRaises(ValueError): core.decode_text(True)
        with self.assertRaises(ValueError): core.decode_text(257)

    def test_deep_input_rejected(self):
        value = {}
        for _ in range(18): value = {"x": value}
        with self.assertRaises(ValueError): core.canonical(value)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = BoundedServer(("127.0.0.1", 0), H)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def request(self, path, payload, raw=False):
        body = payload if raw else json.dumps(payload)
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        connection.request("POST", path, body, {"Content-Type": "application/json"})
        response = connection.getresponse(); status = response.status; data = json.loads(response.read())
        connection.close()
        return status, data

    def test_rejected_payloads_return_400(self):
        for data in ({}, [], None, {**claims(), "g_re": "1e400"}):
            with self.subTest(data=data):
                status, result = self.request("/evaluate", data)
                self.assertEqual(status, 400)
                self.assertEqual(result["decision"], "REJECTED_INPUT")

    def test_flags_return_400(self):
        d = {k: "false" for k in ("invariant_before", "guard_passed", "transition_preserves_invariant")}
        self.assertEqual(self.request("/transition", d)[0], 400)

    def test_valid_witness_and_claims(self):
        self.assertEqual(self.request("/evaluate", witnessed())[1]["decision"], "CERTIFIED_MODEL_CANDIDATE")
        self.assertEqual(self.request("/evaluate", claims())[1]["decision"], "UNDETERMINED")

    def test_duplicate_keys_and_nonfinite_json(self):
        for body in ('{"g_re":0,"g_re":1}', '{"g_re":NaN}', '{"g_re":Infinity}'):
            self.assertEqual(self.request("/evaluate", body, raw=True)[0], 400)

    def test_oversized_body(self):
        self.assertEqual(self.request("/encode", {"payload": "a" * 17000})[0], 400)

    def test_explicit_encode_payload_required(self):
        self.assertEqual(self.request("/encode", {})[0], 400)
        self.assertEqual(self.request("/encode", {"payload": None})[0], 200)

    def test_health_version(self):
        c = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        c.request("GET", "/health"); r = c.getresponse()
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.read())["protocol"], core.PROTOCOL)
        c.close()


if __name__ == "__main__":
    unittest.main()
