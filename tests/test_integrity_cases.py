import copy
import unittest
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from integrity_cases import new_case,transition,prioritize,evidence,verify_event_chain

T="2026-11-15T11:00:00Z"
EVID=[evidence("CEE-public-pdf","a"*64)]
def case(kind="RESULT_DISCREPANCY"):
    return new_case("fixture-case-001",kind,T,"Published tally version mismatch")

def reviewed(kind="RESULT_DISCREPANCY"):
    c=case(kind)
    transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Scope confirmed")
    transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Primary bytes verified",sources=EVID)
    transition(c,"HUMAN_REVIEWED",actor="analyst",timestamp=T,reason="Separate reviewer reviewed",reviewer="independent-reviewer")
    return c

class IntegrityLifecycle(unittest.TestCase):
    def test_complete_synthetic_case(self):
        c=reviewed()
        transition(c,"REFERRAL_READY",actor="analyst",timestamp=T,reason="Referral draft ready")
        transition(c,"REFERRED",actor="analyst",timestamp=T,reason="Receipt entered after external human submission",authorized_by="compliance-officer",receipt="synthetic-receipt-001")
        transition(c,"OFFICIAL_DISPOSITION",actor="analyst",timestamp=T,reason="Synthetic official response",sources=EVID)
        transition(c,"CLOSED",actor="analyst",timestamp=T,reason="Final review")
        self.assertEqual(c["status"],"CLOSED")
        self.assertEqual(len(c["events"]),7)
        self.assertTrue(verify_event_chain(c))
        self.assertFalse(c["public_release_authorized"])
    def test_no_direct_referral(self):
        with self.assertRaises(ValueError):transition(case(),"REFERRED",actor="analyst",timestamp=T,reason="Skip review",authorized_by="other",receipt="x")
    def test_no_referral_without_review(self):
        c=case()
        transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Triaged")
        transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Evidence",sources=EVID)
        with self.assertRaises(ValueError):transition(c,"REFERRAL_READY",actor="analyst",timestamp=T,reason="Skip review")
    def test_no_uncorroborated_evidence(self):
        c=case()
        transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Triaged")
        with self.assertRaises(ValueError):transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Unverified",sources=[])
    def test_independent_reviewer(self):
        c=case()
        transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Triaged")
        transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Evidence",sources=EVID)
        with self.assertRaises(PermissionError):transition(c,"HUMAN_REVIEWED",actor="analyst",timestamp=T,reason="Own review",reviewer="analyst")
    def test_separate_referral_authorization(self):
        c=reviewed()
        transition(c,"REFERRAL_READY",actor="analyst",timestamp=T,reason="Ready")
        with self.assertRaises(PermissionError):transition(c,"REFERRED",actor="analyst",timestamp=T,reason="Unauthorized",authorized_by="analyst",receipt="receipt")
        with self.assertRaises(PermissionError):transition(c,"REFERRED",actor="analyst",timestamp=T,reason="Wrong reviewer",authorized_by="independent-reviewer",receipt="receipt")
        with self.assertRaises(PermissionError):transition(c,"REFERRED",actor="analyst",timestamp=T,reason="Missing receipt",authorized_by="other")
        self.assertEqual(c["status"],"REFERRAL_READY")
    def test_jurisdiction_review_blocks(self):
        c=reviewed("EQUIPMENT_PROCUREMENT")
        with self.assertRaises(PermissionError):transition(c,"REFERRAL_READY",actor="analyst",timestamp=T,reason="Not adjudicated")
    def test_campaign_finance_routes_to_oce(self):
        self.assertEqual(case("CAMPAIGN_FINANCE")["authority_candidate"],"OCE")
    def test_priority_not_guilt(self):
        x=prioritize(case(),document_discrepancy=True,deadline_proximity=True,impact_scope="MULTI_RECORD")
        self.assertEqual(x["review_priority"],35)
        self.assertIsNone(x["fraud_determination"])
    def test_no_real_cases(self):
        with self.assertRaises(PermissionError):new_case("x","RESULT_DISCREPANCY",T,"Real case",synthetic=False)
    def test_no_accusation(self):
        with self.assertRaises(ValueError):new_case("x","RESULT_DISCREPANCY",T,"Fraud proven")
    def test_privacy_field_fails(self):
        c=case(); c["voter_id"]="123"
        with self.assertRaises(ValueError):transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="No")
    def test_hash_validation(self):
        with self.assertRaises(ValueError):evidence("source","bad")
    def test_duplicate_source_ids(self):
        c=case();transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Triaged")
        with self.assertRaises(ValueError):transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Duplicate",sources=EVID*2)
    def test_event_tampering_detected(self):
        c=reviewed();c["events"][0]["reason"]="altered"
        self.assertFalse(verify_event_chain(c))
    def test_time_regression_rejected(self):
        c=reviewed()
        with self.assertRaises(ValueError):transition(c,"REFERRAL_READY",actor="analyst",timestamp="2026-11-15T10:59:59Z",reason="Backdated")
    def test_withdrawal_preserves_log(self):
        c=case();transition(c,"WITHDRAWN",actor="analyst",timestamp=T,reason="False positive")
        self.assertTrue(verify_event_chain(c));self.assertEqual(c["status"],"WITHDRAWN")
        with self.assertRaises(ValueError):transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Reopen disallowed")
    def test_disposition_requires_document(self):
        c=reviewed();transition(c,"REFERRAL_READY",actor="analyst",timestamp=T,reason="Ready")
        transition(c,"REFERRED",actor="analyst",timestamp=T,reason="External receipt",authorized_by="officer",receipt="synthetic")
        with self.assertRaises(ValueError):transition(c,"OFFICIAL_DISPOSITION",actor="analyst",timestamp=T,reason="Undocumented")
    def test_missing_evidence_cannot_be_manufactured_from_secondary(self):
        c=case(); transition(c,"TRIAGED",actor="analyst",timestamp=T,reason="Triaged")
        secondary=[evidence("news","b"*64,"INDEPENDENT_CORROBORATION")]
        with self.assertRaises(ValueError):transition(c,"EVIDENCE_VERIFIED",actor="analyst",timestamp=T,reason="Secondary only",sources=secondary)
if __name__=="__main__":unittest.main()
