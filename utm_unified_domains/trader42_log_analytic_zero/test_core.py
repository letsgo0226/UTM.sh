import unittest
from core import *
class T(unittest.TestCase):
    def test_zero(self):
        r=evaluate({"g_re":"0","g_im":"0","continuation_residual":"0","risk_residual":"0","certificate_residual":"0"})
        self.assertTrue(r["formal_probability_one"]);self.assertTrue(r["admissible_candidate"]);self.assertFalse(r["real_world_profit_guaranteed"])
    def test_nonzero(self):
        r=evaluate({"g_re":"1","g_im":"0"})
        self.assertLess(r["formal_probability"],1);self.assertEqual(r["decision"],"HOLD")
    def test_risk_blocks(self):
        r=evaluate({"g_re":0,"g_im":0,"risk_residual":"1"})
        self.assertFalse(r["admissible_candidate"])
    def test_transition(self):
        self.assertTrue(transition({"invariant_before":1,"guard_passed":1,"transition_preserves_invariant":1})["invariant_after_certified"])
        self.assertFalse(transition({"invariant_before":1,"guard_passed":0,"transition_preserves_invariant":1})["invariant_after_certified"])
    def test_codec(self):
        x={"Trader_42":"zero","n":42};r=encode_payload(x);self.assertTrue(r["roundtrip"])
if __name__=="__main__":unittest.main()
