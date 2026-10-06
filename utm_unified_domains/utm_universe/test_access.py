import json, os, socket, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        self.start('test-token')

    def start(self, token, federation=''):
        env = dict(os.environ, PORT=str(self.port), AKASHIC_PATH=self.tmp.name+'/events.jsonl',
                   FABRIC_PATH=self.tmp.name+'/fabric.json', FEDERATION_TOKEN=federation,
                   UTM_ACCESS_TOKEN=token, FEDERATION_PEERS='')
        self.proc = subprocess.Popen([sys.executable, 'server.py'], cwd=Path(__file__).parent,
                                     env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                if self.req('/health')[0] == 200:
                    return
            except (URLError, OSError):
                time.sleep(0.02)
        raise RuntimeError('server did not start')

    def tearDown(self):
        self.proc.terminate(); self.proc.wait(timeout=5); self.tmp.cleanup()

    def req(self, path, data=None, token=None):
        headers = {'Content-Type': 'application/json'}
        if token is not None:
            headers['Authorization'] = 'Bearer '+token
        r = Request('http://127.0.0.1:'+str(self.port)+path,
                    data=None if data is None else json.dumps(data).encode(), headers=headers)
        try:
            response = urlopen(r, timeout=2)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_private_reads_require_auth(self):
        for path in ['/akashic', '/resident', '/resident/missing', '/resident/missing/compute', '/compute/jobs', '/compute/jobs/missing']:
            self.assertEqual(self.req(path)[0], 401)
            self.assertEqual(self.req(path, token='wrong')[0], 401)

    def test_private_writes_reject_before_mutation(self):
        before = self.req('/health')[1]
        for path in ['/resident/admit','/resident/resume','/compute/jobs','/compute/jobs/missing/continue','/compute/jobs/missing/takeover','/utm/run']:
            self.assertEqual(self.req(path, {})[0], 401)
        after = self.req('/health')[1]
        self.assertEqual(before['events'], after['events'])
        self.assertEqual(before['jobs'], after['jobs'])

    def test_authorized_resident_survives_restart(self):
        status, body = self.req('/resident/admit', {'capsule': {'agent_id':'test', 'state':'preserved'}}, 'test-token')
        self.assertEqual(status, 201)
        path = '/resident/'+body['resident_id']
        self.assertEqual(self.req(path, token='test-token')[1]['capsule']['state'], 'preserved')
        self.proc.terminate(); self.proc.wait(timeout=5); self.start('test-token')
        self.assertEqual(self.req(path, token='test-token')[1]['capsule']['state'], 'preserved')
        self.assertEqual(self.req(path)[0], 401)

    def test_public_health_and_discovery(self):
        for path in ['/health','/manifest','/world','/.well-known/utm-seed.json','/federation/status']:
            self.assertEqual(self.req(path)[0], 200)
        self.assertFalse(self.req('/manifest')[1]['access_control']['per_resident_ownership'])

    def test_federation_token_remains_separate(self):
        self.proc.terminate(); self.proc.wait(timeout=5); self.start('test-token', 'peer-token')
        self.assertEqual(self.req('/federation/snapshot', token='test-token')[0], 401)
        self.assertEqual(self.req('/federation/snapshot', token='peer-token')[0], 200)
        self.assertEqual(self.req('/resident/missing', token='peer-token')[0], 401)

    def test_empty_access_token_fails_closed(self):
        self.proc.terminate(); self.proc.wait(timeout=5); self.start('', 'peer-token')
        self.assertEqual(self.req('/resident/missing', token='peer-token')[0], 401)
        self.assertEqual(self.req('/health')[0], 200)


if __name__ == '__main__':
    unittest.main()
