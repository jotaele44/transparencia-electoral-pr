import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CalendarCandidateStatus(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((ROOT/'evidence/rc17_calendar_candidates.json').read_text())
  cls.r=json.loads((ROOT/'evidence/meta2028_event_registry.json').read_text())
 def test_no_full_calendar_coverage_claim(self):
  self.assertEqual(self.c["completeness"],"OPEN")
  self.assertIsNone(self.c["closure"]["official_authoritative_denominator"])
  self.assertEqual(self.c["closure"]["proposed_milestones"],len(self.c["candidates"]))
  self.assertIsNone(self.c["final_signed_official_cee_hosted_calendar_original_bytes_sha256"])
 def test_calendar_copy_not_authority_identity(self):
  c=self.r["discovered_calendar_candidate"]
  self.assertEqual(c["certification"],"CANDIDATE_NOT_FULL_AUTHORITY")
  self.assertFalse(c["complete_content_validated"])
  self.assertEqual(c["official_cee_hosted_copy"],"NOT_VERIFIED")
 def test_source_bindings_no_unknown(self):
  events=self.r["events"]; sources={x["source_id"]:x for x in self.r["source_registry"]}
  self.assertEqual((len(events),len(sources)),(4,9))
  for event in events:
   self.assertIn(event["source_id"],sources)
   self.assertEqual(event["source_url"],sources[event["source_id"]]["url"])
 def test_primary_contradiction_not_overwritten(self):
  p=next(x for x in self.c["contradictions"] if x["id"]=="PRIMARY_DATE_RFP")
  self.assertIn("2028-06-06",p["left"])
  self.assertIn("2028-06-04",p["right"])
 def test_later_mailing_calendar_source_needs_scope_review(self):
  p=next(x for x in self.c["contradictions"] if x["id"]=="CALENDAR_VS_RESOLUTION_MAILING")
  self.assertIn("SCOPE_UNRESOLVED",p["adjudication"])
 def test_all_candidates_have_source_epoch_and_status(self):
  ids={x["source_id"] for x in self.c["authorities"]}
  self.assertEqual(len(ids),4)
  self.assertEqual(len({x["id"] for x in self.c["candidates"]}),len(self.c["candidates"]))
  self.assertTrue(all(x["authority_source"] in ids and x["status"] for x in self.c["candidates"]))
 def test_no_original_source_hash(self):
  self.assertTrue(all(x["sha256"] is None for x in self.c["authorities"]))
  self.assertEqual(self.c["closure"]["original_source_bytes_sha256_frozen"],0)
if __name__=="__main__":unittest.main()
