import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC21Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'certification/rc21_audit_only.json').read_text())
 def test_no_release(self):
  self.assertFalse(self.x['certified']);self.assertFalse(self.x['production_authorized'])
  self.assertFalse(self.x['merge_authorized']);self.assertEqual(self.x['classification'],'AUDIT_ONLY')
 def test_source_bytes_not_claimed(self):
  x=self.x['verified_sources'];self.assertEqual(x['original_source_sha256_verified'],0)
  self.assertIsNone(x['full_event_denominator']);self.assertIsNone(x['full_amendment_denominator'])
 def test_effective_date_contradiction_retained(self):
  x=self.x['verified_sources']
  self.assertEqual(x['official_sutra_effective_metadata_date'],'2026-04-08')
  self.assertEqual(x['computed_effective_date'],'2026-04-09')
  self.assertEqual(x['date_adjudication'],'OPEN')
 def test_no_cross_repo_runtime_or_qa(self):
  x=self.x['software'];self.assertEqual(x['producer_runtime'],'NOT_EXECUTED')
  self.assertEqual(x['cross_repo_rollback'],'NOT_EXECUTED')
  self.assertEqual(x['independent_legal_qa'],'NOT_PERFORMED')
 def test_no_real_publication(self):
  self.assertTrue(all(v is False for v in self.x['limits'].values()))
if __name__=='__main__':unittest.main()
