import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC24PrimaryEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/"evidence/rc24_primary_evidence_ledger.json").read_text())
 def test_calendar_dates_and_scope(self):
  rows={r["event_id"]:r for r in self.x["calendar_events"]}
  self.assertEqual(rows["PR2028_GENERAL"]["date"],"2028-11-07")
  self.assertEqual(rows["PR2028_PRIMARY"]["date"],"2028-06-06")
  self.assertEqual(rows["PR2028_ADVANCE_APPLICATION_DEADLINE"]["date"],"2028-09-18")
  self.assertEqual(rows["PR2028_ADVANCE_MAIL_DISPATCH_START_LIMIT"]["date"],"2028-09-20")
  self.assertEqual(rows["PR2028_ADVANCE_MAIL_DISPATCH_END_LIMIT"]["date"],"2028-10-03")
  self.assertEqual(self.x["calendar_denominators"]["identified_event_rows"],7)
  self.assertIsNone(self.x["calendar_denominators"]["complete_official_calendar_rows"])
 def test_uocava_and_domestic_deadlines_separate(self):
  rows={r["event_id"]:r for r in self.x["calendar_events"]}
  self.assertEqual(rows["PR2028_UOCAVA_45_DAY_DATE"]["date"],"2028-09-23")
  self.assertNotEqual(rows["PR2028_UOCAVA_45_DAY_DATE"]["date"],rows["PR2028_ADVANCE_APPLICATION_DEADLINE"]["date"])
 def test_calendar_identity_contradiction_preserved(self):
  s={r["id"]:r for r in self.x["source_records"]}["CEE-AC-26-149"]
  self.assertEqual(s["raw_index_title"],"CALENDARIO ELECTORAL 2028")
  self.assertEqual(s["raw_page1_subject"],"CALENDARIO ELECTORAL 2026")
  self.assertEqual(s["contradiction"],"INDEX_TITLE_2028_VS_INTERNAL_SUBJECT_2026")
  self.assertEqual(s["identity"],"NOT_THE_COMPLETE_CALENDAR")
 def test_eRE_schedule_not_eJAVAA_deployment(self):
  s={r["id"]:r for r in self.x["source_records"]}["CEE-AC-25-112"]
  self.assertIn("eRE",s["known_fact"])
  self.assertIn("NOT PROOF OF eJAVAA DEPLOYMENT",s["scope_limit"])
 def test_cee_110_not_deployment_proof(self):
  g=self.x["eRE_eJAVAA_release_gates"]
  self.assertEqual(g["osiPE_original_test_report"],"OPEN")
  self.assertEqual(g["system_build_and_release_id"],"OPEN")
  self.assertEqual(g["actual_deployment_and_acceptance"],"OPEN")
  self.assertEqual(g["independent_cybersecurity_assessment"],"OPEN")
 def test_law_signing_not_effective_date(self):
  x=self.x["legal"]
  self.assertEqual(x["ley39_signed_date"],"2026-03-10")
  self.assertEqual(x["effective_date"],"UNRESOLVED")
  self.assertTrue(x["raw_contradiction_preserved"])
 def test_source_ids_unique_and_urls_official(self):
  ids=[r["id"] for r in self.x["source_records"]]
  self.assertEqual(len(ids),len(set(ids)))
  for r in self.x["source_records"]:
   self.assertTrue(r["url"].startswith("https://"))
   self.assertIn(r["url"].split("/")[2],("www.ceepur.org","ceepur.org","ww2.ceepur.org","sutra.oslpr.org","senado.pr.gov"))
 def test_no_false_hashes_or_certification(self):
  self.assertEqual(self.x["source_freeze"]["raw_original_bytes_sha256_verified"],0)
  self.assertEqual(self.x["certification"],"AUDIT_ONLY")
  self.assertFalse(self.x["safety"]["real_voter_data_processed"])
  self.assertFalse(self.x["safety"]["autonomous_enforcement"])
if __name__=="__main__":unittest.main()
