import sys,unittest
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc13_primary_gates import require_manifestation,compare_report_manifestations,reconcile_unit_keys
def doc(epoch,payload):
 return {"source_id":"cee-"+epoch,"authority":"CEE_SYNTHETIC","source_epoch":epoch,"source_url":"https://example.org/test.pdf",
         "original_bytes":payload,"sha256":sha256(payload).hexdigest()}
def unit(epoch,unit_id="73",ballot="MUNICIPAL"):
 return {"source_epoch":epoch,"municipality_raw":"ISABELA","precinct_raw":"032","unit_raw":unit_id,"college_raw":"001","ballot_type":ballot}
class RC13Gates(unittest.TestCase):
 def test_2025_completion_not_delivered_file(self):
  with self.assertRaises(ValueError):require_manifestation({"source_id":"CEE-SIP-2025-006","completion":"2025-03-28"})
 def test_payload_match_is_only_byte_match(self):
  x=compare_report_manifestations(doc("2025",b"synthetic"),doc("2026",b"synthetic"))
  self.assertEqual(x["source_version_relation"],"BYTE_IDENTICAL")
  self.assertEqual(x["logical_relation"],"UNRESOLVED")
 def test_differing_payload_remains_unresolved(self):
  x=compare_report_manifestations(doc("2025",b"one"),doc("2026",b"two"))
  self.assertEqual(x["source_version_relation"],"BYTE_DIFFERENT")
  self.assertEqual(x["real_result_comparison"],"BLOCKED")
 def test_checksum_rejection(self):
  x=doc("2025",b"raw");x["sha256"]="f"*64
  with self.assertRaises(ValueError):require_manifestation(x)
 def test_unverifiable_crosswalk_not_canonical(self):
  x=compare_report_manifestations(doc("2025",b"one"),doc("2026",b"two"),authoritative_crosswalk=doc("crosswalk",b"fixture"))
  self.assertEqual(x["logical_relation"],"CANDIDATE_NOT_IDENTITY")
 def test_no_name_only_cross_epoch_merge(self):
  x=reconcile_unit_keys([unit("2024-11-06")],[unit("2024-12-31")],ballot_type="MUNICIPAL")
  self.assertEqual(x["intersection"],0)
  self.assertEqual(x["symmetric_difference"],2)
  self.assertTrue(x["counts_close"])
 def test_no_unit_normalization(self):
  x=reconcile_unit_keys([unit("same","073")],[unit("same","73")],ballot_type="MUNICIPAL")
  self.assertEqual(x["intersection"],0)
 def test_duplicate_preserved_as_unresolved(self):
  x=reconcile_unit_keys([unit("same"),unit("same")],[],ballot_type="MUNICIPAL")
  self.assertEqual(x["left_keyed"],1)
  self.assertEqual(x["left_unresolved"][0]["reason"],"DUPLICATE_KEY")
  self.assertTrue(x["counts_close"])
 def test_invalid_scope_preserved(self):
  x=reconcile_unit_keys([unit("same",ballot="ESTATAL")],[],ballot_type="MUNICIPAL")
  self.assertEqual(x["left_unresolved"][0]["reason"],"BALLOT_SCOPE_CONFLICT")
 def test_missing_keys_preserved(self):
  x=reconcile_unit_keys([{}],[],ballot_type="MUNICIPAL")
  self.assertEqual(x["left_unresolved"][0]["reason"],"MISSING_FIELDS")
 def test_unverified_unit_crosswalk_rejected(self):
  with self.assertRaises(PermissionError):reconcile_unit_keys([],[],ballot_type="MUNICIPAL",authoritative_unit_map={})
 def test_denominator_stays_null(self):
  x=reconcile_unit_keys([unit("same")],[unit("same")],ballot_type="MUNICIPAL")
  self.assertIsNone(x["official_denominator"])
  self.assertEqual(x["certification"],"UNRESOLVED")
if __name__=="__main__":unittest.main()
