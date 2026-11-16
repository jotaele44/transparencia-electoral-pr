import sys,unittest
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc15_custody_gates import classify_decision,verify_precinct_scope,custody_relation,reconcile_ledger
def key(m="Isabela",p="032",u="73",c="01",epoch="2024-certified"):
 return {"municipality_raw":m,"precinct_raw":p,"unit_raw":u,"college_raw":c,"ballot_type":"MUNICIPAL","source_epoch":epoch}
class CustodyGates(unittest.TestCase):
 def test_tabled_no_execution(self):
  x=classify_decision({"state":"TABLED","source_id":"CEE-AC-25-006"})
  self.assertFalse(x["custody_proven"])
 def test_index_only_not_approval(self):
  self.assertFalse(classify_decision({"state":"INDEX_ONLY"})["verified_byte_integrity"])
 def test_approved_requires_bytes(self):
  with self.assertRaises(ValueError):classify_decision({"state":"APPROVED","source_id":"CEE-AC-25-047"})
 def test_digest_mismatch_rejected(self):
  with self.assertRaises(ValueError):classify_decision({"state":"APPROVED","source_bytes":b"data","sha256":"a"*64})
 def test_original_byte_integrity_does_not_prove_custody(self):
  x=classify_decision({"state":"APPROVED","source_bytes":b"synthetic","sha256":sha256(b"synthetic").hexdigest()})
  self.assertFalse(x["custody_proven"])
 def test_execution_requires_independent_receipt(self):
  with self.assertRaises(PermissionError):classify_decision({"state":"EXECUTED","source_bytes":b"synthetic","sha256":sha256(b"synthetic").hexdigest()})
 def test_district_overlap_not_case_identity(self):
  x=custody_relation({"representative_district":"16"},{"representative_district":"16"})
  self.assertEqual(x["reason"],"DISTRICT_OVERLAP_ONLY")
  self.assertFalse(x["execution_proven"])
 def test_lares_cannot_match_isabela(self):
  self.assertFalse(verify_precinct_scope(key("Lares","053"),key())["match"])
 def test_other_epoch_no_automatic_identity(self):
  self.assertFalse(verify_precinct_scope(key(epoch="2024-preliminary"),key())["match"])
 def test_college_04_not_college_01(self):
  self.assertFalse(verify_precinct_scope(key(c="04"),key())["match"])
 def test_raw_073_not_73(self):
  self.assertFalse(verify_precinct_scope(key(u="073"),key())["match"])
 def test_exact_tuple_remains_candidate(self):
  x=verify_precinct_scope(key(),key());self.assertTrue(x["match"])
  self.assertEqual(x["state"],"CANDIDATE_NOT_IDENTITY")
  self.assertFalse(x["custody_proven"])
 def test_malformed_preserved(self):
  x=verify_precinct_scope({"municipality_raw":"Isabela"},key())
  self.assertEqual(x["state"],"UNRESOLVED")
 def test_ledger_duplicate_retained(self):
  x=reconcile_ledger([{"record_id":"a"},{"record_id":"a"},{"record_id":"b"},{}])
  self.assertEqual(x["input_rows"],4);self.assertEqual(x["unique_records"],2)
  self.assertEqual(len(x["unresolved_rows"]),2);self.assertTrue(x["row_conserved"])
if __name__=="__main__":unittest.main()
