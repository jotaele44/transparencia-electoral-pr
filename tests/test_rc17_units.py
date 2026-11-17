import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc17_units import index_units,compare_epochs
def row(epoch="2024",unit="73",college="01",modality="DOMICILE"):
 return {"synthetic":True,"source_epoch":epoch,"municipality_raw":"Isabela",
        "precinct_raw":"032","unit_raw":unit,"college_raw":college,
        "ballot_type":"MUNICIPAL","modality":modality}
class EpochUnits(unittest.TestCase):
 def test_exact_source_identity_still_candidate(self):
  x=compare_epochs([row()],[row()])
  self.assertEqual(x["intersection"],1)
  self.assertEqual(x["identity"],"CANDIDATE_NOT_IDENTITY")
 def test_raw_leading_zeros_not_equivalent(self):
  x=compare_epochs([row(unit="73")],[row(unit="073")])
  self.assertEqual(x["intersection"],0)
  self.assertEqual(x["symmetric_difference"],2)
 def test_different_epoch_distinct(self):
  x=compare_epochs([row("2024")],[row("2028")])
  self.assertEqual(x["intersection"],0)
 def test_modality_distinct(self):
  x=compare_epochs([row()],[row(modality="REGULAR")])
  self.assertEqual(x["intersection"],0)
 def test_college_identifiers_distinct(self):
  x=compare_epochs([row()],[row(college="04")])
  self.assertEqual(x["intersection"],0)
 def test_duplicate_retained(self):
  x=compare_epochs([row(),row()],[])
  self.assertEqual((x["a_rows"],x["a_indexed"],len(x["a_unresolved"])),(2,1,1))
 def test_unsourced_real_records_rejected_as_unresolved(self):
  item=row();item["synthetic"]=False
  x=compare_epochs([item],[])
  self.assertEqual(x["a_unresolved"][0]["reason"],"NOT_SYNTHETIC")
 def test_empty_denominator_unknown(self):
  x=compare_epochs([],[])
  self.assertIsNone(x["real_official_unit_denominator"])
 def test_sets_close_arithmetically(self):
  x=compare_epochs([row(),row(unit="72")],[row(),row(unit="77")])
  self.assertEqual((x["intersection"],x["a_only"],x["b_only"],x["union"],x["symmetric_difference"]),(1,1,1,3,2))
 def test_malformed_retained(self):
  x=compare_epochs([{}],[])
  self.assertEqual(len(x["a_unresolved"]),1)
if __name__=="__main__":unittest.main()
