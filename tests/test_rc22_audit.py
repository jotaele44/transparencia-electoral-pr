import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC22Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'certification/rc22_audit_only.json').read_text())
 def test_no_certification(self):
  self.assertFalse(self.x['certified']);self.assertFalse(self.x['production_authorized'])
  self.assertFalse(self.x['main_merge_authorized']);self.assertEqual(self.x['classification'],'AUDIT_ONLY')
 def test_source_gap_closure_not_invented(self):
  d=self.x['new_source_discovery'];self.assertEqual(d['original_source_sha256_count'],0)
  self.assertIsNone(d['full_calendar_event_denominator'])
  self.assertIsNone(d['full_amendment_denominator'])
 def test_no_runtime_claim(self):
  self.assertEqual(self.x['code']['real_producer_runtime'],'NOT_TESTED')
  self.assertEqual(self.x['code']['rollback_scope'],'FIVE_SYNTHETIC_LOCAL_GIT_REPOS')
 def test_safety(self):
  self.assertTrue(all(not v for v in self.x['safety'].values()))
if __name__=='__main__':unittest.main()
