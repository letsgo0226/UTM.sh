#!/usr/bin/env python3
import math, unittest
import ucbc

class UCBCTests(unittest.TestCase):
    def test_symbolic_codec_certificate(self):
        r=ucbc.symbolic_certificate(3,5,2)
        self.assertTrue(r["valid"])
        self.assertEqual(r["ab"],"15")
        self.assertEqual(r["unordered_prime_decode"],[3,5])
        self.assertFalse(r["c_alone_is_payload_code"])

    def test_numeric_shared_base_when_coordinates_constructed_from_same_c(self):
        c=2.0
        x=math.log(3,c)
        y=math.log(5,c)
        r=ucbc.numeric_compatibility(3,5,x,y)
        self.assertTrue(r["compatible_numeric"])
        self.assertTrue(r["product_relation_numeric"])
        self.assertAlmostEqual(r["shared_c_numeric"],2.0,places=11)

    def test_incompatible_coordinates_rejected(self):
        r=ucbc.numeric_compatibility(2,3,1.0,1.0)
        self.assertFalse(r["compatible_numeric"])

    def test_distinct_primes_cannot_share_nonzero_rational_coordinates(self):
        r=ucbc.exact_rational_compatibility(2,3,1,1,1,1)
        self.assertFalse(r["compatible_exact"])
        self.assertTrue(r["authoritative"])

    def test_same_sign_requirement(self):
        r=ucbc.exact_rational_compatibility(2,3,1,1,-1,1)
        self.assertFalse(r["compatible_exact"])

if __name__=="__main__":
    unittest.main()
