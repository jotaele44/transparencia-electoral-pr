import hashlib,importlib.util,json,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_rc26_archived_sources import verify_archive
class ArchiveVerifier(unittest.TestCase):
 def _zip(self,folder,mutate=None):
  p=Path(folder)/"source.zip"
  data=b"synthetic original"
  row={"id":"MOCK-1","status":"ACQUIRED","bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"path":"artifacts/rc24/raw/MOCK-1.pdf"}
  m={"counts":{"requested":2,"acquired":1,"failed":1,"blocked":0},
     "sources":[row,{"id":"MISSING-2","status":"FAILED","bytes":None,"sha256":None,"path":None}]}
  if mutate:mutate(m)
  with zipfile.ZipFile(p,"w") as z:
   z.writestr("source_manifest.json",json.dumps(m))
   z.writestr("raw/MOCK-1.pdf",data)
  return p,hashlib.sha256(p.read_bytes()).hexdigest()
 def test_synthetic_readback_pass_without_remote_claim(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d);x=verify_archive(p,h)
   self.assertEqual(x["originals_rehashed"],1)
   self.assertFalse(x["independent_offdevice_recovery_pass"])
 def test_outer_checksum_falsification_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d)
   with self.assertRaises(ValueError):verify_archive(p,"0"*64)
 def test_forged_member_digest_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d,lambda m:m["sources"][0].update(sha256="0"*64))
   with self.assertRaises(ValueError):verify_archive(p,h)
 def test_record_count_corruption_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d,lambda m:m["counts"].update(requested=4))
   with self.assertRaises(ValueError):verify_archive(p,h)
 def test_duplicate_source_identity_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d,lambda m:m["sources"][1].update(id="MOCK-1"))
   with self.assertRaises(ValueError):verify_archive(p,h)
 def test_forged_missing_source_digest_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d,lambda m:m["sources"][1].update(sha256="0"*64))
   with self.assertRaises(ValueError):verify_archive(p,h)
 def test_archive_path_traversal_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,h=self._zip(d)
   with zipfile.ZipFile(p,"a") as z:z.writestr("../outside","danger")
   h=hashlib.sha256(p.read_bytes()).hexdigest()
   with self.assertRaises(ValueError):verify_archive(p,h)
if __name__=="__main__":unittest.main()
