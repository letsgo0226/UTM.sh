import unittest
from resource_guard import g257, decode257, atgc, decode_atgc, bounded_vm, check

def proposal(est=None, cap=None):
    return {"declared_estimate": est or {"build_context_bytes":100, "runtime_memory_mb":32, "persistent_volume_mb":0},
            "declared_ceiling": cap or {"build_context_bytes":1000, "runtime_memory_mb":64, "persistent_volume_mb":500}}

class TestResourceGuard(unittest.TestCase):
    def test_roundtrips(self):
        for b in (b"", b"abc", bytes(range(256))):
            self.assertEqual(decode257(g257(b)), b)
            self.assertEqual(decode_atgc(atgc(b)), b)

    def test_bounded_is_not_nonhalting_proof(self):
        self.assertEqual(bounded_vm("+[+]", steps=30)["status"], "BOUNDED")
        self.assertEqual(bounded_vm("+.", steps=10)["output_hex"], "01")
        self.assertEqual(bounded_vm("<")["reason"], "tape_limit")
        self.assertEqual(bounded_vm("[")["status"], "REJECTED")

    def test_complete_declared_budget(self):
        r=check(proposal())
        self.assertEqual(r["result"],"PREFLIGHT_PASS")
        self.assertFalse(r["formal"]["infinite_resource_created"])

    def test_fail_closed(self):
        d=proposal()
        d["declared_estimate"]["persistent_volume_mb"]=512
        self.assertEqual(check(d)["result"],"BLOCK")
        d["declared_ceiling"]["persistent_volume_mb"]=None
        self.assertEqual(check(d)["result"],"REVIEW_REQUIRED")
        self.assertEqual(check({"declared_estimate":{}, "declared_ceiling":{}})["result"], "REVIEW_REQUIRED")

if __name__=="__main__":
    unittest.main()
