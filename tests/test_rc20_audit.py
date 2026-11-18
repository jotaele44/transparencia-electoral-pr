import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC20Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'certification/rc20_audit_only.json').read_text())
 def test_release_blocked(self):
  self.assertFalse(self.x['certified']);self.assertFalse(self.x['production_authorized'])
  self.assertFalse(self.x['merge_authorized']);self.assertEqual(self.x['state'],'AUDIT_ONLY')
 def test_original_bytes_not_fabricated(self):
  self.assertIsNone(self.x['source_findings']['guide_original_sha256'])
  self.assertEqual(self.x['source_findings']['verified_original_pdf_sha256_count'],0)
  self.assertIsNone(self.x['source_findings']['authoritative_full_event_denominator'])
 def test_effective_date_conflict_preserved(self):
  s=self.x['source_findings']
  self.assertEqual(s['law_effective_index_date'],'2026-04-08')
  self.assertEqual(s['rc19_computed_effective_date'],'2026-04-09')
  self.assertEqual(s['effective_date_status'],'CONTRADICTION_UNRESOLVED')
 def test_no_runtime_or_rollback_claim(self):
  s=self.x['software']
  self.assertEqual(s['real_Centinelas_runtime'],'NOT_EXECUTED')
  self.assertEqual(s['cross_repo_rollback'],'NOT_EXECUTED')
 def test_production_off(self):
  self.assertTrue(all(v is False for v in self.x['safety'].values()))
if __name__=='__main__':unittest.main()
