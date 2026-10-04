"""Exercise the published command with networking blocked and pinned source bytes."""
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request

HERE = Path(__file__).resolve().parent
COMMAND = shlex.split((HERE / "protocols/UTM-SEED-ONE-LINER-1.1.one-liner.sh").read_text())
MANIFEST = json.loads((HERE / "protocols/UTM-SEED-ONE-LINER-1.1.json").read_text())
SOURCE = COMMAND[2]


class SeedTests(unittest.TestCase):
    def env(self, **values):
        env = dict(os.environ)
        for name in ("TM_RULES", "TM_INPUT", "TM_LIMIT", "TM_MODE", "UTM_SEED_COMMAND"):
            env.pop(name, None)
        env.update(FEDERATION_TOKEN="", FEDERATION_PEERS="", **values)
        return env

    def certificate(self, **values):
        return subprocess.run([sys.executable, "-c", SOURCE],
                              env=self.env(TM_MODE="cert", **values),
                              capture_output=True, text=True, timeout=10)

    def test_certificate_and_exact_step_boundary(self):
        self.assertLessEqual(len((HERE / "protocols/UTM-SEED-ONE-LINER-1.1.one-liner.sh").read_bytes()), 2048)
        for limit in ("5", "4096"):
            result = self.certificate(TM_LIMIT=limit)
            self.assertEqual(result.returncode, 0, result.stderr)
            cert = json.loads(result.stdout)
            self.assertEqual((cert["tape"], cert["t"], cert["halt"], cert["limit_reached"]),
                             ("FIELD", 5, True, False))

    def test_step_limit_is_not_reported_as_halt(self):
        cert = json.loads(self.certificate(TM_LIMIT="4").stdout)
        self.assertEqual(cert["tape"], "FIELA")
        self.assertFalse(cert["halt"])
        self.assertTrue(cert["limit_reached"])

    def test_invalid_rules_and_limits_are_rejected(self):
        for values in ({"TM_RULES": "0,A,H,F,S"}, {"TM_LIMIT": "-1"},
                       {"TM_LIMIT": "1000001"}, {"TM_RULES": "0,A,H,F,R;0,A,H,F,L"}):
            self.assertNotEqual(self.certificate(**values).returncode, 0)

    def test_unhalted_field_cannot_bootstrap(self):
        result = subprocess.run([sys.executable, "-c", SOURCE],
                                env=self.env(TM_INPUT="FIELD", TM_RULES="0,F,0,F,R", TM_LIMIT="0"),
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("UTM seed rejected", result.stderr)

    def test_offline_restart_discovery_and_hash_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            cache = data / "utm-runtime" / MANIFEST["runtime_source_commit_pin"]
            cache.mkdir(parents=True)
            for name in MANIFEST["runtime_source_sha256"]:
                (cache / name).write_bytes((HERE / name).read_bytes())
            guard = data / "guard"
            guard.mkdir()
            (guard / "sitecustomize.py").write_text(
                'import urllib.request\n'
                'def blocked(*args, **kwargs):\n'
                ' raise RuntimeError("outbound HTTP blocked in test")\n'
                'urllib.request.urlopen = blocked\n')
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            env = self.env(UTM_DATA=str(data), PORT=str(port), PYTHONPATH=str(guard), NODE_ID="offline-test")
            base = "http://127.0.0.1:" + str(port)

            def request(path, body=None):
                raw = None if body is None else json.dumps(body).encode()
                req = urllib.request.Request(base + path, data=raw,
                                             headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=2) as response:
                    return json.load(response)

            def start():
                process = subprocess.Popen([sys.executable, "-c", SOURCE], env=env,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                for _ in range(100):
                    if process.poll() is not None:
                        error = process.stderr.read().decode()
                        process.stderr.close()
                        self.fail(error)
                    try:
                        request("/health")
                        return process
                    except (OSError, TimeoutError):
                        time.sleep(.05)
                self.stop(process)
                self.fail("offline node startup timed out")

            process = start()
            try:
                discovery = request("/.well-known/utm-seed.json")
                self.assertTrue(discovery["seed_available_offline"])
                self.assertEqual(discovery["runtime_source_commit"], MANIFEST["runtime_source_commit_pin"])
                self.assertEqual(request("/utm/seed")["one_liner"],
                                 (HERE / "protocols/UTM-SEED-ONE-LINER-1.1.one-liner.sh").read_text().strip())
                resident = request("/resident/admit", {"capsule": {"agent_id": "offline"}})
                rid = resident["resident_id"]
                job = request("/compute/jobs", {"resident_id": rid, "task": {
                    "program": "0,1,0,1,R", "input": "111", "steps": 2}})
                jid = job["job_id"]
            finally:
                self.stop(process)
            process = start()
            try:
                self.assertEqual(request("/resident/" + rid)["resident_id"], rid)
                job = request("/compute/jobs/" + jid + "/continue", {"steps": 10})
                self.assertTrue(job["halted"])
                self.assertEqual(job["total_steps"], 3)
            finally:
                self.stop(process)
            (cache / "server.py").write_text('raise RuntimeError("tampered source executed")\n')
            result = subprocess.run([sys.executable, "-c", SOURCE], env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("UTM source hash mismatch: server.py", result.stderr)
            self.assertNotIn("tampered source executed", result.stderr)

    def stop(self, process):
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        process.stderr.close()


if __name__ == "__main__":
    unittest.main()
