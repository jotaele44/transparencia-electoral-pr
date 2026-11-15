import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_security import AUDIENCE,synthetic_token,verify_token,require_distinct_principals,public_envelope,verified_evidence_manifest,route
from rc6_evidence_store import build_chain,verify_chain,write_once,verify_snapshot
from rc6_legal_route import assess_route
KEY=b"x"*40
NOW=1794740000
def principal(name,role):
    return verify_token(synthetic_token({"sub":name,"role":role,"iss":"synthetic-rc6-idp","aud":AUDIENCE,"iat":NOW-60,"exp":NOW+60},KEY),KEY,now=NOW)
def envelope():
    return {"case_id":"synthetic-01","domain":"RESULT_DISCREPANCY","status":"DETECTED","source_count":0,"review_state":"OPEN","synthetic":True,"classification":"UNKNOWN"}
def entries():
    return [{"event_id":"a","event_type":"CREATED","synthetic":True},{"event_id":"b","event_type":"TRIAGED","synthetic":True}]
class SecurityGates(unittest.TestCase):
    def test_verified_fixture(self):self.assertEqual(principal("person-a","analyst").role,"analyst")
    def test_hmac_tampering(self):
        t=synthetic_token({"sub":"a","role":"analyst","iss":"synthetic-rc6-idp","aud":AUDIENCE,"iat":NOW-60,"exp":NOW+60},KEY)
        t["claims"]["role"]="reviewer"
        with self.assertRaises(PermissionError):verify_token(t,KEY,now=NOW)
    def test_expired_token(self):
        t=synthetic_token({"sub":"a","role":"analyst","iss":"synthetic-rc6-idp","aud":AUDIENCE,"iat":NOW-100,"exp":NOW-1},KEY)
        with self.assertRaises(PermissionError):verify_token(t,KEY,now=NOW)
    def test_wrong_audience(self):
        t=synthetic_token({"sub":"a","role":"analyst","iss":"synthetic-rc6-idp","aud":"other","iat":NOW-60,"exp":NOW+60},KEY)
        with self.assertRaises(PermissionError):verify_token(t,KEY,now=NOW)
    def test_weak_key(self):
        with self.assertRaises(ValueError):synthetic_token({},b"bad")
    def test_role_separation(self):self.assertTrue(require_distinct_principals(principal("a","analyst"),principal("b","reviewer"),principal("c","release_officer")))
    def test_same_subject_separation(self):
        with self.assertRaises(PermissionError):require_distinct_principals(principal("a","analyst"),principal("a","reviewer"),principal("c","release_officer"))
    def test_wrong_role(self):
        with self.assertRaises(PermissionError):require_distinct_principals(principal("a","reviewer"),principal("b","reviewer"),principal("c","release_officer"))
    def test_public_allowlist(self):self.assertEqual(public_envelope(envelope()),envelope())
    def test_private_field_rejected(self):
        a=envelope();a["voter_name"]="Test Person"
        with self.assertRaises(ValueError):public_envelope(a)
    def test_free_text_field_rejected(self):
        a=envelope();a["description"]="personal contact"
        with self.assertRaises(ValueError):public_envelope(a)
    def test_real_case_rejected(self):
        a=envelope();a["synthetic"]=False
        with self.assertRaises(PermissionError):public_envelope(a)
    def test_invalid_source_hash(self):
        with self.assertRaises(ValueError):verified_evidence_manifest([{"source_id":"mock","sha256":"bad","synthetic":True}])
    def test_duplicate_source(self):
        a={"source_id":"s","sha256":"a"*64,"synthetic":True}
        with self.assertRaises(ValueError):verified_evidence_manifest([a,a])
    def test_manifest_deterministic(self):
        a={"source_id":"a","sha256":"a"*64,"synthetic":True}
        b={"source_id":"b","sha256":"b"*64,"synthetic":True}
        self.assertEqual(verified_evidence_manifest([a,b])["manifest_sha256"],verified_evidence_manifest([b,a])["manifest_sha256"])
    def test_default_legal_route_unresolved(self):self.assertEqual(route("EQUIPMENT_PROCUREMENT"),"JURISDICTION_REVIEW_REQUIRED")
    def test_legal_screen_requires_standing(self):
        result=assess_route(domain="RESULT_DISCREPANCY",source_ids=["s"],legal_basis_verified=True,standing_reviewed=False,deadline_reviewed=True,analyst=principal("a","analyst"),reviewer=principal("b","reviewer"))
        self.assertFalse(result["eligible_for_draft_referral"])
    def test_complete_screen_still_no_submission(self):
        result=assess_route(domain="CAMPAIGN_FINANCE",source_ids=["s"],legal_basis_verified=True,standing_reviewed=True,deadline_reviewed=True,analyst=principal("a","analyst"),reviewer=principal("b","reviewer"))
        self.assertEqual(result["suggested_authority"],"OCE")
        self.assertTrue(result["eligible_for_draft_referral"])
        self.assertFalse(result["submission_authorized"])
    def test_chain_detection(self):
        c=build_chain(entries());self.assertTrue(verify_chain(c,expected_tip=c[-1]["digest"],expected_count=2))
        c[0]["event_type"]="WITHDRAWN"
        self.assertFalse(verify_chain(c))
    def test_truncation_detected_with_anchor(self):
        c=build_chain(entries());self.assertFalse(verify_chain(c[:-1],expected_tip=c[-1]["digest"],expected_count=2))
    def test_duplicate_event_rejected(self):
        with self.assertRaises(ValueError):build_chain([entries()[0],entries()[0]])
    def test_write_once(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"events.json";chain=build_chain(entries());digest=write_once(p,chain)
            self.assertTrue(verify_snapshot(p,digest))
            with self.assertRaises(FileExistsError):write_once(p,chain)
    def test_snapshot_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"events.json";digest=write_once(p,build_chain(entries()))
            p.write_text(p.read_text().replace("TRIAGED","WITHDRAWN"))
            self.assertFalse(verify_snapshot(p,digest))
    def test_unknown_authority(self):
        r=assess_route(domain="OTHER",source_ids=["s"],legal_basis_verified=True,standing_reviewed=True,deadline_reviewed=True,analyst=principal("a","analyst"),reviewer=principal("b","reviewer"))
        self.assertFalse(r["eligible_for_draft_referral"])
if __name__=="__main__":unittest.main()
