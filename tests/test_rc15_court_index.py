import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC15CourtCase(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((ROOT/"evidence/rc15_court_record_index.json").read_text())
  cls.s=json.loads((ROOT/"evidence/rc15_primary_discovery.json").read_text())
 def test_docket_identity_and_outcome(self):
  self.assertEqual(self.c["trial_case"],"SJ2025CV01115")
  self.assertEqual(self.c["appeal_case"],"KLAN202500306")
  self.assertEqual(self.c["appellate_disposition"],"CERTIORARI_GRANTED_TRIAL_JUDGMENT_AFFIRMED")
 def test_source_date_conflict_retained(self):
  x=next(x for x in self.c["document_references"] if x["record"]=="CEE dismissal motion")
  self.assertEqual(x["date_as_printed_in_appellate_text"],"2024-02-24")
  self.assertIn("CONTRADICTION",x["temporal_validity"])
 def test_original_appendices_not_claimed(self):
  self.assertEqual(len(self.c["document_references"]),9)
  self.assertTrue(all(not x["original_obtained"] and x["sha256"] is None for x in self.c["document_references"]))
 def test_separate_lares_docket(self):
  self.assertEqual(self.c["related_case"]["identity"],"DISTINCT_CASE_NOT_ISABELA")
 def test_custody_sources_not_promoted(self):
  a={x["id"]:x for x in self.s["sources"]}
  self.assertEqual(a["cee_ac_25_006"]["observed_state"],"TABLED_AS_LISTED")
  self.assertIsNone(a["cee_ac_25_006"]["approved"])
  self.assertIsNone(a["cee_ac_25_047"]["executed"])
 def test_ledger_count_and_unknown_denominator(self):
  self.assertEqual(len(self.s["sources"]),self.s["closure"]["registered_source_rows"])
  self.assertEqual(len({x["id"] for x in self.s["sources"]}),self.s["closure"]["registered_unique_source_ids"])
  self.assertIsNone(self.s["closure"]["complete_reporting_unit_denominator"])
 def test_no_unsupported_case_finding(self):
  self.assertIsNone(self.c["ballot_evidence"]["maletin_destroyed"])
  self.assertIsNone(self.c["ballot_evidence"]["valid_uncounted_ballots"])
if __name__=="__main__":unittest.main()
