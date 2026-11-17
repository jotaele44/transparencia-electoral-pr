import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC19Contract(unittest.TestCase):
 def test_contract_is_fail_closed(self):
  d=json.loads((ROOT/"contracts/rc19_http_readonly_contract.json").read_text())
  self.assertEqual(d["method"],"GET")
  self.assertEqual(d["redirect_policy"],"BLOCK")
  for key in ("write","alert","publish","enforce","schedule"):
   self.assertFalse(d["side_effects"][key])
 def test_source_hash_denominator_open(self):
  d=json.loads((ROOT/"evidence/rc19_primary_source_register.json").read_text())
  self.assertEqual(d["coverage"]["source_records"],9)
  self.assertEqual(d["coverage"]["original_bytes_acquired"],0)
  self.assertEqual(d["coverage"]["sha256_frozen"],0)
if __name__=="__main__":unittest.main()
