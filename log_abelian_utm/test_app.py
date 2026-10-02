import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app

class LogAbelianUTMTests(unittest.TestCase):
    def test_round_trip(self):
        events=[{"step":0,"op":1},{"step":1,"op":2},{"step":2,"op":0}]
        enc=app.encode_events(events)
        self.assertEqual(app.decode_godel(enc["godel_product"]), enc["canonical_events"])

    def test_commutative_representation(self):
        a=[{"step":0,"op":1},{"step":3,"op":2}]
        b=[{"step":1,"op":4}]
        ab=app.compose(a,b)
        ba=app.compose(b,a)
        self.assertEqual(ab["composition"]["godel_product"], ba["composition"]["godel_product"])
        self.assertTrue(all(ab["proof"].values()))
        self.assertTrue(all(ba["proof"].values()))

    def test_empty_identity(self):
        enc=app.encode_events([])
        self.assertEqual(enc["godel_product"], "1")
        self.assertEqual(enc["log_coordinate"], 0.0)
        self.assertEqual(app.decode_godel("1"), [])

    def test_order_is_metadata_not_multiplication_order(self):
        a=[{"step":9,"op":1},{"step":2,"op":3}]
        enc=app.encode_events(a)
        self.assertEqual(app.decode_godel(enc["godel_product"]), [
            {"step":2,"op":3},{"step":9,"op":1}
        ])

if __name__ == "__main__":
    unittest.main()
