import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC12AuditGate(unittest.TestCase):
 def setUp(self):self.a=json.loads((ROOT/'certification/rc12_audit_only.json').read_text())
 def test_certification_blocked(self):
  self.assertFalse(self.a['certified']);self.assertFalse(self.a['production_authorized']);self.assertEqual(self.a['state'],'AUDIT_ONLY')
 def test_no_fabricated_source_byte_hashes(self):
  x=self.a['source_findings']
  self.assertIsNone(x['cee_rs_26_010']['original_sha256'])
  self.assertIsNone(x['cee_sip_2025_006']['sha256'])
  self.assertIsNone(x['cee_2026_approved_statistical_report']['sha256'])
  self.assertEqual(self.a['test_evidence']['real_original_payload_hashes_verified'],0)
 def test_mailing_date_adjudicated_bounded(self):
  x=self.a['source_findings']['cee_rs_26_010']
  self.assertEqual(x['signed_date'],'2026-09-08')
  self.assertEqual(x['relationship_to_cee_ac_26_149'],'RESOLVES_MAILING_DATE_DISAGREEMENT')
 def test_real_election_denominator_unresolved(self):
  x=self.a['source_findings']
  self.assertIsNone(x['complete_2024_reporting_unit_denominator'])
  self.assertEqual(x['real_vote_comparisons'],0)
if __name__=='__main__':unittest.main()
