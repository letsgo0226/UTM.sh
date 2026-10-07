import unittest
from core import evaluate, selftest

class GuardTests(unittest.TestCase):
    def test_selftest(self):
        self.assertTrue(selftest()["ok"])

    def test_sell_transition(self):
        c={
            "transition":{
                "transition_id":"tm-2-2","tm_n":2,"market":-1,
                "requested_operation":"SELL","from_state":"LONG","target_state":"FLAT",
                "quote":"0","hard_cap":"0","volatility_factor":"1"
            },
            "kernel":{"C":True,"CF":None},
            "risk":{"kill_active":False}
        }
        out=evaluate(c,15)
        self.assertTrue(out["allowed_candidate"])
        self.assertEqual(out["certificate"]["gc"],15)

    def test_bad_state_fails_closed(self):
        c={
            "transition":{
                "transition_id":"tm-3-3","tm_n":3,"market":1,
                "requested_operation":"BUY","from_state":"LONG","target_state":"LONG",
                "quote":"5","hard_cap":"10","volatility_factor":"0.5"
            },
            "kernel":{"C":True,"CF":None},
            "risk":{"kill_active":False}
        }
        out=evaluate(c,15)
        self.assertFalse(out["allowed_candidate"])
        self.assertEqual(out["effective_operation"],"HOLD")

if __name__=="__main__":
    unittest.main()
