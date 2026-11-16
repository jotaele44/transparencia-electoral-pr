import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC13AuditTest(unittest.TestCase):
 def setUp(self):self.a=json.loads((ROOT/'certification/rc13_audit_only.json').read_text())
 def test_release_blocked(self):
  self.assertFalse(self.a['certified']);self.assertFalse(self.a['production_authorized'])
  self.assertEqual(self.a['classification'],'AUDIT_ONLY')
 def test_source_payloads_not_fabricated(self):
  e=self.a['evidence'];self.assertIsNone(e['delivery_payload_sha256'])
  self.assertIsNone(e['approved_2026_original_sha256'])
  self.assertEqual(e['original_report_bytes_verified'],0)
 def test_no_premature_denominator_or_vote_findings(self):
  e=self.a['evidence'];self.assertIsNone(e['complete_reporting_unit_denominator'])
  self.assertEqual(e['authentic_preliminary_certified_pairs'],0)
  self.assertEqual(e['real_votes_reconciled'],0)
 def test_hub_live_disabled(self):
  g=json.loads((ROOT/'federation.json').read_text())['federation_readiness_gate']
  self.assertFalse(g['ready_for_hub_live_execution'])
  self.assertFalse(g['ready_for_hub_discovery'])
if __name__=='__main__':unittest.main()
