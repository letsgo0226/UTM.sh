"""Non-networked runtime tests with a local loopback HTTP server."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from server import Handler

class TestReadOnlyRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=3)

    def request(self, path, method="GET"):
        with urlopen(Request(f"http://127.0.0.1:{self.port}{path}", method=method), timeout=5) as response:
            return response.status, response.headers, response.read()

    def test_health(self):
        status, _, payload = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["status"], "ok")

    def test_public_registry(self):
        status, h, payload = self.request("/v1/registry")
        data = json.loads(payload)
        self.assertEqual(status, 200)
        self.assertEqual(h["Access-Control-Allow-Origin"], "*")
        self.assertIsNone(data["model"]["clinical_or_veterinary_efficacy"])
        self.assertFalse(data["formal"]["universal_halting_solver"])
        self.assertEqual(data["model"]["replenished_and_finite"]["1"]["safe_kernel_size"], 12)
        self.assertEqual(data["model"]["replenished_and_finite"]["0"]["safe_kernel_size"], 0)
        self.assertIn("cat", data["species"])

    def test_unified_virtual_registry(self):
        status, _, payload = self.request("/v1/unified")
        data = json.loads(payload)
        self.assertEqual(status, 200)
        self.assertEqual(data["deployments_triggered"], 0)
        self.assertEqual(len(data["services"]), 6)
        self.assertEqual(data["total_steps"], 31)
        self.assertFalse(data["real_time_synchronization"])

    def test_machine_discovery(self):
        self.assertIn(b"/v1/registry", self.request("/llms.txt")[2])
        self.assertEqual(json.loads(self.request("/openapi.json")[2])["openapi"], "3.0.3")

    def test_no_mutation(self):
        with self.assertRaises(HTTPError) as c:
            self.request("/v1/registry", method="POST")
        self.assertEqual(c.exception.code, 405)

    def test_head_does_not_return_body(self):
        status, _, body = self.request("/health", method="HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")

if __name__ == "__main__":
    unittest.main()
