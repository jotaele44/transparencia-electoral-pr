import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc19_legal_dates import days_before,first_sunday_of_june,build_2028_deadline_matrix,compare_cee_absentee_page_to_current_code,compare_mail_timeline
class RC19LegalDates(unittest.TestCase):
 def test_first_sunday_june_2028(self):self.assertEqual(first_sunday_of_june(2028),"2028-06-04")
 def test_general_election_50_day_deadline(self):
  d=build_2028_deadline_matrix()
  self.assertEqual(d["absentee_application"]["date"],"2028-09-18")
  self.assertEqual(d["advance_application"]["date"],"2028-09-18")
 def test_uocava_45_day_date_is_separate(self):
  d=build_2028_deadline_matrix()
  self.assertEqual(d["uocava_transmission"]["date"],"2028-09-23")
  self.assertIn("NOT_APPLICATION",d["uocava_transmission"]["classification"])
 def test_cee_advance_mail_window(self):
  d=build_2028_deadline_matrix()
  self.assertEqual(d["cee_advance_mail_start"]["date"],"2028-09-20")
  self.assertEqual(d["cee_advance_mail_completion"]["date"],"2028-10-03")
 def test_javaa_30_day_processing_start(self):
  self.assertEqual(build_2028_deadline_matrix()["javaa_processing"]["date"],"2028-10-08")
 def test_primary_rfp_conflict_preserved(self):
  x=build_2028_deadline_matrix()["primary_date_conflict"]
  self.assertEqual(x["cee_rfp_date"],"2028-06-06")
  self.assertEqual(x["statutory_computed_date"],"2028-06-04")
  self.assertEqual(x["state"],"UNRESOLVED_SOURCE_DATE_CONTRADICTION")
  self.assertFalse(x["legal_violation_proven"])
 def test_cee_absentee_webpage_mismatch(self):
  x=compare_cee_absentee_page_to_current_code()
  self.assertEqual(x["cee_page_claim"]["days"],45)
  self.assertEqual(x["current_code"]["days"],50)
  self.assertEqual(x["current_code"]["article"],"9.36(5)")
  self.assertTrue(x["findings"]["absentee_page_article_reference_stale"])
  self.assertFalse(x["findings"]["statutory_violation_proven"])
 def test_advance_article_renumbering(self):
  x=compare_cee_absentee_page_to_current_code()
  self.assertEqual(x["cee_advance_page_claim"]["article"],"9.38(4)")
  self.assertEqual(x["current_advance_code"]["article"],"9.39(5)")
  self.assertTrue(x["findings"]["advance_page_article_reference_stale"])
 def test_uocava_not_general_absentee_application(self):
  x=compare_cee_absentee_page_to_current_code()
  self.assertTrue(x["findings"]["uocava_45_day_rule_is_not_the_general_absentee_application_deadline"])
  self.assertIsNone(x["findings"]["actual_cee_administered_deadline"])
 def test_mail_timeline_does_not_false_merge(self):
  x=compare_mail_timeline()
  self.assertFalse(x["same_modality"])
  self.assertFalse(x["same_legal_population"])
  self.assertFalse(x["direct_contradiction_established"])
 def test_invalid_date_and_days_fail(self):
  with self.assertRaises(ValueError):days_before("2028-02-30",50)
  with self.assertRaises(ValueError):days_before("2028-11-07",True)
if __name__=="__main__":unittest.main()
