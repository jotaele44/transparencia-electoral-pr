import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC9Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads((ROOT/"certification/rc9_audit_only.json").read_text())
        cls.federation=json.loads((ROOT/"federation.json").read_text())
    def test_fail_closed(self):
        a=self.audit
        self.assertFalse(a["certified"])
        self.assertEqual(a["classification"],"AUDIT_ONLY")
        self.assertEqual(a["production_state"],"BLOCKED")
    def test_true_source_proof_missing(self):
        self.assertEqual(self.audit["primary_source_payload_sha256_verified"],0)
        self.assertIsNone(self.audit["record_count_denominator"])
        self.assertFalse(self.audit["third_party_csv_bound_to_cee_original"])
    def test_no_invented_outcome(self):
        self.assertEqual(self.audit["real_vote_comparisons_performed"],0)
        self.assertEqual(self.audit["real_vote_discrepancies_proven"],0)
        self.assertEqual(self.audit["disclosures_or_alerts"],0)
    def test_federation_still_off(self):
        g=self.federation["federation_readiness_gate"]
        self.assertFalse(g["ready_for_hub_discovery"])
        self.assertFalse(g["ready_for_hub_live_execution"])
if __name__=="__main__":unittest.main()
