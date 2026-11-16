import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC11EvidenceGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/"evidence/rc11_source_manifest.json").read_text())
  cls.n=json.loads((ROOT/"evidence/rc11_reporting_unit_namespace.json").read_text())
  cls.c=json.loads((ROOT/"evidence/rc11_case_registry.json").read_text())
 def test_report_not_claimed_hashed(self):
  r=next(x for x in self.m["source_manifestations"] if x["id"]=="cee_2024_statistical_report_2026_approved")
  self.assertIsNone(r["byte_sha256"]);self.assertFalse(r["original_bytes_frozen"]);self.assertFalse(r["content_reviewed"])
 def test_2025_2026_versions_not_assumed_equal(self):
  self.assertEqual(self.m["version_conflicts"][0]["relationship"],"UNRESOLVED; do not assume same bytes or logical content")
 def test_denominator_open(self):
  self.assertIsNone(self.m["closure"]["complete_reporting_unit_denominator"])
  self.assertEqual(self.m["closure"]["original_source_byte_hashes"],0)
 def test_official_locator_not_canonical_id(self):
  self.assertIn("NOT_STABLE_IDENTITY",self.n["classification"])
  self.assertEqual(self.n["third_party_columns"]["binding"],"UNRESOLVED; names and matching counts cannot prove equivalence")
 def test_case_allegations_not_findings(self):
  c=self.c["cases"][0]
  self.assertEqual(c["official_disposition"]["state"],"NO_HA_LUGAR")
  self.assertIn("fraud or intentional manipulation",c["official_disposition"]["not_established"])
  self.assertEqual(c["qa"],"FULL_12_PAGE_VISUAL_REVIEW; original bytes and SHA-256 unverified; no underlying ballot totals or individual records acquired.")
 def test_no_930_equals_disputed_ballots(self):
  c=self.c["cases"][0]
  self.assertIn("930 ballots were unadjudicated",c["official_disposition"]["not_established"])
if __name__=="__main__":unittest.main()
