import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc17_snapshots import (freeze_fixture,compare_snapshots,classify_source_visibility,source_identity_coverage)
URL="https://cee.example.org/docs/calendar.pdf"
def snap(data=b"draft",t="2026-11-16T12:00:00Z",url=URL,source="CEE-MOCK"):
 return freeze_fixture(source_id=source,authority="CEE_MOCK",url=url,received_utc=t,bytes_value=data)
class Snapshots(unittest.TestCase):
 def test_original_bytes_sha(self):
  self.assertEqual(len(snap()["sha256"]),64)
  self.assertFalse(snap()["original_authority_verified"])
 def test_missing_bytes_rejected(self):
  with self.assertRaises(ValueError):freeze_fixture(source_id="A",authority="A",url=URL,received_utc="2026-11-16T12:00:00Z",bytes_value=None)
 def test_non_https_rejected(self):
  with self.assertRaises(ValueError):freeze_fixture(source_id="A",authority="A",url="http://example.org",received_utc="2026-11-16T12:00:00Z",bytes_value=b"x")
 def test_invalid_utc_rejected(self):
  with self.assertRaises(ValueError):snap(t="2026-02-30T12:00:00Z")
 def test_identical_document(self):
  x=compare_snapshots(snap(),snap(t="2026-11-17T12:00:00Z"))
  self.assertEqual(x["classification"],"BYTE_IDENTICAL");self.assertFalse(x["human_review_required"])
 def test_same_url_content_reissue(self):
  x=compare_snapshots(snap(),snap(data=b"amend",t="2026-11-17T12:00:00Z"))
  self.assertEqual(x["classification"],"REISSUED_AT_SAME_URL_CANDIDATE")
  self.assertEqual(x["logical_relation"],"UNRESOLVED")
 def test_moved_same_bytes_not_equivalence_of_source(self):
  x=compare_snapshots(snap(),snap(t="2026-11-17T12:00:00Z",url="https://cee.example.org/new.pdf"))
  self.assertEqual(x["classification"],"BYTE_IDENTICAL")
  self.assertTrue(x["url_changed"])
 def test_moved_changed_bytes(self):
  x=compare_snapshots(snap(),snap(data=b"new",t="2026-11-17T12:00:00Z",url="https://cee.example.org/new.pdf"))
  self.assertEqual(x["classification"],"MOVED_AND_BYTE_CHANGED_CANDIDATE")
 def test_distinct_source_id_blocked(self):
  with self.assertRaises(ValueError):compare_snapshots(snap(),snap(source="another",t="2026-11-17T12:00:00Z"))
 def test_timestamp_backwards_blocked(self):
  with self.assertRaises(ValueError):compare_snapshots(snap(t="2026-11-17T12:00:00Z"),snap(t="2026-11-16T12:00:00Z"))
 def test_fabricated_source_certification_blocked(self):
  s=snap();s["original_authority_verified"]=True
  with self.assertRaises(PermissionError):compare_snapshots(s,s)
 def test_missing_source_not_deletion(self):
  x=classify_source_visibility(snap(),None,searched_coverage={"exhaustive":False})
  self.assertFalse(x["deletion_proven"])
  self.assertEqual(x["search_false_negative"],"OPEN")
 def test_even_certified_search_absence_not_physical_deletion(self):
  x=classify_source_visibility(snap(),None,searched_coverage={"exhaustive":True})
  self.assertFalse(x["deletion_proven"])
 def test_new_registry_two_bindings_closed_only_locally(self):
  reg=json.loads((ROOT/"evidence/meta2028_event_registry.json").read_text())
  x=source_identity_coverage(reg)
  self.assertEqual((x["discovered_source_count"],x["discovered_event_count"]),(9,4))
  self.assertEqual(x["unbound_event_source_ids"],[])
  self.assertIsNone(x["complete_authoritative_event_denominator"])
 def test_duplicate_registry_source_rejected(self):
  reg=json.loads((ROOT/"evidence/meta2028_event_registry.json").read_text())
  reg["source_registry"].append(copy.deepcopy(reg["source_registry"][0]))
  with self.assertRaises(ValueError):source_identity_coverage(reg)
if __name__=="__main__":unittest.main()
