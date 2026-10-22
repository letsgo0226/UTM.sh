import copy
import json
import unittest
from pathlib import Path
from unified_machine import simulate
SOURCE = json.loads((Path(__file__).resolve().parent / "unified_registry.json").read_text())

class UnifiedTests(unittest.TestCase):
    def test_deterministic_and_bounded(self):
        a=simulate(SOURCE)
        b=simulate(copy.deepcopy(SOURCE))
        self.assertEqual(a,b)
        self.assertEqual(a["deployments_triggered"],0)
        self.assertEqual(a["total_steps"], a["events_count"])
        self.assertLessEqual(a["total_steps"],SOURCE["limits"]["global_steps"])
        self.assertTrue(all(s["status"]=="HALTED" for s in a["services"]))
        self.assertFalse(a["real_time_synchronization"])

    def test_nonhalting_loop_is_bounded(self):
        p=copy.deepcopy(SOURCE)
        p["virtual_services"]=[{"id":"loop","domain":"test-only","program":"+[]","external_apply_enabled":False}]
        p["limits"]["steps_per_job"]=8
        self.assertEqual(simulate(p)["services"][0]["status"],"BOUNDED_STEPS")

    def test_rejects_authority(self):
        p=copy.deepcopy(SOURCE)
        p["virtual_services"][0]["external_apply_enabled"]=True
        with self.assertRaises(ValueError):
            simulate(p)

    def test_rejects_expanding_envelope(self):
        p=copy.deepcopy(SOURCE)
        p["limits"]["global_steps"]=999999999
        with self.assertRaises(ValueError):
            simulate(p)

    def test_fair_round_robin(self):
        p=copy.deepcopy(SOURCE)
        p["virtual_services"]=[
            {"id":"a","domain":"test","program":"+[]","external_apply_enabled":False},
            {"id":"b","domain":"test","program":"+[]","external_apply_enabled":False}]
        p["limits"]["steps_per_job"]=32
        p["limits"]["global_steps"]=10
        run=simulate(p)
        self.assertEqual(run["total_steps"],10)
        self.assertEqual([s["steps"] for s in run["services"]],[5,5])
        self.assertTrue(all(s["status"]=="BOUNDED_GLOBAL" for s in run["services"]))

if __name__=="__main__":
    unittest.main()
