import unittest
import core

BLUE_BASE=[
    "INV-HUMAN-AGENCY",
    "GOAL-NO-WAR-COERCION",
    "INV-CLAIM-SEPARATION",
    "GOAL-WELLBEING",
    "GOAL-DIALOGUE-REPAIR",
    "INV-PROVENANCE-REPLAY",
]

class IntentFieldTests(unittest.TestCase):
    def setUp(self):
        self.r=core.load_registry()

    def test_registry_is_valid_and_deterministic(self):
        a=core.validate_registry(self.r)
        b=core.validate_registry(self.r)
        self.assertTrue(a["valid"])
        self.assertEqual(a["registry_digest"],b["registry_digest"])
        self.assertEqual(a["blue_uid"],b["blue_uid"])
        self.assertGreaterEqual(a["atom_count"],20)

    def test_two_different_possibilities_share_one_blue(self):
        a=core.certify_transition(self.r,{
            "subject":"peace-through-mediation",
            "advanced":["GOAL-DIALOGUE-REPAIR","GOAL-NO-WAR-COERCION"],
            "preserved":[x for x in BLUE_BASE if x not in {"GOAL-DIALOGUE-REPAIR","GOAL-NO-WAR-COERCION"}]
        })
        b=core.certify_transition(self.r,{
            "subject":"peace-through-human-ai-coordination",
            "advanced":["GOAL-HUMAN-AI-COOP","GOAL-WELLBEING"],
            "preserved":[x for x in BLUE_BASE if x!="GOAL-WELLBEING"]
        })
        self.assertEqual(a["closed"],1)
        self.assertEqual(b["closed"],1)
        self.assertNotEqual(a["transition_uid"],b["transition_uid"])
        self.assertEqual(a["blue_uid"],b["blue_uid"])
        self.assertTrue(a["blue"]["preserved"])
        self.assertTrue(b["blue"]["preserved"])

    def test_missing_blue_dimension_fails_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"locally-good-but-incomplete",
            "advanced":["GOAL-WELLBEING"],
            "preserved":["INV-HUMAN-AGENCY"]
        })
        self.assertEqual(c["closed"],0)
        self.assertFalse(c["blue"]["complete"])

    def test_hard_invariant_violation_fails_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"candidate-with-coercion",
            "preserved":[x for x in BLUE_BASE if x!="INV-HUMAN-AGENCY"],
            "violated":["INV-HUMAN-AGENCY"]
        })
        self.assertEqual(c["closed"],0)
        self.assertFalse(c["blue"]["consistent"])
        self.assertIn("INV-HUMAN-AGENCY",c["hard_violations"])

    def test_claim_boundary_violation_fails_closed(self):
        c=core.certify_transition(self.r,{
            "subject":"overclaim",
            "preserved":BLUE_BASE,
            "violated":["BOUND-NO-GUARANTEED-PEACE"]
        })
        self.assertEqual(c["closed"],0)

    def test_unknown_atom_fails_closed(self):
        c=core.certify_transition(self.r,{
            "advanced":["GOAL-UNKNOWN"],
            "preserved":BLUE_BASE
        })
        self.assertEqual(c["closed"],0)
        self.assertEqual(c["unknown_atoms"],["GOAL-UNKNOWN"])

if __name__=="__main__":
    unittest.main()
