import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BranchIncident(unittest.TestCase):
 def test_main_exact_head_recovered(self):
  x=json.loads((ROOT/'evidence/rc11_branch_incident.json').read_text())
  self.assertEqual(x['recovery']['restored_head'],x['baseline_main'])
  self.assertEqual(x['recovery']['verified_main_head'],x['baseline_main'])
  self.assertEqual(x['recovery']['api_result'],'success')
 def test_incident_is_disclosed(self):
  x=json.loads((ROOT/'evidence/rc11_branch_incident.json').read_text())
  self.assertEqual(x['classification'],'RECOVERED_BRANCH_TARGETING_ERROR')
  self.assertEqual(x['scope']['other_files_changed'],0)
  self.assertIn('explicit branch',x['prevention'])
if __name__=='__main__':unittest.main()
