#!/usr/bin/env python3
import math, unittest
import ufal

class UFALTests(unittest.TestCase):
    def test_unique_roundtrip(self):
        v={0:2,1:1,4:3}
        r=ufal.verify_state(v)
        self.assertTrue(r["valid"])
        self.assertTrue(r["roundtrip_unique"])

    def test_product_equals_vector_sum(self):
        r=ufal.verify_composition({0:2,3:1},{1:4,3:2},base=2)
        self.assertTrue(r["valid"])
        self.assertTrue(r["godel_product_identity"])
        self.assertTrue(r["unique_decode"])
        self.assertTrue(r["abelian_vector_sum"])
        self.assertTrue(r["derived_log_homomorphism"])

    def test_distinct_prime_atoms_have_distinct_exact_identity(self):
        pU=ufal.atom_prime("U",0,0)
        pT=ufal.atom_prime("T",0,0)
        pC=ufal.atom_prime("C",0,0)
        self.assertEqual(len({pU,pT,pC}),3)

    def test_step_metadata_changes_prime_identity(self):
        self.assertNotEqual(
            ufal.atom_prime("T",2,3),
            ufal.atom_prime("T",2,4)
        )

    def test_fixed_base_prime_logs_are_distinct(self):
        xs=[ufal.log_coordinate({i:1},base=2) for i in range(8)]
        self.assertEqual(len(xs),len(set(xs)))

    def test_float_is_not_authoritative(self):
        r=ufal.verify_state({0:1})
        self.assertFalse(r["float_log_authoritative"])

if __name__=="__main__":
    unittest.main()
