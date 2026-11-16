import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AuditGate(unittest.TestCase):
 def test_fail_closed(self):
  a=json.loads((ROOT/'certification/rc10_audit_only.json').read_text())
  self.assertEqual(a['classification'],'AUDIT_ONLY');self.assertFalse(a['certified']);self.assertEqual(a['gates']['production'],'BLOCKED')
 def test_denominator_open(self):
  a=json.loads((ROOT/'certification/rc10_audit_only.json').read_text())
  self.assertIsNone(a['evidence']['reporting_unit_denominator']);self.assertEqual(a['evidence']['real_vote_comparisons'],0)
 def test_federation_disabled(self):
  a=json.loads((ROOT/'federation.json').read_text())['federation_readiness_gate']
  self.assertFalse(a['ready_for_hub_live_execution']);self.assertFalse(a['ready_for_hub_discovery'])
if __name__=='__main__':unittest.main()
