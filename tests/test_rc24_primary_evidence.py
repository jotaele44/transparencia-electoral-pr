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
 def test_calendar_identity_consistent(self):
  s={r["id"]:r for r in self.x["source_records"]}["CEE-AC-26-149"]
  self.assertEqual(s["raw_index_title"],"CALENDARIO ELECTORAL 2028")
  self.assertEqual(s["raw_page1_subject"],"CALENDARIO ELECTORAL 2028")
  self.assertNotIn("contradiction",s)
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
 def test_law_effectivity_uses_exclusive_first_day_rule(self):
  x=self.x["legal"]
  self.assertEqual(x["ley39_signed_and_approved_date"],"2026-03-10")
  self.assertEqual(x["effectivity_clause"],"Section 69: 30 days after approval")
  self.assertIn("exclude first day",x["counting_rule"])
  self.assertEqual(x["computed_effective_date"],"2026-04-09")
  from datetime import date,timedelta
  self.assertEqual(date(2026,3,10)+timedelta(days=30),date(2026,4,9))
  self.assertEqual(x["sutra_index_date"],"2026-04-08")
  self.assertTrue(x["raw_contradiction_preserved"])
  self.assertEqual(x["independent_legal_review"],"OPEN")
 def test_committee_evaluation_chain_is_not_the_report_itself(self):
  rows={r["id"]:r for r in self.x["source_records"]}
  self.assertIn("three representatives",rows["CEE-AC-25-009"]["known_fact"])
  self.assertIn("unanimously adopted",rows["CEE-AC-25-031"]["known_fact"])
  self.assertIn("not attached",rows["CEE-AC-25-031"]["missing"])
  self.assertIn("remained usable",rows["CEE-AC-25-037-APPROVED-MINUTES"]["known_fact"])
  self.assertIn("do not substitute",rows["CEE-AC-25-037-APPROVED-MINUTES"]["scope_limit"].casefold())
 def test_source_ids_unique_and_urls_official(self):
  ids=[r["id"] for r in self.x["source_records"]]
  self.assertEqual(len(ids),len(set(ids)))
  for r in self.x["source_records"]:
   self.assertTrue(r["url"].startswith("https://"))
   self.assertIn(r["url"].split("/")[2],("www.ceepur.org","ceepur.org","ww2.ceepur.org","sutra.oslpr.org","senado.pr.gov","bvirtualogp.pr.gov"))
 def test_no_false_hashes_or_certification(self):
  self.assertEqual(self.x["source_freeze"]["raw_original_bytes_sha256_verified"],14)
  self.assertEqual(self.x["source_freeze"]["round1"]["acquired"],13)
  self.assertEqual(self.x["source_freeze"]["round2"]["acquired"],14)
  self.assertEqual(self.x["source_freeze"]["round2"]["failed"],1)
  self.assertIsNone(next(r for r in self.x["source_records"] if r["id"]=="OGP_CIVIL_CODE_55_2020").get("sha256"))
  self.assertEqual(self.x["source_freeze"]["round1"]["acquired"],13)
  self.assertEqual(self.x["certification"],"AUDIT_ONLY")
  self.assertFalse(self.x["safety"]["real_voter_data_processed"])
  self.assertFalse(self.x["safety"]["autonomous_enforcement"])
 def test_acquisition_round_manifests_close(self):
  r1=json.loads((ROOT/"evidence/rc24_acquisition_round1.json").read_text())
  r2=json.loads((ROOT/"evidence/rc24_acquisition_round2.json").read_text())
  self.assertEqual((r1["counts"]["requested"],r1["counts"]["acquired"]),(13,13))
  self.assertEqual((r2["counts"]["requested"],r2["counts"]["acquired"],r2["counts"]["failed"]),(15,14,1))
  failed=next(r for r in r2["failed"] if r["id"]=="OGP-CIVIL-CODE-55-2020")
  self.assertIsNone(failed["sha256"])
  self.assertTrue(all(len(r["sha256"])==64 for r in r2["sources"]))
  law={r["id"]:r for r in r2["sources"]}
  self.assertNotEqual(law["LEY39-SUTRA-PDF"]["sha256"],law["LEY39-SUTRA-DOC"]["sha256"])
if __name__=="__main__":unittest.main()
