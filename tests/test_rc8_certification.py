import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AuditGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/"certification/rc8_audit_only.json").read_text())
        cls.e=json.loads((ROOT/"evidence/2024_manifestation_bindings_rc8.json").read_text())
        cls.h=json.loads((ROOT/"federation.json").read_text())
    def test_certification_must_fail_closed(self):
        for key in ("certified","release_authorized","main_merge_authorized"):
            self.assertFalse(self.d[key])
        self.assertEqual(self.d["classification"],"AUDIT_ONLY")
        self.assertEqual(self.d["production_certification"],"BLOCKED")
    def test_real_data_not_acquired(self):
        self.assertEqual(self.d["source_manifestations_frozen"],0)
        self.assertEqual(self.d["actual_result_pairs"],0)
        self.assertEqual(self.e["official_originals_acquired"],0)
        self.assertIsNone(self.e["identity_findings"]["college_count"])
    def test_registry_noncanonical(self):
        self.assertEqual(self.e["classification"],"CANDIDATE_NOT_IDENTITY")
        self.assertFalse(self.e["reconciliation"]["eligible"])
    def test_public_federation_blocked(self):
        gate=self.h["federation_readiness_gate"]
        self.assertFalse(gate["ready_for_hub_discovery"])
        self.assertFalse(gate["ready_for_hub_live_execution"])
    def test_no_promotions(self):
        for key in ("production_changes","main_mutations","external_referrals","public_alerts"):
            self.assertEqual(self.d[key],0)
if __name__=="__main__":unittest.main()
