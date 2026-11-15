import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from reconcile import reconcile

def item(unit="001", votes=3):
    return {"election_id": "2024", "contest_id": "fixture", "reporting_unit_id": unit, "candidate_id": "stable-id", "vote_method": "in_person", "votes": votes}

class TestReconcile(unittest.TestCase):
    def test_match(self): self.assertEqual(reconcile([item()], [item()])["counts"]["MATCH"], 1)
    def test_change(self): self.assertEqual(reconcile([item()], [item(votes=4)])["counts"]["VALUE_DIFFERENCE"], 1)
    def test_missing_not_zero(self): self.assertIsNone(reconcile([item()], [])["rows"][0]["right_votes"])
    def test_duplicate(self):
        with self.assertRaises(ValueError): reconcile([item(), item()], [])
    def test_negative(self):
        with self.assertRaises(ValueError): reconcile([item(votes=-1)], [])
    def test_bool(self):
        with self.assertRaises(ValueError): reconcile([item(votes=True)], [])
    def test_no_heuristic_merge(self): self.assertEqual(reconcile([item("01")], [item("001")])["symmetric_difference_count"], 2)
    def test_federation_fail_closed(self):
        x = json.loads((ROOT / "federation.json").read_text())
        self.assertFalse(x["federation_readiness_gate"]["ready_for_hub_discovery"])
        self.assertFalse(x["federation_readiness_gate"]["ready_for_hub_live_execution"])
    def test_registry_unfrozen(self):
        x = json.loads((ROOT / "evidence/cee_registry.json").read_text())
        self.assertTrue(all(s["sha256"] is None for s in x["sources"]))

if __name__ == "__main__": unittest.main()
