import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC23Audit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'certification/rc23_audit_only.json').read_text())
 def test_release_not_authorized(self):
  self.assertFalse(self.x['certified'])
  self.assertFalse(self.x['production_authorized'])
  self.assertFalse(self.x['main_merge_authorized'])
 def test_agreement_is_not_deployment(self):
  x=self.x['primary']
  self.assertTrue(x['unanimous_approval_test_report'])
  self.assertTrue(x['authorized_steps_toward_operation'])
  self.assertFalse(x['actual_deployment_receipt_recovered'])
  self.assertFalse(x['independent_security_QA_recovered'])
 def test_bytes_and_full_denominator_unknown(self):
  self.assertIsNone(self.x['primary']['original_pdf_sha256'])
  self.assertEqual(self.x['additional']['original_primary_sha256_count'],0)
  self.assertIsNone(self.x['additional']['full_event_denominator'])
 def test_real_full_export_and_rollback_not_claimed(self):
  x=self.x['testing']
  self.assertEqual(x['real_full_producer_export'],'NOT_EXECUTED')
  self.assertEqual(x['actual_federation_rollback'],'NOT_EXECUTED')
 def test_safety(self):
  self.assertFalse(any(self.x['safety'].values()))
if __name__=='__main__':unittest.main()
