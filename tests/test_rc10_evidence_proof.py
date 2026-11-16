import hashlib,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc10_evidence_proof import reconcile,verify_manifestations,KEY
def manifest(v,blob):
    return {"version_id":v,"source_epoch":v,"authority":"CEE_FIXTURE_ONLY","source_bytes":blob,
            "manifestation_sha256":hashlib.sha256(blob).hexdigest(),"synthetic":True}
A=manifest("pre",b"synthetic pre payload")
B=manifest("cert",b"synthetic certified payload")
BIND={"binding_status":"PRIMARY_SOURCE_LINK_PENDING"}
def row(v,unit="001",votes=10):
    return {"election_id":"2024","contest_id":"mayor","source_reporting_unit_id":unit,"candidate_id":"CAND-01",
            "vote_method":"in_person","votes":votes,"version_id":v,"synthetic":True}
def k(unit="001"):
    return ("2024","mayor",unit,"CAND-01","in_person")
class EvidenceProofGates(unittest.TestCase):
    def test_complete_two_rows(self):
        r=reconcile([A,B],[row("pre")],[row("cert")],independent_source_binding=BIND,expected_keys=[k()])
        self.assertEqual((r["intersection"],r["union"],r["different_value"]),(1,1,0))
        self.assertEqual(r["authoritative_pair_identity"],"UNRESOLVED")
    def test_changed_votes_not_fraud(self):
        r=reconcile([A,B],[row("pre")],[row("cert",votes=20)],independent_source_binding=BIND)
        self.assertEqual(r["different_value"],1)
        self.assertFalse(r["actual_election_discrepancy_proven"])
    def test_left_right_count_conservation(self):
        r=reconcile([A,B],[row("pre","001"),row("pre","002")],[row("cert","002"),row("cert","003")],independent_source_binding=BIND)
        self.assertEqual((r["intersection"],r["left_only"],r["right_only"],r["union"],r["symmetric_difference"]),(1,1,1,3,2))
    def test_absent_is_not_zero(self):
        r=reconcile([A,B],[row("pre")],[],independent_source_binding=BIND)
        self.assertEqual(r["left_only"],1);self.assertEqual(r["different_value"],0)
    def test_unresolved_duplicate_kept(self):
        r=reconcile([A,B],[row("pre"),row("pre")],[],independent_source_binding=BIND)
        self.assertEqual((r["left_rows"],r["left_keyed"],len(r["left_unresolved"])),(2,1,1))
        self.assertEqual(r["row_conservation"],"UNRESOLVED_ROWS_PRESERVED")
    def test_malformed_boolean_not_votes(self):
        r=reconcile([A,B],[row("pre",votes=True)],[],independent_source_binding=BIND)
        self.assertEqual(r["left_unresolved"][0]["reason"],"INVALID_VOTE_COUNT")
    def test_source_bytes_tampering_fails(self):
        bad={**A,"source_bytes":b"modified"}
        with self.assertRaises(ValueError):reconcile([bad,B],[],[],independent_source_binding=BIND)
    def test_authority_mismatch_fails(self):
        bad={**B,"authority":"OTHER"}
        with self.assertRaises(ValueError):reconcile([A,bad],[],[],independent_source_binding=BIND)
    def test_real_sources_fail_closed(self):
        bad={**A,"synthetic":False}
        with self.assertRaises(PermissionError):reconcile([bad,B],[],[],independent_source_binding=BIND)
    def test_unverified_binding_cannot_pass(self):
        with self.assertRaises(PermissionError):reconcile([A,B],[],[],independent_source_binding={"binding_status":"VERIFIED"})
    def test_source_id_never_from_name_nearness(self):
        r=reconcile([A,B],[row("pre","01")],[row("cert","001")],independent_source_binding=BIND)
        self.assertEqual(r["intersection"],0)
    def test_expected_denominator_not_source_authority(self):
        r=reconcile([A,B],[row("pre")],[],independent_source_binding=BIND,expected_keys=[k(),k("002")])
        self.assertEqual(r["denominator"]["missing_expected"],1)
        self.assertEqual(r["denominator"]["state"],"FIXTURE_ONLY_INTERNAL_CHECK")
    def test_expected_duplicate_fail(self):
        with self.assertRaises(ValueError):reconcile([A,B],[],[],expected_keys=[k(),k()],independent_source_binding=BIND)
if __name__=="__main__":unittest.main()
