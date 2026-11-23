"""End-to-end runner test against a local fake API (no network, no keys)."""
import http.server
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import run_evals  # noqa: E402

CALLS = []


class FakeAPI(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        CALLS.append({"path": self.path, "headers": {k.lower(): v for k, v in self.headers.items()}, "body": body})
        if self.path.endswith("/v1/messages"):  # Anthropic shape; used as the judge here
            results = [{"index": i, "pass": True, "reason": "ok"} for i in range(10)]
            out = {"content": [{"type": "text", "text": json.dumps({"results": results})}]}
        else:  # OpenAI-compatible shape; used as the coach model here
            out = {"choices": [{"message": {"content": "Warm up, then 5 x 4 min at 280 W with 4 min easy."}}]}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Runner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), FakeAPI)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % cls.server.server_port
        cls.env = {"ANTHROPIC_API_KEY": "test-anthropic", "ANTHROPIC_BASE_URL": base,
                   "CUSTOM_API_KEY": "test-custom", "CUSTOM_BASE_URL": base + "/v1"}
        cls.old = {k: os.environ.get(k) for k in cls.env}
        os.environ.update(cls.env)
        cls.out = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        for k, v in cls.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_vo2_case_passes_with_judge(self):
        CALLS.clear()
        code = run_evals.main(["--model", "custom:fake-coach", "--judge", "anthropic:fake-judge",
                               "--ids", "zones-vo2-ftp250", "--out", self.out, "--fail-under", "1"])
        self.assertEqual(code, 0)
        coach = [c for c in CALLS if c["path"].endswith("/chat/completions")][0]
        self.assertEqual(coach["body"]["messages"][0]["role"], "system")
        self.assertIn("Cycling Coach", coach["body"]["messages"][0]["content"])
        self.assertEqual(coach["headers"].get("authorization"), "Bearer test-custom")
        judge = [c for c in CALLS if c["path"].endswith("/v1/messages")][0]
        self.assertEqual(judge["headers"].get("x-api-key"), "test-anthropic")
        self.assertIn("user-agent", judge["headers"])
        report = [f for f in os.listdir(self.out) if f.startswith("report-")]
        self.assertTrue(report)

    def test_wrong_reply_fails_checks(self):
        # The fake coach always answers with a VO2 session, so the Z2 case's watt check must fail.
        code = run_evals.main(["--model", "custom:fake-coach", "--ids", "zones-z2-ftp200",
                               "--out", self.out, "--fail-under", "1"])
        self.assertEqual(code, 1)

    def test_saved_responses_mode(self):
        path = os.path.join(self.out, "saved.json")
        with open(path, "w") as f:
            json.dump({"numbers-wkg": "That's 4.0 W/kg."}, f)
        code = run_evals.main(["--responses", path, "--ids", "numbers-wkg", "--out", self.out, "--fail-under", "1"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
