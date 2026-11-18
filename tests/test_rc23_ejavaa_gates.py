import json,sys,unittest
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc23_ejavaa_gates import classify_commission_agreement,release_gate,source_identity
class RC23EvidenceGates(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/"evidence/rc23_ejavaa_original_agreement.json").read_text())
 def test_agreement_scope_accurate(self):
  x=classify_commission_agreement(self.x["primary"][0])
  self.assertTrue(x["authorized_to_pursue_operation"])
  self.assertFalse(x["actual_deployment_verified"])
  self.assertFalse(x["test_report_content_verified"])
 def test_test_report_does_not_exist_in_one_page(self):
  a=self.x["primary"][0]
  self.assertEqual(a["pages"],1)
  self.assertFalse(a["source_doc_contains_test_results"])
  self.assertFalse(a["source_doc_contains_work_schedule"])
 def test_original_law_and_agreement_bytes_not_claimed(self):
  self.assertTrue(all(r.get("sha256") is None for r in self.x["primary"]))
  self.assertEqual(self.x["closure"]["original_source_bytes_sha256_verified"],0)
 def test_all_gate_rows_close(self):
  x=release_gate(self.x["required_ejavaa_release_evidence"])
  self.assertEqual((x["required"],x["passed_source_integrity_and_review"]),(6,0))
  self.assertFalse(x["production_release_approved"])
 def test_missing_required_gate_rejected(self):
  with self.assertRaises(ValueError):release_gate(self.x["required_ejavaa_release_evidence"][:-1])
 def test_duplicate_gate_rejected(self):
  rows=self.x["required_ejavaa_release_evidence"][:]
  with self.assertRaises(ValueError):release_gate(rows+[rows[0]])
 def test_unsupported_pass_without_bytes_denied(self):
  rows=[dict(r) for r in self.x["required_ejavaa_release_evidence"]]
  rows[0]["state"]="PASS"
  with self.assertRaises(ValueError):release_gate(rows)
 def test_synthetic_integrity_not_production_release(self):
  rows=[dict(r) for r in self.x["required_ejavaa_release_evidence"]]
  rows[0].update(state="PASS",original_source_bytes=b"fixture",sha256=sha256(b"fixture").hexdigest(),independent_review_receipt="synthetic-fixture")
  self.assertFalse(release_gate(rows)["production_release_approved"])
 def test_approval_and_test_report_not_same_original(self):
  self.assertFalse(source_identity({"id":"agreement","url":"https://cee.example/approval.pdf"},{"id":"test","url":"https://cee.example/report.pdf"})["same_original_source_proven"])
 def test_equal_url_not_original_source_proof(self):
  s={"id":"CEE","url":"https://cee.example/x.pdf"}
  self.assertFalse(source_identity(s,s)["same_original_source_proven"])
 def test_cee_ac_26_204_scope_unresolved(self):
  x=self.x["primary"][1];self.assertFalse(x["signed_content_verified"]);self.assertFalse(x["actual_destruction_executed"])
 def test_amendment_denominator_unknown(self):
  self.assertIsNone(self.x["legal"]["amendment_denominator"])
if __name__=="__main__":unittest.main()
