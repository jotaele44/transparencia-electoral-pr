import json,sys,unittest
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc18_publication import intake,classify_incremental,compare_public_information_with_law,same_legal_population
URL="https://www.ceepur.org/test.pdf"
T="2026-11-16T14:00:00Z"
def snap(data=b"%PDF-1.4 synthetic",tm=T,url=URL):
 return intake(source_id="mock",url=url,observed_utc=tm,payload=data,content_type="application/pdf")
class RC18Publication(unittest.TestCase):
 def test_pdf_bytes_are_hashed(self):
  s=snap();self.assertEqual(s["sha256"],sha256(b"%PDF-1.4 synthetic").hexdigest())
  self.assertFalse(s["original_authority_verified"])
 def test_html_masquerading_as_pdf_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url=URL,observed_utc=T,payload=b"<html>fake</html>",content_type="application/pdf")
 def test_missing_bytes_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url=URL,observed_utc=T,payload=b"",content_type="application/pdf")
 def test_oversize_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url=URL,observed_utc=T,payload=b"x"*(40_000_001),content_type="text/plain")
 def test_nonhttps_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url="http://site.com/test.pdf",observed_utc=T,payload=b"%PDF-a",content_type="application/pdf")
 def test_invalid_timestamp_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url=URL,observed_utc="2026-02-30T12:00:00Z",payload=b"%PDF-a",content_type="application/pdf")
 def test_checksum_mismatch_fails(self):
  with self.assertRaises(ValueError):intake(source_id="a",url=URL,observed_utc=T,payload=b"%PDF-a",content_type="application/pdf",declared_sha256="0"*64)
 def test_identical_publication_no_alert(self):
  v=classify_incremental(snap(),snap(tm="2026-11-17T14:00:00Z"))
  self.assertEqual(v["state"],"BYTE_IDENTICAL");self.assertFalse(v["public_alert_allowed"])
 def test_reissue_requires_review(self):
  v=classify_incremental(snap(),snap(data=b"%PDF-1.7 new",tm="2026-11-17T14:00:00Z"))
  self.assertEqual(v["state"],"REISSUED_AT_SAME_URL_CANDIDATE")
  self.assertTrue(v["requires_independent_review"])
  self.assertFalse(v["legal_change_verified"])
 def test_changed_url_classified(self):
  v=classify_incremental(snap(),snap(data=b"%PDF-new",url="https://www.ceepur.org/new.pdf",tm="2026-11-17T14:00:00Z"))
  self.assertEqual(v["state"],"MOVED_AND_BYTE_CHANGED_CANDIDATE")
 def test_absentee_info_conflict_preserved(self):
  c=compare_public_information_with_law(web_claim_days=45,law_claim_days=50,web_source="CEE_JAVAA_PAGE",law_source="OGP_NOV_2026_ART_9_36",modality="ABSENTEE_APPLICATION")
  self.assertTrue(c["stated_deadlines_differ"]);self.assertFalse(c["legal_violation_proven"])
  self.assertIsNone(c["affected_voters"])
 def test_same_deadline_no_difference(self):
  c=compare_public_information_with_law(web_claim_days=50,law_claim_days=50,web_source="w",law_source="l",modality="ADVANCE_APPLICATION")
  self.assertFalse(c["stated_deadlines_differ"])
 def test_bad_modality_fails(self):
  with self.assertRaises(ValueError):compare_public_information_with_law(web_claim_days=45,law_claim_days=50,web_source="w",law_source="l",modality="UNKNOWN")
 def test_advance_and_absentee_separate(self):
  a={"modality":"ADVANCE_MAILING","population":"ADVANCE","source_epoch":"2028"}
  b={"modality":"ABSENTEE_BALLOT_TRANSMISSION","population":"OVERSEAS","source_epoch":"2028"}
  self.assertEqual(same_legal_population(a,b)["state"],"DIFFERENT_SCOPES")
 def test_same_description_not_legal_identity(self):
  a={"modality":"ADVANCE_MAILING","population":"ADVANCE","source_epoch":"2028"}
  self.assertFalse(same_legal_population(a,a)["same_population_proven"])
 def test_evidence_ledger_record_count(self):
  d=json.loads((ROOT/"evidence/rc18_legal_publication_audit.json").read_text())
  self.assertEqual(len(d["sources"]),d["coverage"]["identified_public_sources"])
  self.assertEqual(len(d["observations"]),d["coverage"]["observations"])
  self.assertEqual(d["coverage"]["original_source_byte_sha256_verified"],0)
if __name__=="__main__":unittest.main()
