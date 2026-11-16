import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class META2028ReleaseGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=json.loads((ROOT/'certification/meta2028_rc16_audit_only.json').read_text())
 def test_governance(self):
  self.assertEqual(self.a['classification'],'AUDIT_ONLY')
  self.assertFalse(self.a['certified'])
  self.assertFalse(self.a['production_release_authorized'])
  self.assertFalse(self.a['main_merge_authorized'])
 def test_denominator_not_invented(self):
  self.assertEqual(self.a['scope']['historical_weakness_rows'],8)
  self.assertEqual(self.a['scope']['metric_definitions'],8)
  self.assertEqual(self.a['scope']['real_election_results_acquired'],0)
  self.assertEqual(self.a['scope']['original_new_source_bytes_frozen'],0)
  self.assertEqual(len(self.a['scope']['unbound_source_identifiers']),2)
 def test_federation_stays_off(self):
  s=self.a['safety']
  for v in ('automated_complaints','external_alerts','real_case_publication','live_federation','real_election_system_access'):
   self.assertFalse(s[v])
  f=json.loads((ROOT/'federation.json').read_text())['federation_readiness_gate']
  self.assertFalse(f['ready_for_hub_discovery'])
  self.assertFalse(f['ready_for_hub_live_execution'])
 def test_independent_review_not_claimed(self):
  x=self.a['test_evidence']
  self.assertEqual(x['independent_security_qa'],'NOT_PERFORMED')
  self.assertEqual(x['independent_legal_qa'],'NOT_PERFORMED')
 def test_static_preview_only(self):
  p=(ROOT/'public/meta2028/index.html').read_text()
  self.assertIn('OFFLINE SYNTHETIC DEMO',p)
  self.assertNotIn('fetch(',p)
  self.assertIn("script-src 'none'",p)
if __name__=='__main__':unittest.main()
