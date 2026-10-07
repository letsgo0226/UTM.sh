import unittest
import core

class IntentFieldTests(unittest.TestCase):
    def setUp(self):
        self.r=core.load_registry()

    def test_registry_is_valid_and_deterministic(self):
        a=core.validate_registry(self.r)
        b=core.validate_registry(self.r)
        self.assertTrue(a["valid"])
        self.assertEqual(a["registry_digest"],b["registry_digest"])
        self.assertGreaterEqual(a["atom_count"],20)

    def test_goal_advance_is_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"worldline-candidate-1",
            "advanced":["GOAL-NO-WAR-COERCION","GOAL-DIALOGUE-REPAIR"],
            "preserved":["INV-HUMAN-AGENCY","INV-CLAIM-SEPARATION"]
        })
        self.assertEqual(c["closed"],1)
        self.assertGreater(c["goal_delta"],0)

    def test_hard_invariant_violation_fails_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"candidate-with-coercion",
            "violated":["INV-HUMAN-AGENCY"]
        })
        self.assertEqual(c["closed"],0)
        self.assertIn("INV-HUMAN-AGENCY",c["hard_violations"])

    def test_claim_boundary_violation_fails_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"overclaim",
            "violated":["BOUND-NO-GUARANTEED-PEACE"]
        })
        self.assertEqual(c["closed"],0)

    def test_unknown_atom_fails_closed(self):
        c=core.certify_transition(self.r,{"advanced":["GOAL-UNKNOWN"]})
        self.assertEqual(c["closed"],0)
        self.assertEqual(c["unknown_atoms"],["GOAL-UNKNOWN"])

if __name__=="__main__":
    unittest.main()
