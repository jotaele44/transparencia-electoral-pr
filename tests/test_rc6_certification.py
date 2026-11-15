import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.loads((ROOT/"certification/rc6_audit_only.json").read_text())
        cls.f=json.loads((ROOT/"federation.json").read_text())
    def test_certification_fail_closed(self):
        self.assertEqual(self.a["classification"],"AUDIT_ONLY")
        self.assertFalse(self.a["certified"])
        self.assertFalse(self.a["production_release_authorized"])
        self.assertFalse(self.a["main_merge_authorized"])
    def test_material_security_gaps_explicit(self):
        for key in ("actual_identity_provider","immutable_external_storage","real_election_data_production_pipeline","production_certification"):
            self.assertEqual(self.a["critical_gates"][key],"BLOCKED")
    def test_no_real_case_or_alert_claim(self):
        for key in ("source_manifestations_frozen","real_election_case_records_processed","alerts_sent","external_referrals_sent"):
            self.assertEqual(self.a[key],0)
    def test_federation_disabled(self):
        g=self.f["federation_readiness_gate"]
        self.assertFalse(g["ready_for_hub_discovery"])
        self.assertFalse(g["ready_for_hub_live_execution"])
if __name__=="__main__":unittest.main()
