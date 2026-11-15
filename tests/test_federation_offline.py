import json,sys,tempfile,hashlib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from export_dry_run import generate

class FederationOfflineTests(unittest.TestCase):
    def test_export_manifest_hash_and_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            m=generate([{"id":"source-b","synthetic":True},{"id":"source-a","synthetic":True}],tmp)
            self.assertEqual(m["files"][0]["record_count"],2)
            self.assertEqual(hashlib.sha256((Path(tmp)/"sources.jsonl").read_bytes()).hexdigest(),m["files"][0]["sha256"])
            self.assertEqual(len((Path(tmp)/"sources.jsonl").read_text().splitlines()),2)
            self.assertEqual(m["federation"]["hub_parent"],"thehub-pr")
            self.assertEqual(m["mode"],"test")
            self.assertRegex(m["package_id"],r"^pkg_[a-f0-9]{32}$")
    def test_escaped_newline_does_not_corrupt_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {"id":"a","synthetic":True,"note":"line 1\\nline 2","literal":"\\\\n"}
            generate([payload],tmp)
            lines=(Path(tmp)/"sources.jsonl").read_text().splitlines()
            self.assertEqual(len(lines),1)
            self.assertEqual(json.loads(lines[0]),payload)
    def test_empty_package_count_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=generate([],tmp)
            self.assertEqual(manifest["files"][0]["record_count"],0)
            self.assertEqual((Path(tmp)/"sources.jsonl").read_bytes(),b"")
    def test_order_independent_manifest(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            x={"id":"a","synthetic":True};y={"id":"b","synthetic":True}
            self.assertEqual(generate([x,y],a)["package_id"],generate([y,x],b)["package_id"])
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):generate([{"id":"a","synthetic":True},{"id":"a","synthetic":True}],tmp)
    def test_real_rows_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):generate([{"id":"a","synthetic":False}],tmp)
    def test_production_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):generate([],tmp,test_only=False)
    def test_discovery_and_live_disabled(self):
        g=json.loads((ROOT/"federation.json").read_text())["federation_readiness_gate"]
        self.assertFalse(g["ready_for_hub_discovery"]);self.assertFalse(g["ready_for_hub_live_execution"])
if __name__=="__main__":unittest.main()
