import json,subprocess,unittest
from pathlib import Path
P=Path(__file__).with_name("fixed_point.sh")
class T(unittest.TestCase):
    def test_core(self):
        r=subprocess.run(["sh",str(P)],capture_output=True,text=True,check=True)
        o=json.loads(r.stdout)
        self.assertEqual(o["protocol"],"CLS-Recursive-Fixed-Point/1.0")
        self.assertEqual(o["program_index"],o["self_source_godel"])
        self.assertFalse(o["claims"]["oracle"])
        self.assertFalse(o["claims"]["self_awareness"])
if __name__=='__main__': unittest.main()
