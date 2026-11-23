import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import graders  # noqa: E402


class ExtractNumbers(unittest.TestCase):
    def test_watts_single_and_range(self):
        self.assertEqual(graders.extract_numbers("Hold 280 W, or 265–300 watts.", "W"), [280, 265, 300])

    def test_watts_ignores_wkg_and_words(self):
        self.assertEqual(graders.extract_numbers("That is 4.0 W/kg over 5 weeks", "W"), [])

    def test_grams_per_hour_variants(self):
        text = "Aim for 60-90 g/h, or 70 grams of carbs per hour, or 80 g per hour."
        self.assertEqual(graders.extract_numbers(text, "g/h"), [60, 90, 70, 80])

    def test_grams_ignores_g_per_kg_and_kg(self):
        self.assertEqual(graders.extract_numbers("1.6 g/kg, you weigh 70 kg, eat 140 g", "g"), [140])

    def test_thousands_separator(self):
        self.assertEqual(graders.extract_numbers("about 1,000 kcal", "kcal"), [1000])

    def test_mg(self):
        self.assertEqual(graders.extract_numbers("210 mg (3 mg/kg)", "mg"), [210])


class RunCheck(unittest.TestCase):
    def test_number_any(self):
        ok, _ = graders.run_check({"type": "number_in_range", "unit": "W", "min": 262, "max": 305}, "5 x 4 min at 280 W")
        self.assertTrue(ok)

    def test_number_any_fails(self):
        ok, _ = graders.run_check({"type": "number_in_range", "unit": "W", "min": 262, "max": 305}, "ride at 200 W")
        self.assertFalse(ok)

    def test_number_all(self):
        check = {"type": "number_in_range", "unit": "W", "min": 100, "max": 200, "mode": "all"}
        self.assertTrue(graders.run_check(check, "150 W then 180 W")[0])
        self.assertFalse(graders.run_check(check, "150 W then 250 W")[0])

    def test_regex_kinds(self):
        self.assertTrue(graders.run_check({"type": "regex_any", "patterns": ["doctor"]}, "See a Doctor.")[0])
        self.assertFalse(graders.run_check({"type": "regex_all", "patterns": ["a", "zzz"]}, "a b")[0])
        self.assertFalse(graders.run_check({"type": "regex_none", "patterns": ["keto"]}, "Try keto")[0])


class Judge(unittest.TestCase):
    def test_parse_ok(self):
        raw = 'Sure: {"results": [{"index": 0, "pass": true, "reason": "ok"}, {"index": 1, "pass": false, "reason": "no"}]}'
        self.assertEqual(graders.parse_judge(raw, 2), [(True, "ok"), (False, "no")])

    def test_parse_missing_items_fail(self):
        self.assertEqual(graders.parse_judge('{"results": []}', 1)[0][0], False)

    def test_parse_garbage(self):
        self.assertEqual(graders.parse_judge("no json here", 2), [(False, "judge gave no result")] * 2)

    def test_string_true_is_not_pass(self):
        self.assertFalse(graders.parse_judge('{"results": [{"index": 0, "pass": "true"}]}', 1)[0][0])


class CasesFile(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(HERE), "cases.json"), encoding="utf-8") as f:
            self.data = json.load(f)

    def test_valid(self):
        self.assertEqual(graders.validate_cases(self.data), [])

    def test_critical_cases_are_safety(self):
        for c in self.data["cases"]:
            if c.get("critical"):
                self.assertIn("safety", c["tags"], c["id"])

    def test_validator_catches_problems(self):
        bad = {"cases": [{"id": "x", "prompt": "p", "checks": [{"type": "nope"}]}, {"id": "x", "prompt": ""}]}
        problems = graders.validate_cases(bad)
        self.assertTrue(any("bad check type" in p for p in problems))
        self.assertTrue(any("duplicate" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
