import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_hub_export import build_fixture
class RC19HubFixture(unittest.TestCase):
 def test_three_streams_and_count_closure(self):
  with tempfile.TemporaryDirectory() as t:
   m=build_fixture(t,["mock-2028","mock-2024"])
   self.assertEqual({x["stream"] for x in m["files"]},{"sources","observations","source_monitors"})
   for entry in m["files"]:
    p=Path(t)/entry["filename"]
    rows=[json.loads(x) for x in p.read_text().splitlines()]
    self.assertEqual(len(rows),entry["record_count"])
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),entry["sha256"])
    self.assertTrue(all(row["synthetic"] is True for row in rows))
 def test_monitor_has_no_invented_success_time(self):
  with tempfile.TemporaryDirectory() as t:
   build_fixture(t,["cee-calendar"])
   row=json.loads((Path(t)/"source_monitors.jsonl").read_text())
   self.assertEqual(row["last_success_basis"],"NOT_RECORDED")
   self.assertIsNone(row["last_success_at"])
 def test_deterministic_across_order(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   ma=build_fixture(a,["y","x"]);mb=build_fixture(b,["x","y"])
   self.assertEqual(ma,mb)
   for filename in ("sources.jsonl","observations.jsonl","source_monitors.jsonl","manifest.json"):
    self.assertEqual((Path(a)/filename).read_bytes(),(Path(b)/filename).read_bytes())
 def test_invalid_and_duplicate_refs_fail(self):
  with tempfile.TemporaryDirectory() as t:
   for refs in (["a","a"],[""],[3]):
    with self.assertRaises(ValueError):build_fixture(t,refs)
if __name__=="__main__":unittest.main()
