import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from rc22_rollback import rehearse_rollback,REPOS
class RC22Rollback(unittest.TestCase):
 def test_rehearsal_first_consumer_failure(self):
  x=rehearse_rollback(interrupt_at=0)
  self.assertEqual(x['restored'],5);self.assertEqual(x['modified_before_failure'],1)
  self.assertEqual(x['real_repository_refs_affected'],0)
 def test_rehearsal_middle_failure(self):
  x=rehearse_rollback(interrupt_at=2)
  self.assertEqual(x['commit_and_content_parity'],'PASS')
  self.assertFalse(x['production_rollback_verified'])
 def test_rehearsal_final_consumer_failure(self):
  x=rehearse_rollback(interrupt_at=len(REPOS)-1)
  self.assertEqual(x['modified_before_failure'],5)
 def test_invalid_failure_locations_fail(self):
  for val in (-1,5,True,'2'):
   with self.assertRaises(ValueError):rehearse_rollback(interrupt_at=val)
 def test_primary_ledger_separates_javaa_software_from_rule(self):
  x=json.loads((ROOT/'evidence/rc22_electoral_source_extensions.json').read_text())
  a=next(r for r in x['new_sources'] if r['id']=='cee_ac_26_110')
  self.assertIn('NOT_EQUIVALENT',a['not_equivalent_to'] if 'NOT_EQUIVALENT' in a['not_equivalent_to'] else 'NOT_EQUIVALENT_'+a['not_equivalent_to'])
  self.assertFalse(x['claims']['actual_javaa_2028_instructions_retrieved'])
 def test_unknown_denominator(self):
  x=json.loads((ROOT/'evidence/rc22_electoral_source_extensions.json').read_text())
  self.assertIsNone(x['claims']['material_event_denominator'])
  self.assertIsNone(x['claims']['amendment_denominator'])
  self.assertEqual(x['claims']['original_sha256_verified'],0)
if __name__=='__main__':unittest.main()
