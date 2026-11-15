import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_hub_export import build_fixture
class HubFixture(unittest.TestCase):
    def test_source_row_contract_shape(self):
        with tempfile.TemporaryDirectory() as t:
            m=build_fixture(t,["mock2","mock1"])
            rows=[json.loads(s) for s in (Path(t)/"sources.jsonl").read_text().splitlines()]
            self.assertEqual(m["files"][0]["record_count"],2)
            self.assertEqual(m["mode"],"test")
            for r in rows:
                self.assertRegex(r["source_id"],r"^src_[0-9a-f]{32}$")
                self.assertTrue(r["synthetic"])
                self.assertEqual(set(["source_id","source_type","source_name","confidence","lineage","synthetic","created_at","extracted_at"])-r.keys(),set())
                self.assertEqual(set(["producer_script","producer_phase","source_inputs"])-r["lineage"].keys(),set())
            self.assertEqual(hashlib.sha256((Path(t)/"sources.jsonl").read_bytes()).hexdigest(),m["files"][0]["sha256"])
    def test_deterministic_order(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            self.assertEqual(build_fixture(a,["y","x"]),build_fixture(b,["x","y"]))
            self.assertEqual((Path(a)/"sources.jsonl").read_bytes(),(Path(b)/"sources.jsonl").read_bytes())
    def test_duplicate_and_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            for refs in (["a","a"],[""],[3]):
                with self.assertRaises(ValueError):build_fixture(t,refs)
    def test_no_real_input_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            m=build_fixture(t,["synthetic"])
            self.assertEqual(m["mode"],"test")
            self.assertNotIn("production",str(m))
if __name__=="__main__":unittest.main()
