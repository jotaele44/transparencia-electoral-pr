"""Bounded 2028 synthetic publication and review lifecycle matrix (no live feeds)."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from change_monitor import classify,verify_calendar
from integrity_cases import new_case,transition,evidence,verify_event_chain
from rc8_reporting_units import compare
T="2028-11-07T20:00:00Z"
def pub(id="A",version="1",sha="a"*64,at="2028-11-07T20:00:00Z"):
    return {"source_id":"SYNTHETIC_CEE","source_version":version,"publication_kind":"results","record_id":id,"published_at":at,"document_sha256":sha}

class Lifecycle2028(unittest.TestCase):
    def test_normal_identical_publication(self):
        self.assertEqual(classify([pub()],[pub()])["events"][0]["status"],"UNCHANGED")
    def test_corrected_publication_not_fraud(self):
        delta=classify([pub()],[pub(version="2",sha="b"*64)])
        self.assertEqual(delta["events"][0]["status"],"REISSUED_OR_REVISED")
        self.assertNotIn("fraud",str(delta).lower())
    def test_missing_version_not_deletion(self):
        delta=classify([pub()],[])
        self.assertEqual(delta["events"][0]["status"],"MISSING_IN_NEW_SNAPSHOT")
    def test_late_publication_change(self):
        delta=classify([pub()],[pub(at="2028-11-08T01:00:00Z")])
        self.assertEqual(delta["events"][0]["status"],"METADATA_CHANGED")
    def test_two_ballot_unit_sets_distinct(self):
        x=compare([{"PREKEY":"001","UNIKEY":"01","COLKEY":"01"}],
                  [{"PREKEY":"001","UNIKEY":"01","COLKEY":"02"}],ballot="ESTATAL")
        self.assertEqual((x["intersection"],x["a_only"],x["b_only"]),(0,1,1))
        self.assertFalse(x["identity_verified"])
    def test_repeated_publication_identity_rejected(self):
        with self.assertRaises(ValueError):classify([pub(),pub()],[])
    def test_calendar_conflict_preserved(self):
        cal=json.loads((ROOT/"evidence/2028_calendar.json").read_text())
        self.assertTrue(verify_calendar(cal))
        self.assertEqual(cal["contradictions"][0]["source_stated_date"],"2028-06-06")
    def test_false_positive_withdrawal(self):
        c=new_case("simulated-2028-event","RESULT_DISCREPANCY",T,"Publication mismatch under review")
        transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Version candidate")
        transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Synthetic hash",sources=[evidence("synthetic-pdf","a"*64)])
        transition(c,"HUMAN_REVIEWED",actor="analyst",timestamp=T,reason="Independent review",reviewer="reviewer")
        transition(c,"WITHDRAWN",actor="analyst",timestamp=T,reason="Administrative correction explained discrepancy")
        self.assertEqual(c["status"],"WITHDRAWN")
        self.assertTrue(verify_event_chain(c))
        self.assertIsNone(c["referral_receipt"])
    def test_production_disallowed(self):
        with self.assertRaises(PermissionError):new_case("x","RESULT_DISCREPANCY",T,"Live",synthetic=False)
if __name__=="__main__":unittest.main()
