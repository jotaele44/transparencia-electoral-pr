import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC7Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=json.loads((ROOT/"certification/rc7_audit_only.json").read_text())
    def test_no_promotion(self):
        d=self.d;self.assertEqual(d["state"],"AUDIT_ONLY")
        self.assertFalse(d["production_deployment"]);self.assertFalse(d["main_merge_authorized"])
        self.assertFalse(d["federation_activated"])
    def test_unverified_sources_not_certified(self):
        self.assertEqual(self.d["source_payloads_frozen"],0)
        self.assertEqual(self.d["scopes"]["denominator"],"UNRESOLVED")
        self.assertEqual(self.d["scopes"]["actual_vote_reconciliation"],"NOT_ATTEMPTED")
    def test_external_cases_zero(self):
        for k in ("real_cases_processed","external_referrals","public_accusations","alerts_sent"):
            self.assertEqual(self.d[k],0)
    def test_auth_and_storage_not_misrepresented(self):
        self.assertEqual(self.d["scopes"]["anti_replay"],"IN_MEMORY_SYNTHETIC_ONLY")
        self.assertEqual(self.d["scopes"]["external_checkpoint"],"PURE_VERIFIER_NO_EXTERNAL_ANCHOR_OR_STORAGE")
if __name__=="__main__":unittest.main()
