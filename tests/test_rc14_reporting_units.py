import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc14_reporting_units import (classify_reporting_unit,isabela_032_denominator,
 validate_special_acta_binding,can_compare_result_pair)
def rec(code="73",cls="SPECIAL_MODALITY",college="01"):
 return {"source_epoch":"2024-11-05","municipality_raw":"Isabela","precinct_raw":"032","unit_raw":code,"college_raw":college,"ballot_type":"MUNICIPAL","unit_class":cls}
class RC14UnitTests(unittest.TestCase):
 def test_unit_73_is_home_access_domicile(self):
  x=classify_reporting_unit(rec());self.assertEqual(x["modality"],"VOTO_FACIL_ACCESO_EN_DOMICILIO")
 def test_unit_73_college_01(self):
  self.assertEqual(classify_reporting_unit(rec(college="02"))["reason"],"UNIT_73_COLLEGE_NOT_BOUND_TO_01")
 def test_other_special_modalities_separate(self):
  expected={"72":"VOTO_ADELANTADO_POR_CORREO","74":"COLEGIO_ESPECIAL_JAVAA","76":"VOTO_CONFINADO","77":"VOTO_AUSENTE"}
  for code,modality in expected.items():
   with self.subTest(code=code):self.assertEqual(classify_reporting_unit(rec(code=code))["modality"],modality)
 def test_unit_73_not_silently_regular(self):
  self.assertEqual(classify_reporting_unit(rec(cls="REGULAR_PRECINCT_UNIT"))["reason"],"SPECIAL_CODE_CONFLICTS_WITH_REGULAR_CLASS")
 def test_regular_unit_needs_epoch_scope(self):
  x=classify_reporting_unit(rec(code="03",cls="REGULAR_PRECINCT_UNIT"))
  self.assertEqual(x["state"],"REGULAR_UNIT_CANDIDATE")
  self.assertEqual(x["identity"],"SOURCE_EPOCH_SCOPED_NOT_CROSS_EPOCH_CANONICAL")
 def test_unknown_unit_class_unresolved(self):
  self.assertEqual(classify_reporting_unit(rec(cls="UNKNOWN"))["state"],"UNRESOLVED")
 def test_missing_identity_not_dropped(self):
  x=rec();x.pop("college_raw")
  self.assertEqual(classify_reporting_unit(x)["reason"],"MISSING_RAW_IDENTITY_FIELDS")
 def test_22_units_not_complete_denominator(self):
  x=isabela_032_denominator(22)
  self.assertEqual(x["reported_units"],22)
  self.assertIsNone(x["complete_reporting_unit_denominator"])
  self.assertIsNone(x["special_unit_inclusion_in_22"])
  self.assertEqual(x["certification"],"OPEN")
 def test_do_not_guess_special_unit_inclusion(self):
  with self.assertRaises(ValueError):isabela_032_denominator(22,special_unit_inclusion="PROBABLY")
 def test_acta_without_hash_blocked(self):
  x={"source_id":"CEE-ACTA","authority":"CEE","source_epoch":"2024","signed":True,"municipality_raw":"Isabela","precinct_raw":"032","unit_raw":"73","college_raw":"01","modality":"VOTO_FACIL_ACCESO_EN_DOMICILIO"}
  self.assertEqual(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["reason"],"ACTA_MANIFEST_INCOMPLETE")
 def test_acta_wrong_precinct_blocked(self):
  from hashlib import sha256
  x={"source_id":"CEE-ACTA","authority":"CEE","source_epoch":"2024","signed":True,"sha256":sha256(b"fixture").hexdigest(),"municipality_raw":"Lares","precinct_raw":"053","unit_raw":"73","college_raw":"01","modality":"VOTO_FACIL_ACCESO_EN_DOMICILIO"}
  self.assertEqual(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["reason"],"ACTA_SCOPE_IDENTITY_MISMATCH")
 def test_authentic_scoped_acta_candidate_only(self):
  from hashlib import sha256
  x={"source_id":"CEE-ACTA","authority":"CEE","source_epoch":"2024","signed":True,"sha256":sha256(b"fixture").hexdigest(),"municipality_raw":"Isabela","precinct_raw":"032","unit_raw":"73","college_raw":"01","modality":"VOTO_FACIL_ACCESO_EN_DOMICILIO"}
  self.assertTrue(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["eligible"])
 def test_municipal_partial_cannot_pair_to_unit(self):
  x={"authority":"CEE","geographic_level":"MUNICIPALITY","source_epoch":"NIGHT_OF_ELECTION","identity_state":"VERIFIED_BINDING","ballot_type":"MUNICIPAL","sha256":"a"*64}
  y={"authority":"CEE","geographic_level":"PRECINCT_UNIT_COLLEGE","source_epoch":"CERTIFIED","identity_state":"VERIFIED_BINDING","ballot_type":"MUNICIPAL","sha256":"b"*64}
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"GEOGRAPHIC_GRAIN_MISMATCH")
 def test_result_pair_requires_verified_identity(self):
  x={"authority":"CEE","geographic_level":"PRECINCT_UNIT_COLLEGE","source_epoch":"NIGHT","identity_state":"CANDIDATE_NOT_IDENTITY","ballot_type":"MUNICIPAL","sha256":"a"*64}
  y={"authority":"CEE","geographic_level":"PRECINCT_UNIT_COLLEGE","source_epoch":"CERTIFIED","identity_state":"VERIFIED_BINDING","ballot_type":"MUNICIPAL","sha256":"b"*64}
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"IDENTITY_NOT_VERIFIED")
 def test_result_pair_requires_distinct_epochs(self):
  x={"authority":"CEE","geographic_level":"PRECINCT_UNIT_COLLEGE","source_epoch":"SAME","identity_state":"VERIFIED_BINDING","ballot_type":"MUNICIPAL","sha256":"a"*64}
  y={**x,"sha256":"b"*64}
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"DISTINCT_RESULT_EPOCHS_REQUIRED")
if __name__=="__main__":unittest.main()
