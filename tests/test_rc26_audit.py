import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC26AuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=json.loads((ROOT/'certification/rc26_audit_only.json').read_text())
 def test_no_release(self):
  self.assertFalse(self.a['certified'])
  self.assertFalse(self.a['production_authorized'])
  self.assertFalse(self.a['main_merge_authorized'])
 def test_local_source_hash_conservation_but_offdevice_still_open(self):
  x=self.a['source_readback']
  self.assertEqual(x['originals_rehashed_in_RC26_local_container'],14)
  self.assertEqual(x['requested'],15)
  self.assertEqual(x['failed_originals'],1)
  self.assertEqual(x['offdevice_restore'],'NOT_TESTED')
  self.assertIn('NOT_PERFORMED',x['offdevice_permanent_copy'])
 def test_candidate_not_deployed(self):
  x=self.a['location_contract'];self.assertEqual(x['schema_change_upstream'],'NOT_PERFORMED')
  self.assertFalse(x['production_activation'])
  self.assertEqual(x['municipality_geometry'],'UNRESOLVED')
 def test_calendar_and_cybersecurity_unverified(self):
  x=self.a['carry_forward']
  self.assertIsNone(x['event_denominator'])
  self.assertEqual(x['osiPE_test_report'],'OPEN')
  self.assertEqual(x['signed_2028_javaa_rules'],'OPEN')
 def test_no_writes(self):
  self.assertTrue(all(v==0 for v in self.a['safety'].values()))
if __name__=='__main__':unittest.main()
