import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HistoricalEvidenceGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/"evidence/2024_report_structure.json").read_text())
        cls.denominator=json.loads((ROOT/"evidence/2024_denominator.json").read_text())
    def test_discovery_does_not_imply_inspection(self):
        self.assertEqual(self.report["discovery_status"],"LINK_CONFIRMED_BY_OFFICIAL_CEE_INDEX")
        self.assertIsNone(self.report["sections"])
        self.assertIsNone(self.report["tables"])
    def test_report_approval_not_publication(self):
        self.assertFalse(self.report["approval_date_is_publication_date"])
        self.assertIsNone(self.report["report_publication_date"])
    def test_denominators_still_unresolved(self):
        self.assertEqual(self.denominator["denominator_status"],"OPEN")
        self.assertTrue(all(v is None for v in self.denominator["denominators"].values()))
    def test_no_real_result_pair_claim(self):
        self.assertIsNone(self.report["original_vs_certified_pair"])
        self.assertEqual(self.report["certification"],"UNRESOLVED")
if __name__=="__main__":unittest.main()
