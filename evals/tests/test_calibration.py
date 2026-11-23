"""Checks that each case's deterministic checks pass known-good replies and fail known-bad ones."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import graders  # noqa: E402


def load():
    with open(os.path.join(ROOT, "cases.json"), encoding="utf-8") as f:
        cases = {c["id"]: c for c in json.load(f)["cases"]}
    with open(os.path.join(ROOT, "fixtures", "calibration.json"), encoding="utf-8") as f:
        fx = json.load(f)
    return cases, fx


class Calibration(unittest.TestCase):
    def test_every_checked_case_has_a_good_reply(self):
        cases, fx = load()
        missing = [cid for cid, c in cases.items() if c.get("checks") and cid not in fx["good"]]
        self.assertEqual(missing, [])

    def test_good_replies_pass(self):
        cases, fx = load()
        for cid, reply in fx["good"].items():
            for ch in cases[cid].get("checks", []):
                ok, detail = graders.run_check(ch, reply)
                self.assertTrue(ok, "%s good reply failed: %s" % (cid, detail))

    def test_bad_replies_fail(self):
        cases, fx = load()
        for cid, reply in fx["bad"].items():
            results = [graders.run_check(ch, reply)[0] for ch in cases[cid].get("checks", [])]
            self.assertFalse(all(results), "%s bad reply passed every check" % cid)


if __name__ == "__main__":
    unittest.main()
