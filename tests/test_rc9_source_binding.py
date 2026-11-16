import hashlib,sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc9_source_binding import verify_manifestation,bind_pair,classify_unit,municipal_snapshot
def source(sid="a",payload=b"mock source",geo="MUNICIPALITY"):
    return {"source_id":sid,"authority":"CEE_FIXTURE","source_epoch":"PRELIMINARY","geographic_level":geo,"sha256":hashlib.sha256(payload).hexdigest(),"bytes":payload}
class SourceBinding(unittest.TestCase):
    def test_hash_match(self):self.assertEqual(verify_manifestation(source())["source_id"],"a")
    def test_bad_hash(self):
        x=source();x["bytes"]=b"changed"
        with self.assertRaises(ValueError):verify_manifestation(x)
    def test_no_url_only_identity(self):
        x=source();del x["bytes"]
        with self.assertRaises(ValueError):verify_manifestation(x)
    def test_identical_name_not_binding(self):
        a=source("same",b"a");b=source("same",b"b")
        with self.assertRaises(ValueError):bind_pair(a,b)
    def test_unbound_pair(self):
        self.assertEqual(bind_pair(source(),source("b"))["status"],"UNRESOLVED")
    def test_no_scope_merge(self):
        self.assertEqual(bind_pair(source(),source("b"),official_relation_id="synthetic",scope_verified=False,identity_verified=True)["status"],"CANDIDATE_NOT_IDENTITY")
    def test_geometry_level_rejected(self):
        with self.assertRaises(ValueError):bind_pair(source(),source("b",geo="COLLEGE"),official_relation_id="synthetic",scope_verified=True,identity_verified=True)
    def test_special_modalities(self):
        exp={"72":"EARLY_MAIL","73":"ACCESSIBLE_HOME","74":"JAVAA_SPECIAL_COLLEGE","76":"INCARCERATED","77":"ABSENTEE"}
        for raw,name in exp.items():
            x=classify_unit(raw);self.assertEqual(x["modality"],name);self.assertFalse(x["normal_spatial_college_equivalence"])
    def test_non_special_not_proven_normal(self):
        self.assertIsNone(classify_unit("01")["normal_spatial_college_equivalence"])
    def test_leading_zero_stays_distinct(self):
        self.assertNotEqual(classify_unit("072")["state"],classify_unit("72")["state"])
    def test_municipal_coverage_not_island(self):
        x=municipal_snapshot([{"municipality_id":"fixture_1","reported":40,"total":46}])
        self.assertEqual(x["municipalities"]["fixture_1"]["unreported"],6)
        self.assertFalse(x["islandwide_complete"])
    def test_municipal_duplicate_rejected_and_conserved(self):
        x=municipal_snapshot([{"municipality_id":"x","reported":1,"total":2},{"municipality_id":"x","reported":1,"total":2}])
        self.assertEqual(x["validated_count"]+x["unresolved_count"],2)
    def test_invalid_coverage_quarantined(self):
        x=municipal_snapshot([{"municipality_id":"x","reported":47,"total":46}])
        self.assertEqual(x["unresolved_count"],1)
    def test_official_sources_remain_unfrozen(self):
        m=json.loads((ROOT/"evidence/rc9_official_source_manifest.json").read_text())
        self.assertTrue(all(x["byte_sha256"] is None for x in m["official_manifests"]))
        self.assertEqual(m["source_snapshot_bytes_recovered"],0)
if __name__=="__main__":unittest.main()
