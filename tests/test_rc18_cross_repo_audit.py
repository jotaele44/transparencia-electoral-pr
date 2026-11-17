import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC18ConsumerSourceBoundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'evidence/rc18_cross_repo_manifest_audit.json').read_text())
 def test_three_distinct_pinned_real_repository_manifests(self):
  self.assertEqual(self.x["consumer_count"],3)
  self.assertEqual(len(self.x["consumers"]),3)
  self.assertEqual(len({c["repo"] for c in self.x["consumers"]}),3)
  for c in self.x["consumers"]:
   self.assertEqual(len(c["commit"]),40);self.assertEqual(len(c["manifest_git_blob_sha1"]),40)
 def test_no_runtime_claim(self):
  self.assertTrue(all(not c["exercised_runtime"] for c in self.x["consumers"]))
  self.assertEqual(self.x["restrictions"]["real_external_runtime_calls"],0)
  self.assertEqual(self.x["restrictions"]["consumer_activation"],0)
 def test_money_not_ready_for_live(self):
  m=next(c for c in self.x["consumers"] if c["repo"].endswith("moneysweep-pr"))
  self.assertFalse(m["ready_for_hub_live_execution"])
 def test_git_blob_not_misreported_sha256(self):
  self.assertTrue(self.x["restrictions"]["manifest_sha1_is_not_sha256"])
  self.assertIn("NOT_RUNTIME",self.x["classification"])
if __name__=="__main__":unittest.main()
