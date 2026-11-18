import json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc20_authority import classify_source,reconcile_effective_date,scope_absentee_guidance,count_source_rows
class RC20Authority(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((ROOT/'evidence/rc20_authority_ledger.json').read_text())
 def test_guide_is_not_calendar(self):
  x=classify_source(self.d["sources"][0]);self.assertEqual(x["type"],"STATISTICAL_GUIDE")
  self.assertFalse(x["may_certify_complete_calendar"])
 def test_original_bytes_not_recovered(self):
  self.assertEqual(self.d["closure"]["original_primary_pdf_hashes_verified"],0)
  self.assertTrue(all(s.get("sha256") is None for s in self.d["sources"]))
 def test_signed_guide_approval_is_distinct_source(self):
  b=self.d['guide_approval_binding']
  self.assertEqual(b['agreement'],'cee_ac_26_112')
  self.assertEqual(b['guide'],'cee_2028_statistical_guide')
  self.assertFalse(b['same_original_file'])
 def test_pdf_and_doc_distinct_originals(self):
  self.assertNotEqual(self.d["sources"][1]["url"],self.d["sources"][2]["url"])
 def test_date_conflict_retained(self):
  x=reconcile_effective_date(indexed_date="2026-04-08",computed_date="2026-04-09")
  self.assertTrue(x["date_conflict"]);self.assertFalse(x["operational_deadline_established"])
 def test_no_auto_legal_certification(self):
  with self.assertRaises(PermissionError):
   reconcile_effective_date(indexed_date="2026-04-08",computed_date="2026-04-09",verified_official_interpretation="2026-04-08")
 def test_no_vote_violation_inferred(self):
  x=scope_absentee_guidance(cee_application_days=45,statutory_application_days=50,federal_transmission_days=45)
  self.assertTrue(x["cee_vs_code_text_difference"])
  self.assertTrue(x["federal_transmission_separate_from_application"])
  self.assertFalse(x["fraud_or_violation_proven"])
 def test_missing_javaa_and_calendar_remain_unknown(self):
  self.assertIsNone(self.d["calendar"]["complete_event_count"])
  self.assertEqual(self.d["sources"][4]["observed_absentee_application_window_days"],45)
 def test_source_count_conserves(self):
  x=count_source_rows(self.d["sources"]);self.assertEqual(x["input_rows"],6)
  self.assertEqual(x["unique_ids"],6);self.assertTrue(x["conserved"])
 def test_duplicate_rejected_to_unresolved(self):
  x=count_source_rows([{"id":"same"},{"id":"same"},{}])
  self.assertEqual((x["unique_ids"],len(x["unresolved_indices"])),(1,2))
 def test_fabricated_hash_rejected(self):
  x=dict(self.d["sources"][1]);x["sha256"]="a"*64
  with self.assertRaises(ValueError):classify_source(x)
if __name__=="__main__":unittest.main()
