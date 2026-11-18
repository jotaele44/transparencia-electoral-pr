import copy,json,sys,unittest
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from rc25_primary_calendar import first_sunday_june,classify_primary_date,review_frozen_members
class RC25PrimaryCalendar(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((ROOT/"evidence/rc24_primary_evidence_ledger.json").read_text())
  cls.round2=json.loads((ROOT/"evidence/rc24_acquisition_round2.json").read_text())
 def test_first_sunday_2028_is_june_4(self):
  self.assertEqual(first_sunday_june(2028).isoformat(),"2028-06-04")
  self.assertEqual(first_sunday_june(2028).weekday(),6)
 def test_raw_cee_rfp_june_6_is_tuesday(self):
  x=classify_primary_date(source_date="2028-06-06",year=2028,source_class="PROCUREMENT_RFP_CONTEXT",legal_rule_text="FIRST_SUNDAY_JUNE")
  self.assertEqual(x["raw_weekday"],"TUESDAY")
  self.assertEqual(x["statutory_derived_candidate"],"2028-06-04")
  self.assertTrue(x["source_conflict"])
  self.assertFalse(x["operative_date_certified"])
 def test_raw_rfp_preserved_unmodified(self):
  row=next(x for x in self.d["calendar_events"] if x["event_id"]=="PR2028_PRIMARY")
  self.assertEqual(row["date"],"2028-06-06")
  self.assertEqual(row["raw_source_date"],"2028-06-06")
  self.assertNotEqual(row["classification"],"FACT")
  self.assertFalse(row["operative_date_verified"])
 def test_date_conflict_not_silent_and_denominator_open(self):
  x=self.d["calendar_primary_date_adjudication"]
  self.assertEqual(x["status"],"SOURCE_CONTRADICTION")
  self.assertFalse(x["operative_date_certified"])
  self.assertFalse(x["official_complete_calendar_bound"])
  self.assertIsNone(self.d["calendar_denominators"]["complete_official_calendar_rows"])
 def test_date_matches_statutory_candidate_still_no_official_certification(self):
  x=classify_primary_date(source_date="2028-06-04",year=2028,source_class="PROCUREMENT_RFP_CONTEXT",legal_rule_text="FIRST_SUNDAY_JUNE")
  self.assertFalse(x["source_conflict"])
  self.assertFalse(x["operative_date_certified"])
 def test_wrong_source_type_blocked(self):
  with self.assertRaises(ValueError):classify_primary_date(source_date="2028-06-06",year=2028,source_class="OFFICIAL_CERTIFIED_CALENDAR",legal_rule_text="FIRST_SUNDAY_JUNE")
 def test_false_rule_binding_blocked(self):
  with self.assertRaises(ValueError):classify_primary_date(source_date="2028-06-06",year=2028,source_class="PROCUREMENT_RFP_CONTEXT",legal_rule_text="NEAREST_SUNDAY")
 def test_impossible_date_blocked(self):
  with self.assertRaises(ValueError):classify_primary_date(source_date="2028-06-32",year=2028,source_class="PROCUREMENT_RFP_CONTEXT",legal_rule_text="FIRST_SUNDAY_JUNE")
 def test_year_mismatch_blocked(self):
  with self.assertRaises(ValueError):classify_primary_date(source_date="2028-06-06",year=2026,source_class="PROCUREMENT_RFP_CONTEXT",legal_rule_text="FIRST_SUNDAY_JUNE")
 def test_round2_manifest_count_conservation(self):
  v=review_frozen_members(self.round2)
  self.assertEqual(v["listed_source_manifestations"],14)
  self.assertTrue(v["counts_closed"])
  self.assertFalse(v["original_bytes_independently_rehashed_by_this_function"])
 def test_duplicate_source_fails(self):
  v=copy.deepcopy(self.round2)
  v["sources"][1]["id"]=v["sources"][0]["id"]
  with self.assertRaises(ValueError):review_frozen_members(v)
 def test_missing_source_fails(self):
  v=copy.deepcopy(self.round2);v["sources"].pop()
  with self.assertRaises(ValueError):review_frozen_members(v)
 def test_forged_digest_fails(self):
  v=copy.deepcopy(self.round2);v["sources"][0]["sha256"]="N"*64
  with self.assertRaises(ValueError):review_frozen_members(v)
 def test_original_law_source_hash_preserved(self):
  files={x["id"]:x for x in self.round2["sources"]}
  self.assertEqual(files["LEY39-SUTRA-PDF"]["sha256"],"167bb21cc824ffcff256713cc4f3c640baa381b29c8f55c0074dbdd1df811f00")
  self.assertEqual(files["LEY39-SUTRA-DOC"]["sha256"],"fb414ae1a184c81902d58d285c61034f24f378cd0900df9241ba8ed18904a7ae")
if __name__=="__main__":unittest.main()
