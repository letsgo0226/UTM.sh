"""Credential-free tests of bounded proof/meta-logic decisions."""
import unittest
from proof_meta import (Invalid, classify_frame, explore_axioms, godel_encode,
                        holds, prove_bounded, substitute, verify_proof)


def P(x): return {"op":"pred","name":"P","args":[x]}
def Q(x): return {"op":"pred","name":"Q","args":[x]}
def AND(x,y): return {"op":"and","left":x,"right":y}
def IMP(x,y): return {"op":"imp","left":x,"right":y}
def FORALL(x,f): return {"op":"forall","var":x,"body":f}
def EXISTS(x,f): return {"op":"exists","var":x,"body":f}
def BOX(f): return {"op":"box","arg":f}
def DIA(f): return {"op":"diamond","arg":f}


def model(edges):
    return {"worlds":["w0","w1"], "edges":[list(e) for e in edges],
            "domain":["a","b"],
            "predicates":{"w0":{"P":[["a"]],"Q":[["a"]]},
                          "w1":{"Q":[["b"]]}}}


class InferenceTest(unittest.TestCase):
    def test_mp(self):
        pp=[IMP(P("a"),Q("a")),P("a")]
        result=prove_bounded(pp,Q("a"))
        self.assertEqual(result["status"],"PROVED_WITHIN_BUDGET")
        self.assertTrue(verify_proof(pp,result["steps"],Q("a")))
        self.assertFalse(result["external_authorization"])

    def test_forall(self):
        pp=[FORALL("x",IMP(P("x"),Q("x"))),P("a")]
        result=prove_bounded(pp,Q("a"))
        self.assertEqual(result["status"],"PROVED_WITHIN_BUDGET")
        self.assertTrue(verify_proof(pp,result["steps"],Q("a")))

    def test_and_intro(self):
        result=prove_bounded([P("a"),Q("a")],AND(P("a"),Q("a")))
        self.assertTrue(result["certificate"]["verified"])

    def test_exists_intro(self):
        result=prove_bounded([P("a")],EXISTS("x",P("x")))
        self.assertTrue(result["certificate"]["verified"])

    def test_unresolved_not_refuted(self):
        result=prove_bounded([P("a")],Q("a"),max_steps=10)
        self.assertEqual(result["status"],"UNRESOLVED_WITHIN_BUDGET")
        self.assertFalse(result["certificate"]["verified"])

    def test_nongrounded_axiom_rejected(self):
        bad=[{"rule":"premise","formula":Q("a"),"refs":[]}]
        with self.assertRaises(Invalid):
            verify_proof([P("a")],bad,Q("a"))

    def test_bad_mp_rejected(self):
        pp=[IMP(P("a"),Q("a")),P("a")]
        bad=[{"rule":"premise","formula":pp[0],"refs":[]},
             {"rule":"premise","formula":pp[1],"refs":[]},
             {"rule":"imp_elim","formula":P("a"),"refs":[0,1]}]
        with self.assertRaises(Invalid):
            verify_proof(pp,bad,P("a"))

    def test_future_reference_rejected(self):
        bad=[{"rule":"premise","formula":P("a"),"refs":[0]}]
        with self.assertRaises(Invalid):
            verify_proof([P("a")],bad,P("a"))

    def test_quantifier_capture_rejected(self):
        with self.assertRaises(Invalid):
            substitute(FORALL("y",P("x")),"x","y")

    def test_shadowing_valid(self):
        self.assertEqual(substitute(FORALL("x",P("x")),"x","a"),
                         FORALL("x",P("x")))

    def test_encoding_deterministic(self):
        self.assertEqual(godel_encode({"a":1,"b":2}),
                         godel_encode({"b":2,"a":1}))

    def test_invalid_steps_boolean_indices(self):
        s=[{"rule":"premise","formula":P("a"),"refs":[]},
           {"rule":"and_intro","formula":AND(P("a"),P("a")),"refs":[True,0]}]
        with self.assertRaises(Invalid):
            verify_proof([P("a")],s,AND(P("a"),P("a")))


class ModalTest(unittest.TestCase):
    def test_t_ax_on_reflexive_frame(self):
        m=model([("w0","w0"),("w1","w1")])
        self.assertTrue(holds(IMP(BOX(P("a")),P("a")),m,"w0"))

    def test_box_empty_relation_vacuous(self):
        m=model([])
        self.assertTrue(holds(BOX(P("b")),m,"w0"))
        self.assertFalse(holds(DIA(P("a")),m,"w0"))

    def test_modal_k_and_t(self):
        self.assertEqual(classify_frame(model([]))["satisfies_frame_conditions_for"],["K"])
        m=model([("w0","w0"),("w1","w1")])
        self.assertIn("S5",classify_frame(m)["satisfies_frame_conditions_for"])

    def test_reflexive_transitive_not_symmetric(self):
        m=model([("w0","w0"),("w1","w1"),("w0","w1")])
        self.assertEqual(classify_frame(m)["satisfies_frame_conditions_for"],["K","T","S4"])

    def test_modal_possible(self):
        self.assertTrue(holds(DIA(Q("b")),model([("w0","w1")]),"w0"))

    def test_quantifier(self):
        m=model([])
        self.assertFalse(holds(FORALL("x",P("x")),m,"w0"))
        self.assertTrue(holds(EXISTS("x",P("x")),m,"w0"))

    def test_invalid_model(self):
        m=model([])
        m["edges"]=[["w0","ghost"]]
        with self.assertRaises(Invalid):
            classify_frame(m)

    def test_unknown_domain(self):
        with self.assertRaises(Invalid):
            holds(P("z"),model([]),"w0")

    def test_nonreflexive_counterexample(self):
        m=model([("w0","w1")])
        self.assertTrue(holds(BOX(Q("b")),m,"w0"))
        self.assertFalse(holds(IMP(BOX(Q("b")),Q("b")),m,"w0"))

    def test_axiom_library_rejects_T_on_nonreflexive_frame(self):
        result=explore_axioms(model([]))
        self.assertTrue(result["candidate_axioms"]["K"]["valid_on_given_finite_frame"])
        self.assertFalse(result["candidate_axioms"]["T"]["valid_on_given_finite_frame"])
        self.assertFalse(result["unrestricted_logic_synthesis"])
        x=result["candidate_axioms"]["T"]["counterexample"]
        self.assertFalse(holds(x["axiom"],x["model"],x["world"]))

    def test_axiom_library_s4_not_s5(self):
        m=model([("w0","w0"),("w1","w1"),("w0","w1")])
        result=explore_axioms(m)
        self.assertTrue(result["candidate_axioms"]["4"]["valid_on_given_finite_frame"])
        self.assertFalse(result["candidate_axioms"]["5"]["valid_on_given_finite_frame"])
        x=result["candidate_axioms"]["5"]["counterexample"]
        self.assertFalse(holds(x["axiom"],x["model"],x["world"]))

    def test_axiom_library_rejects_4_on_nontransitive_frame(self):
        m={"worlds":["w0","w1","w2"],"edges":[["w0","w1"],["w1","w2"]],
           "domain":["a"],"predicates":{"w0":{},"w1":{},"w2":{}}}
        result=explore_axioms(m)
        self.assertFalse(result["candidate_axioms"]["4"]["valid_on_given_finite_frame"])
        x=result["candidate_axioms"]["4"]["counterexample"]
        self.assertFalse(holds(x["axiom"],x["model"],x["world"]))


if __name__ == "__main__":
    unittest.main()
