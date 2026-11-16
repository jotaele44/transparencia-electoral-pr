import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC15Audit(unittest.TestCase):
 def test_no_release(self):
  d=json.loads((ROOT/'certification/rc15_audit_only.json').read_text())
  self.assertFalse(d['certified'])
  self.assertFalse(d['production_authorized'])
  self.assertEqual(d['classification'],'AUDIT_ONLY')
  self.assertEqual(d['gates']['production'],'BLOCKED')
 def test_real_result_denominator_open(self):
  x=json.loads((ROOT/'certification/rc15_audit_only.json').read_text())['actual_evidence']
  self.assertIsNone(x['full_2024_reporting_unit_denominator'])
  self.assertEqual(x['verified_preliminary_certified_pairs'],0)
  self.assertEqual(x['actual_voting_result_rows_reconciled'],0)
  self.assertEqual(x['new_verified_source_bytes_sha256'],0)
 def test_court_and_disposal_not_overpromoted(self):
  d=json.loads((ROOT/'certification/rc15_audit_only.json').read_text())
  self.assertEqual(d['new_findings'][0]['classification'],'TABLED_AS_LISTED_NOT_PROVEN_APPROVED')
  self.assertEqual(d['new_findings'][-1]['classification'],'TPI_CASE_NUMBER_BOUND_BY_OFFICIAL_APPEAL; ORIGINAL_DOCKET_MISSING')
  self.assertEqual(len(d['source_contradictions']),2)
 def test_federation_still_off(self):
  f=json.loads((ROOT/'federation.json').read_text())['federation_readiness_gate']
  self.assertFalse(f['ready_for_hub_live_execution'])
  self.assertFalse(f['ready_for_hub_discovery'])
if __name__=='__main__':unittest.main()
