import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc9_source_binding import municipal_snapshot
class Excerpts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=json.loads((ROOT/"evidence/rc9_municipal_snapshot_candidates.json").read_text())
    def test_source_reported_arithmetic(self):
        rows=[{"municipality_id":x["municipality_raw"],"reported":x["reported_colleges"],"total":x["total_colleges"]} for x in self.d["rows"]]
        computed=municipal_snapshot(rows)
        self.assertEqual(computed["validated_count"],2)
        for x in self.d["rows"]:
            self.assertEqual(computed["municipalities"][x["municipality_raw"]]["unreported"],x["computed_unreported"])
    def test_scope_incomplete(self):
        self.assertIsNone(self.d["source_total_municipal_sections"])
        self.assertIsNone(self.d["islandwide_reporting_unit_denominator"])
        self.assertFalse(self.d["all_in_scope_municipalities_reviewed"])
    def test_unfrozen_unverified(self):
        self.assertIsNone(self.d["raw_pdf_sha256"])
        self.assertTrue(all(x["municipality_canonical_id"] is None for x in self.d["rows"]))
        self.assertEqual(self.d["certification"],"AUDIT_ONLY")
if __name__=="__main__":unittest.main()
