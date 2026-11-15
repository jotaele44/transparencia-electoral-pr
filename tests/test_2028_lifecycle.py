import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from change_monitor import classify

def row(n="A",v="v1",digest="a"*64,published="2028-05-01T10:00:00Z"):
    return {"source_id":"CEE-FIXTURE","record_id":n,"source_version":v,"publication_kind":"notice","published_at":published,"document_sha256":digest}

class ElectoralSimulation(unittest.TestCase):
    def test_simulated_publication_lifecycle(self):
        stages=[[],[row()],[row()],[row(v="v2",digest="b"*64)],[row(v="v2",digest="b"*64),row(n="B")],[row(n="B")]]
        expected=["NEW_RECORD","UNCHANGED","REISSUED_OR_REVISED","UNCHANGED","MISSING_IN_NEW_SNAPSHOT"]
        for i in range(len(stages)-1):
            result=classify(stages[i],stages[i+1]);statuses={tuple(e["identity"]):e["status"] for e in result["events"]}
            self.assertIn(expected[i],statuses.values())
            self.assertEqual(result["union_count"],result["intersection_count"]+result["symmetric_difference_count"])
            self.assertEqual(result["before_count"]+result["after_count"],2*result["intersection_count"]+result["symmetric_difference_count"])
    def test_reissue_not_interpreted_as_fraud(self):
        result=classify([row()],[row(v="v2",digest="b"*64)])
        self.assertNotIn("FRAUD",str(result).upper())
        self.assertEqual(result["certification"],"PROVISIONAL")
    def test_missing_not_authorized_deletion(self):
        result=classify([row()],[])
        self.assertEqual(result["events"][0]["status"],"MISSING_IN_NEW_SNAPSHOT")
        self.assertIsNone(result["events"][0]["after"])
if __name__=="__main__":unittest.main()
