import sys,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_security import VerifiedPrincipal
from rc7_guards import authorize,build_checkpoint,verify_checkpoint
P=VerifiedPrincipal("analyst-1","analyst","synthetic-rc6-idp",2000)
class RC7Guards(unittest.TestCase):
    def test_authorized_synthetic(self):
        x=set();out=authorize(P,"triage",case_id="synthetic-1",now=1000,used_nonces=x,nonce="uniquenonce000001")
        self.assertEqual(out["authentication"],"SYNTHETIC_FIXTURE_ONLY")
    def test_replay_fails(self):
        x=set();args=dict(case_id="case",now=1000,used_nonces=x,nonce="uniquenonce000001")
        authorize(P,"triage",**args)
        with self.assertRaises(PermissionError):authorize(P,"triage",**args)
    def test_role_escalation_fails(self):
        with self.assertRaises(PermissionError):authorize(P,"approve_draft",case_id="case",now=1000,used_nonces=set(),nonce="uniquenonce000001")
    def test_expiration_fails(self):
        with self.assertRaises(PermissionError):authorize(P,"triage",case_id="case",now=2000,used_nonces=set(),nonce="uniquenonce000001")
    def test_short_nonce_fails(self):
        with self.assertRaises(ValueError):authorize(P,"triage",case_id="case",now=1000,used_nonces=set(),nonce="x")
    def test_valid_external_checkpoint(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=3)
        self.assertTrue(verify_checkpoint(c,trusted_external_digest=c["checkpoint_sha256"],minimum_sequence=3))
    def test_local_rewrite_fails_external_anchor(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=3)
        anchor=c["checkpoint_sha256"]
        altered=build_checkpoint(snapshot_sha256="c"*64,chain_tip="b"*64,sequence=3)
        self.assertFalse(verify_checkpoint(altered,trusted_external_digest=anchor))
    def test_sequence_rollback_fails(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=2)
        self.assertFalse(verify_checkpoint(c,trusted_external_digest=c["checkpoint_sha256"],minimum_sequence=3))
    def test_fake_anchor_fails(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=2)
        self.assertFalse(verify_checkpoint(c,trusted_external_digest="0"*64))
    def test_malformed_checkpoint_fails(self):
        self.assertFalse(verify_checkpoint({"sequence":2},trusted_external_digest="0"*64))
    def test_unauthenticated_fails(self):
        with self.assertRaises(PermissionError):authorize("analyst","triage",case_id="case",now=1000,used_nonces=set(),nonce="uniquenonce000001")
if __name__=="__main__":unittest.main()
