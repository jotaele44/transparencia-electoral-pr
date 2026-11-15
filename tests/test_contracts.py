import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
class SchemaSmokeTests(unittest.TestCase):
    def test_source_required(self):
        s=json.loads((ROOT/"contracts/source_manifest.schema.json").read_text())
        self.assertEqual(len(s["required"]),len(set(s["required"])))
        self.assertIn("sha256",s["required"])
        self.assertIn("retrieved_utc",s["required"])
    def test_no_fraud_assumption(self):
        s=json.loads((ROOT/"contracts/discrepancy.schema.json").read_text())
        self.assertNotIn("FRAUD",s["properties"]["classification"]["enum"])
        self.assertIn("UNRESOLVED",s["properties"]["review_status"]["enum"])
if __name__=="__main__":unittest.main()
