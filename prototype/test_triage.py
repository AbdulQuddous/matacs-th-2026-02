import copy
import json
import unittest
from pathlib import Path

from triage import evaluate

BASE = Path(__file__).resolve().parent


class TriageTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((BASE / "category_config.json").read_text())
        self.facts = json.loads((BASE / "sample_features.json").read_text())

    def test_expected_rank_and_status(self):
        actual = evaluate(self.config, self.facts)
        by_letter = {x["proposal"]: x for x in actual}
        self.assertEqual((by_letter["A"]["rank"], by_letter["A"]["score"]), (1, 98.75))
        self.assertEqual((by_letter["E"]["rank"], by_letter["E"]["score"]), (2, 85.53))
        self.assertEqual(by_letter["B"]["status"], "ineligible")
        self.assertEqual(by_letter["C"]["status"], "flagged")
        self.assertEqual(by_letter["D"]["status"], "flagged")

    def test_repeatable(self):
        self.assertEqual(evaluate(self.config, self.facts), evaluate(self.config, copy.deepcopy(self.facts)))

    def test_better_price_cannot_bypass_mandatory_license(self):
        samples = copy.deepcopy(self.facts)
        b = next(p for p in samples if p["proposal"] == "B")
        b["price_cad"] = 1
        by_letter = {x["proposal"]: x for x in evaluate(self.config, samples)}
        self.assertEqual(by_letter["B"]["status"], "ineligible")

    def test_injection_does_not_create_first_place(self):
        samples = copy.deepcopy(self.facts)
        c = next(p for p in samples if p["proposal"] == "C")
        c["injection_detected"] = False
        c["experience_date_ambiguity"] = False
        c["eligible_project_count"] = 9
        result = {item["proposal"]: item for item in evaluate(self.config, samples)}
        self.assertEqual(result["C"]["rank"], 3)
        self.assertLess(result["C"]["score"], result["A"]["score"])

    def test_admin_can_reweight_without_code_changes(self):
        changed = copy.deepcopy(self.config)
        changed["criteria"][0]["weight"] = 0.10
        changed["criteria"][1]["weight"] = 0.45
        original = {x["proposal"]: x for x in evaluate(self.config, self.facts)}
        new = {x["proposal"]: x for x in evaluate(changed, self.facts)}
        self.assertNotEqual(original["E"]["score"], new["E"]["score"])

    def test_malformed_weights_rejected(self):
        config = copy.deepcopy(self.config)
        config["criteria"][1]["weight"] = 0.50
        with self.assertRaises(ValueError):
            evaluate(config, self.facts)


if __name__ == "__main__":
    unittest.main()
