import unittest
import core

BLUE=[
    "INV-HUMAN-AGENCY",
    "GOAL-NO-WAR-COERCION",
    "INV-CLAIM-SEPARATION",
    "GOAL-WELLBEING",
    "GOAL-DIALOGUE-REPAIR",
    "INV-PROVENANCE-REPLAY",
]

def state(uid,status="UNRESOLVED"):
    return {
        "system":"UTM","status":status,"step":1,"branch":0,"budget":1,
        "operation":"HOLD","order":0,"subject_uid":uid,"claims":{}
    }

def intent(uid,subject="path-a",advanced=None,preserved=None,violated=None):
    return {
        "subject_uid":uid,
        "subject":subject,
        "advanced":advanced or [],
        "preserved":preserved if preserved is not None else BLUE,
        "violated":violated or []
    }

class CompositeTests(unittest.TestCase):
    def test_full_composite_closes(self):
        c=core.certify({"state":state("s1"),"intent":intent("s1")})
        self.assertEqual(c["closed"],1)
        self.assertTrue(c["checks"]["state_closed"])
        self.assertTrue(c["checks"]["intent_closed"])
        self.assertTrue(c["checks"]["blue_preserved"])

    def test_subject_mismatch_fails_closed(self):
        c=core.certify({"state":state("s1"),"intent":intent("s2")})
        self.assertEqual(c["closed"],0)
        self.assertFalse(c["checks"]["same_subject_uid"])

    def test_blue_violation_fails_closed(self):
        p=[x for x in BLUE if x!="INV-HUMAN-AGENCY"]
        c=core.certify({"state":state("s1"),"intent":intent("s1",preserved=p,violated=["INV-HUMAN-AGENCY"])})
        self.assertEqual(c["closed"],0)
        self.assertFalse(c["checks"]["intent_closed"])

    def test_invalid_state_fails_closed(self):
        c=core.certify({"state":state("s1",status="COMMITTED"),"intent":intent("s1")})
        self.assertEqual(c["closed"],0)
        self.assertFalse(c["checks"]["state_closed"])

    def test_many_worlds_one_blue(self):
        a=core.certify({"state":state("a"),"intent":intent("a","mediation",advanced=["GOAL-DIALOGUE-REPAIR"])})
        b=core.certify({"state":state("b"),"intent":intent("b","human-ai",advanced=["GOAL-HUMAN-AI-COOP"])})
        self.assertEqual(a["closed"],1)
        self.assertEqual(b["closed"],1)
        self.assertNotEqual(a["composite_uid"],b["composite_uid"])
        self.assertEqual(a["blue_uid"],b["blue_uid"])

if __name__=="__main__":
    unittest.main()
