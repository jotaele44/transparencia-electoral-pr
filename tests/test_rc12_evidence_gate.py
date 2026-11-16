import sys,unittest
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc12_evidence_gate import verify_manifestation,compare_report_versions,mailing_scenario
def doc(edition,payload):
    return {"source_id":"CEE-SIP-"+edition,"source_epoch":edition,"authority":"CEE_SYNTHETIC",
            "bytes":payload,"sha256":sha256(payload).hexdigest()}
class RC12EvidenceGates(unittest.TestCase):
    def test_exact_bytes_both_versions(self):
        a=compare_report_versions(doc("2025",b"synthetic v1"),doc("2026",b"synthetic v2"))
        self.assertEqual(a["byte_relation"],"DISTINCT_BYTES_LOGICAL_IDENTITY_UNRESOLVED")
        self.assertEqual(a["row_reconciliation"],"BLOCKED")
    def test_byte_identical_does_not_prove_logical_relation(self):
        a=compare_report_versions(doc("2025",b"synthetic"),doc("2026",b"synthetic"))
        self.assertEqual(a["byte_relation"],"BYTE_IDENTICAL")
        self.assertEqual(a["logical_relation"],"UNRESOLVED")
    def test_invalid_hash_rejected(self):
        x=doc("2025",b"synthetic");x["sha256"]="a"*64
        with self.assertRaises(ValueError):verify_manifestation(x)
    def test_without_original_bytes_blocked(self):
        x=doc("2025",b"synthetic");x.pop("bytes")
        with self.assertRaises(ValueError):verify_manifestation(x)
    def test_source_id_collision(self):
        x=doc("2025",b"before");y=doc("2026",b"after");y["source_id"]=x["source_id"]
        with self.assertRaises(ValueError):compare_report_versions(x,y)
    def test_cannot_assert_verified_binding(self):
        with self.assertRaises(ValueError):compare_report_versions(doc("2025",b"a"),doc("2026",b"b"),authoritative_relation={"status":"VERIFIED"})
    def test_binding_date_limits(self):
        x=mailing_scenario(first_mail_date="2028-09-20",last_mail_date="2028-10-03",resolution_binding="CEE-RS-26-010")
        self.assertEqual(x["status"],"SYNTHETIC_COMPLIANT")
    def test_historical_proposed_september_27_fails(self):
        x=mailing_scenario(first_mail_date="2028-09-27",last_mail_date="2028-10-03",resolution_binding="CEE-RS-26-010")
        self.assertIn("START_AFTER_RESOLUTION_DEADLINE",x["findings"])
    def test_late_end_fails(self):
        x=mailing_scenario(first_mail_date="2028-09-20",last_mail_date="2028-10-04",resolution_binding="CEE-RS-26-010")
        self.assertIn("END_AFTER_RESOLUTION_DEADLINE",x["findings"])
    def test_reversed_dates_fails(self):
        x=mailing_scenario(first_mail_date="2028-09-20",last_mail_date="2028-09-19",resolution_binding="CEE-RS-26-010")
        self.assertIn("END_BEFORE_START",x["findings"])
    def test_unbound_resolution_fails(self):
        with self.assertRaises(ValueError):mailing_scenario(first_mail_date="2028-09-20",last_mail_date="2028-10-03",resolution_binding="DRAFT")
if __name__=="__main__":unittest.main()
