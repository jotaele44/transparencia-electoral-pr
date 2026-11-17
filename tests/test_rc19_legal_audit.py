import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC19LegalAudit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.x=json.loads((ROOT/"certification/rc19_audit_only.json").read_text())
  cls.s=json.loads((ROOT/"evidence/rc19_primary_source_register.json").read_text())
 def test_legal_article_mapping(self):
  d=self.x["law39"]
  self.assertEqual(d["section45_amends_old_article"],"9.35")
  self.assertEqual(d["section45_deadline_days"],50)
  self.assertEqual(d["section49_renumbers_old_9_35_to"],"9.36")
  self.assertEqual(d["current_deadline_citation"],"9.36(5)")
 def test_45_and_50_are_distinct_obligations(self):
  d=self.x["conflict"]
  self.assertEqual(d["cee_public_page_days"],45)
  self.assertEqual(d["current_code_days"],50)
  self.assertTrue(d["application_deadline_is_not_transmission_deadline"])
  self.assertFalse(d["statutory_violation_proven"])
 def test_original_law_bytes_not_fabricated(self):
  d=next(x for x in self.s["sources"] if x["id"]=="sutra_ley39_original")
  self.assertFalse(d["bytes_acquired"])
  self.assertIsNone(d["sha256"])
 def test_2024_rule_not_promoted_to_2028(self):
  self.assertEqual(self.x["javaa"]["2024_regulation_as_2028_authority"],"NOT_ESTABLISHED")
  self.assertEqual(self.x["javaa"]["2028_operative_instructions"],"NOT_LOCATED_IN_BOUNDED_SEARCH")
 def test_official_resolution_not_full_calendar(self):
  self.assertTrue(self.x["calendar"]["official_cee_resolution"])
  self.assertFalse(self.x["calendar"]["full_official_cee_calendar"])
  self.assertIsNone(self.x["calendar"]["complete_event_denominator"])
 def test_no_release(self):
  self.assertFalse(self.x["certified"])
  self.assertFalse(self.x["production_approved"])
  self.assertFalse(self.x["main_merge_authorized"])
if __name__=="__main__":unittest.main()
