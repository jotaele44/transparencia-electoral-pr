import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC17AuditGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=json.loads((ROOT/'certification/rc17_meta2028_audit_only.json').read_text())
 def test_certification_blocked(self):
  self.assertFalse(self.a["certified"])
  self.assertFalse(self.a["production_release_authorized"])
  self.assertFalse(self.a["merge_to_main_authorized"])
  self.assertEqual(self.a["classification"],"AUDIT_ONLY")
 def test_source_namespace_closed_but_full_denominator_open(self):
  self.assertEqual(self.a["binding"]["source_locators_resolved"],2)
  self.assertEqual(self.a["binding"]["discovered_event_source_bindings_open"],0)
  self.assertEqual(self.a["binding"]["source_original_bytes_sha256_verified"],0)
  self.assertIsNone(self.a["calendar"]["authoritative_complete_2028_event_denominator"])
 def test_calendar_candidate_not_certified(self):
  self.assertIsNone(self.a["calendar"]["full_signed_cee_calendar_sha256"])
  self.assertFalse(self.a["calendar"]["copy_original_bytes_acquired"])
  self.assertEqual(self.a["calendar"]["official_cee_hosted_equivalence"],"UNVERIFIED")
 def test_not_live(self):
  a=self.a["implementation"]
  self.assertEqual(a["monitor_scope"] if "monitor_scope" in a else self.a["calendar"]["monitor_scope"],"OFFLINE_ONLY")
  self.assertEqual(a["external_alerts"],"DISABLED")
  self.assertEqual(self.a["tests"]["cross_repo_Centinelas_MoneySweep_Spiderweb"],"NOT_TESTED")
if __name__=="__main__":unittest.main()
