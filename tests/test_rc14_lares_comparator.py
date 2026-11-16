import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LaresComparatorArithmetic(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'evidence/rc14_lares_comparator.json').read_text())
 def test_all_ballot_totals_close(self):
  for kind,row in self.x['official_facts']['ballots'].items():
   with self.subTest(kind=kind):
    self.assertEqual(row['two_initials']+row['one_initial']+row['none'],row['total'])
 def test_list_and_voted_counts_preserved(self):
  self.assertEqual(self.x['official_facts']['voter_list'],1714)
  self.assertEqual(self.x['official_facts']['voted'],1515)
 def test_comparator_is_not_isabela_identity(self):
  self.assertTrue(self.x['separate_from_isabela_case'])
  self.assertIn('No Lares totals',self.x['transfer_rule'])
  self.assertNotEqual(self.x['precinct_raw'],'032')
 def test_source_bytes_not_claimed(self):
  self.assertIsNone(self.x['evidence_sha256'])
  self.assertFalse(self.x['original_bytes_frozen'])
if __name__=='__main__':unittest.main()
