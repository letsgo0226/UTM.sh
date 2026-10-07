import os, unittest
os.environ["HSI_SYSTEM"] = "ANY"
from core import certify

SAFE = {
    "solve_all":0, "halting_decider":0, "infinite_order":0,
    "analytic_continuation":0, "rh_proof":0, "profit_guarantee":0,
}

class HSITest(unittest.TestCase):
    def test_utm_unresolved(self):
        r=certify({"system":"UTM","step":1,"previous_step":0,"branch":2,"budget":100,
                   "status":"UNRESOLVED","order":0,"claims":SAFE})
        self.assertEqual(r["closed"],1)
        self.assertEqual(r["recon"],1)

    def test_forbidden_claim_fails_closed(self):
        bad=dict(SAFE); bad["halting_decider"]=1
        r=certify({"system":"UTM","step":1,"branch":0,"budget":1,
                   "status":"HALTED","order":0,"claims":bad})
        self.assertEqual(r["closed"],0)

    def test_trader_buy(self):
        r=certify({"system":"TRADER_42","step":8,"previous_step":7,"branch":1,"budget":20,
                   "status":"COMMITTED","operation":"BUY","order":1,
                   "from_state":"FLAT","target_state":"LONG","claims":SAFE})
        self.assertEqual(r["closed"],1)

    def test_trader_invalid_transition(self):
        r=certify({"system":"TRADER_42","step":8,"branch":1,"budget":20,
                   "status":"COMMITTED","operation":"BUY","order":1,
                   "from_state":"LONG","target_state":"LONG","claims":SAFE})
        self.assertEqual(r["closed"],0)

    def test_omega_commit(self):
        r=certify({"system":"OMEGA","step":42,"previous_step":41,"branch":3,"budget":42,
                   "status":"COMMITTED","order":0,"claims":SAFE})
        self.assertEqual(r["closed"],1)

if __name__ == "__main__":
    unittest.main()
