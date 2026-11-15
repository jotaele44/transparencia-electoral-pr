import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from integrity_cases import new_case,transition,evidence,verify_event_chain
class Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority=json.loads((ROOT/"evidence/authority_registry_rc5.json").read_text())
        cls.incident=json.loads((ROOT/"evidence/2024_incident_case_reference.json").read_text())
    def test_statutes_and_authority_roles(self):
        by_id={a["authority_id"]:a for a in self.authority["authorities"]}
        self.assertEqual(by_id["CEE"]["law"],"Ley 58-2020")
        self.assertEqual(by_id["OCE"]["law"],"Ley 222-2011")
        self.assertTrue(all(a["automatic_filing"] is False for a in by_id.values()))
        self.assertTrue(all(a["source_sha256"] is None for a in by_id.values()))
    def test_historical_incident_not_guilt_finding(self):
        self.assertFalse(self.incident["case_instantiated"])
        self.assertIsNone(self.incident["affected_ballot_count"])
        self.assertIsNone(self.incident["certified_results_impact"])
        self.assertEqual(self.incident["culpability"],"UNDETERMINED")
    def test_2028_synthetic_normal_and_false_alarm(self):
        when="2028-11-07T21:00:00Z"
        a=new_case("synthetic-2028-001","RESULT_DISCREPANCY",when,"Late official results-version candidate")
        transition(a,"TRIAGED",actor="review_analyst",timestamp=when,reason="Candidate source version")
        transition(a,"EVIDENCE_VERIFIED",actor="review_analyst",timestamp=when,reason="Synthetic source hash",sources=[evidence("mock-cee-source","b"*64)])
        transition(a,"HUMAN_REVIEWED",actor="review_analyst",reviewer="separate_reviewer",timestamp=when,reason="No supported allegation")
        transition(a,"WITHDRAWN",actor="review_analyst",timestamp=when,reason="False positive resolved")
        self.assertTrue(verify_event_chain(a))
        self.assertEqual(a["status"],"WITHDRAWN")
        self.assertIsNone(a["referral_receipt"])
if __name__=="__main__":unittest.main()
