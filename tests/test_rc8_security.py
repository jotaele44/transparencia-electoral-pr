import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_security import VerifiedPrincipal
from rc7_guards import build_checkpoint
from rc8_replay import consume,count
from rc8_anchor import anchor_once,verify_anchor
PRINCIPAL=VerifiedPrincipal("synthetic-analyst","analyst","synthetic-rc6-idp",5000)
NONCE="unique-safe-nonce-001"

class DurableReplayTests(unittest.TestCase):
    def test_persists_across_connections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"nonce.db"
            args=dict(action="triage",case_id="case1",nonce=NONCE,now=4000)
            consume(path,PRINCIPAL,**args)
            self.assertEqual(count(path),1)
            with self.assertRaises(PermissionError):
                consume(path,PRINCIPAL,**args)
            self.assertEqual(count(path),1)
    def test_replay_different_action_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"nonce.db"
            consume(db,PRINCIPAL,action="triage",case_id="case1",nonce=NONCE,now=4000)
            other=VerifiedPrincipal("synthetic-analyst","reviewer","synthetic-rc6-idp",5000)
            with self.assertRaises(PermissionError):
                consume(db,other,action="review",case_id="case1",nonce=NONCE,now=4000)
    def test_same_subject_nonce_cannot_reuse_across_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"nonce.db"
            consume(db,PRINCIPAL,action="triage",case_id="case1",nonce=NONCE,now=4000)
            changed=VerifiedPrincipal(PRINCIPAL.subject,"reviewer",PRINCIPAL.issuer,5000)
            with self.assertRaises(PermissionError):
                consume(db,changed,action="review",case_id="case1",nonce=NONCE,now=4000)
    def test_expired_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):
                consume(Path(tmp)/"nonce.db",PRINCIPAL,action="triage",case_id="case1",nonce=NONCE,now=5000)
    def test_wrong_issuer_and_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"nonce.db"
            for bad in (VerifiedPrincipal("person","analyst","untrusted",5000),VerifiedPrincipal("person","release_officer","synthetic-rc6-idp",5000)):
                with self.assertRaises(PermissionError):
                    consume(path,bad,action="triage",case_id="case1",nonce=NONCE,now=4000)
    def test_malformed_nonce(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                consume(Path(tmp)/"nonce.db",PRINCIPAL,action="triage",case_id="case1",nonce="x",now=4000)
    def test_two_connections_same_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"nonce.db"
            con1=sqlite3.connect(path,isolation_level=None)
            con2=sqlite3.connect(path,isolation_level=None)
            try:
                con1.execute("CREATE TABLE used_nonces (issuer TEXT, subject TEXT, case_id TEXT, nonce TEXT, action TEXT, expires_at INTEGER, PRIMARY KEY(issuer,subject,case_id,nonce))")
                con1.execute("BEGIN IMMEDIATE")
                con1.execute("INSERT INTO used_nonces VALUES (?,?,?,?,?,?)",("synthetic-rc6-idp","synthetic-analyst","case1",NONCE,"triage",5000))
                con1.commit()
                with self.assertRaises(PermissionError):
                    consume(path,PRINCIPAL,action="triage",case_id="case1",nonce=NONCE,now=4000)
            finally:
                con1.close();con2.close()
    def test_untrusted_principal_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):
                consume(Path(tmp)/"nonce.db","analyst",action="triage",case_id="case1",nonce=NONCE,now=4000)

class AnchoringTests(unittest.TestCase):
    def test_receipt_and_reject_rewrite(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=1)
        with tempfile.TemporaryDirectory() as tmp:
            receipt=anchor_once(tmp,c)
            self.assertTrue(verify_anchor(receipt["receipt_file"],receipt["receipt_sha256"],c))
            with self.assertRaises(FileExistsError):
                anchor_once(tmp,c)
            c2=build_checkpoint(snapshot_sha256="c"*64,chain_tip="b"*64,sequence=1)
            self.assertFalse(verify_anchor(receipt["receipt_file"],receipt["receipt_sha256"],c2))
    def test_truncation_and_rollback(self):
        c=build_checkpoint(snapshot_sha256="a"*64,chain_tip="b"*64,sequence=2)
        with tempfile.TemporaryDirectory() as tmp:
            receipt=anchor_once(tmp,c)
            self.assertFalse(verify_anchor(receipt["receipt_file"],receipt["receipt_sha256"],c,minimum_sequence=3))
            Path(receipt["receipt_file"]).write_bytes(b"")
            self.assertFalse(verify_anchor(receipt["receipt_file"],receipt["receipt_sha256"],c))
if __name__=="__main__":
    unittest.main()
