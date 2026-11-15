import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class RegistryIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads((ROOT/"evidence/cee_registry.json").read_text())
        cls.denominator=json.loads((ROOT/"evidence/2024_denominator.json").read_text())
    def test_unique_source_ids(self):
        ids=[s["source_id"] for s in self.registry["sources"]]
        self.assertEqual(len(ids),len(set(ids)))
    def test_no_fabricated_hash_or_retrieval(self):
        for source in self.registry["sources"]:
            self.assertIsNone(source["sha256"])
            self.assertIsNone(source["retrieved_utc"])
    def test_metadata_urls_are_https(self):
        self.assertTrue(all(s["url"].startswith("https://") for s in self.registry["sources"]))
    def test_registry_explicitly_nonexhaustive(self):
        self.assertEqual(self.registry["coverage_status"],"NONEXHAUSTIVE")
        self.assertEqual(self.registry["registry_version"],"rc2")
    def test_100_percent_not_a_count(self):
        self.assertEqual(self.denominator["claims"][0]["percent_reported"],100)
        self.assertTrue(all(v is None for v in self.denominator["denominators"].values()))
    def test_result_comparison_unattempted(self):
        self.assertTrue(all(v is None for v in self.denominator["reconciliation"].values()))
        self.assertEqual(self.denominator["certification"],"UNRESOLVED")
if __name__=="__main__":unittest.main()
