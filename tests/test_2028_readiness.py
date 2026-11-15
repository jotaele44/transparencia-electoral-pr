import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from change_monitor import classify,verify_calendar

def entry(version="v1",sha="a"*64,record="CEE-RS-26-010",pub="2026-09-08"):
    return {"source_id":"cee","source_version":version,"publication_kind":"resolution","record_id":record,"published_at":pub,"document_sha256":sha}

class ReadinessTests(unittest.TestCase):
    def test_calendar_rule_and_unresolved_conflict(self):
        data=json.loads((ROOT/"evidence/2028_calendar.json").read_text())
        self.assertTrue(verify_calendar(data))
        self.assertEqual(data["contradictions"][0]["disposition"],"SOURCE_CONTRADICTION_RETAINED_LEGAL_RULE_ADJUDICATED")
    def test_silent_resolution_fails(self):
        data=json.loads((ROOT/"evidence/2028_calendar.json").read_text())
        data["events"][1]["legal_status"]="RESOLVED"
        with self.assertRaises(ValueError):verify_calendar(data)
    def test_unchanged(self):self.assertEqual(classify([entry()],[entry()])["events"][0]["status"],"UNCHANGED")
    def test_revision(self):self.assertEqual(classify([entry()],[entry("v2","b"*64)])["events"][0]["status"],"REISSUED_OR_REVISED")
    def test_missing_not_deletion(self):self.assertEqual(classify([entry()],[])["events"][0]["status"],"MISSING_IN_NEW_SNAPSHOT")
    def test_new(self):self.assertEqual(classify([],[entry()])["events"][0]["status"],"NEW_RECORD")
    def test_metadata_change(self):self.assertEqual(classify([entry()],[entry(pub="2026-09-09")])["events"][0]["status"],"METADATA_CHANGED")
    def test_duplicate_fails(self):
        with self.assertRaises(ValueError):classify([entry(),entry()],[])
    def test_invalid_hash_fails(self):
        with self.assertRaises(ValueError):classify([entry(sha="bad")],[])
    def test_no_false_merge(self):
        result=classify([entry(record="001")],[entry(record="01")]);self.assertEqual(result["symmetric_difference_count"],2)
    def test_count_conservation(self):
        r=classify([entry(record="1"),entry(record="2")],[entry(record="2"),entry(record="3")]);self.assertEqual((r["before_count"],r["after_count"],r["union_count"],r["intersection_count"],r["symmetric_difference_count"]),(2,2,3,1,2))
if __name__=="__main__":unittest.main()
