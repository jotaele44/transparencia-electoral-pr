import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC18Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'certification/rc18_audit_only.json').read_text())
 def test_no_release(self):
  self.assertFalse(self.x['certified'])
  self.assertFalse(self.x['production_approved'])
  self.assertFalse(self.x['main_merge_authorized'])
  self.assertEqual(self.x['classification'],'AUDIT_ONLY')
 def test_no_calendar_or_byte_overclaim(self):
  d=self.x['source_recovery']
  self.assertEqual(d['original_primary_source_sha256_verified'],0)
  self.assertIsNone(d['calendar_full_event_denominator'])
  self.assertEqual(d['official_CEE_hosted_complete_2028_calendar'],'NOT_LOCATED_IN_BOUNDED_SEARCH')
 def test_legal_text_difference_not_violation(self):
  d=self.x['new_discovery']
  self.assertIn('NOT_ENFORCEMENT',d['classification'])
  self.assertIsNone(d['actual_administered_deadline'])
  self.assertIsNone(d['individual_voter_impact'])
 def test_no_external_activation(self):
  for name in ('external_source_polling','external_public_alerts','public_real_case_release','actual_voter_records_processed','production_federation_activation','repository_main_writes'):
   self.assertFalse(self.x['safety'][name])
  self.assertEqual(self.x['software']['cross_repo_runtime'],'NOT_EXECUTED')
if __name__=='__main__':unittest.main()
