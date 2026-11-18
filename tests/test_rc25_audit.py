import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC25Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((ROOT/'certification/rc25_audit_only.json').read_text())
 def test_no_release(self):
  self.assertEqual(self.d['state'],'AUDIT_ONLY')
  self.assertFalse(self.d['certified']);self.assertFalse(self.d['production_authorized'])
  self.assertFalse(self.d['main_merge_authorized'])
 def test_prior_source_manifest_not_new_hash_proof(self):
  x=self.d['evidence_reuse']
  self.assertEqual(x['round2_originals_acquired'],14)
  self.assertFalse(x['current_run_original_bytes_rehashed'])
  self.assertEqual(x['permanent_offdevice_archival'],'NOT_VERIFIED')
 def test_previously_incorrect_primary_date_reclassified(self):
  x=self.d['date_contradictions'][0]
  self.assertEqual(x['raw_date'],'2028-06-06')
  self.assertEqual(x['statutory_computed_date'],'2028-06-04')
  self.assertIn('NOT_OPERATIVE_DATE_VERIFIED',x['resolution'])
 def test_important_real_consumer_failure_preserved(self):
  self.assertEqual(self.d['carry_forward']['centinelas_location_versus_hub_schema'],'OPEN_BLOCKER')
  self.assertEqual(self.d['carry_forward']['moneysweep_source_monitor_stream'],'BLOCKED_BY_PINNED_CONTRACT')
  self.assertEqual(self.d['carry_forward']['real_cross_repo_rollback'],'NOT_EXECUTED')
 def test_safety(self):
  self.assertTrue(all(v==0 for v in self.d['safety'].values()))
if __name__=='__main__':unittest.main()
