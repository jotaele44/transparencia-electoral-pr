import sys,unittest
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc14_reporting_units import (classify_reporting_unit,isabela_032_denominator,
 validate_special_acta_binding,can_compare_result_pair)
def rec(code="73",cls="SPECIAL_MODALITY",college="01"):
 return {"source_epoch":"2024-11-05","municipality_raw":"Isabela","precinct_raw":"032","unit_raw":code,"college_raw":college,"ballot_type":"MUNICIPAL","unit_class":cls,"authority":"CEE","binding_source_id":"cee_general_manual_2024","college_binding_source_id":"cee_absentee_advance_regulation_2024"}
def acta(municipality="Isabela",precinct="032",payload=b"synthetic acta"):
 return {"source_id":"CEE-ACTA","authority":"CEE","source_epoch":"2024-certified","sha256":sha256(payload).hexdigest(),"original_bytes":payload,"signed":True,"municipality_raw":municipality,"precinct_raw":precinct,"unit_raw":"73","college_raw":"01","modality":"VOTO_FACIL_ACCESO_EN_DOMICILIO"}
def result(source_id,epoch,payload,grain="PRECINCT_UNIT_COLLEGE",identity="VERIFIED_BINDING"):
 return {"source_id":source_id,"authority":"CEE","geographic_level":grain,"source_epoch":epoch,"identity_state":identity,"ballot_type":"MUNICIPAL","sha256":sha256(payload).hexdigest(),"original_bytes":payload,"signed":True}
class RC14UnitTests(unittest.TestCase):
 def test_unit_73_is_home_access_domicile(self):
  x=classify_reporting_unit(rec());self.assertEqual(x["modality"],"VOTO_FACIL_ACCESO_EN_DOMICILIO")
 def test_unit_73_college_01(self):
  self.assertEqual(classify_reporting_unit(rec(college="02"))["reason"],"UNIT_73_COLLEGE_NOT_BOUND_TO_01")
 def test_unit_73_college_requires_own_authority_binding(self):
  x=rec();x["college_binding_source_id"]="operator_guess"
  self.assertEqual(classify_reporting_unit(x)["reason"],"UNIT_73_COLLEGE_SOURCE_NOT_BOUND")
 def test_other_special_modalities_separate(self):
  expected={"72":"VOTO_ADELANTADO_POR_CORREO","74":"COLEGIO_ESPECIAL_JAVAA","76":"VOTO_CONFINADO","77":"VOTO_AUSENTE"}
  for code,modality in expected.items():
   with self.subTest(code=code):self.assertEqual(classify_reporting_unit(rec(code=code))["modality"],modality)
 def test_unit_73_not_silently_regular(self):
  self.assertEqual(classify_reporting_unit(rec(cls="REGULAR_PRECINCT_UNIT"))["reason"],"SPECIAL_CODE_CONFLICTS_WITH_REGULAR_CLASS")
 def test_regular_unit_requires_authoritative_roster(self):
  x=rec(code="03",cls="REGULAR_PRECINCT_UNIT");x["binding_source_id"]="cee_relation_precincts_2024_10_05"
  self.assertEqual(classify_reporting_unit(x)["reason"],"REGULAR_UNIT_ID_NOT_IN_AUTHORITATIVE_ROSTER")
 def test_regular_unit_candidate_epoch_scoped(self):
  x=rec(code="03",cls="REGULAR_PRECINCT_UNIT");x["binding_source_id"]="cee_authoritative_unit_roster"
  self.assertEqual(classify_reporting_unit(x)["identity"],"SOURCE_EPOCH_SCOPED_NOT_CROSS_EPOCH_CANONICAL")
 def test_non_cee_unit_binding_unresolved(self):
  x=rec();x["authority"]="THIRD_PARTY"
  self.assertEqual(classify_reporting_unit(x)["reason"],"NON_AUTHORITATIVE_BINDING")
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
  x=acta();x.pop("original_bytes")
  self.assertEqual(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["reason"],"ACTA_MANIFEST_INCOMPLETE")
 def test_acta_wrong_precinct_blocked(self):
  x=acta(municipality="Lares",precinct="053")
  self.assertEqual(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["reason"],"ACTA_SCOPE_IDENTITY_MISMATCH")
 def test_acta_hash_must_match_original_bytes(self):
  x=acta();x["sha256"]="a"*64
  self.assertEqual(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["reason"],"ACTA_ORIGINAL_BYTES_OR_HASH_UNVERIFIED")
 def test_authentic_scoped_acta_candidate_only(self):
  x=acta()
  self.assertTrue(validate_special_acta_binding(x,municipality_raw="Isabela",precinct_raw="032",unit_raw="73",college_raw="01")["eligible"])
 def test_municipal_partial_cannot_pair_to_unit(self):
  x=result("pre","NIGHT",b"pre",grain="MUNICIPALITY")
  y=result("final","CERTIFIED",b"final")
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"GEOGRAPHIC_GRAIN_MISMATCH")
 def test_result_pair_requires_verified_identity(self):
  x=result("pre","NIGHT",b"pre",identity="CANDIDATE_NOT_IDENTITY")
  y=result("final","CERTIFIED",b"final")
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"IDENTITY_NOT_VERIFIED")
 def test_result_pair_requires_distinct_epochs(self):
  x=result("pre","SAME",b"pre");y=result("final","SAME",b"final")
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"DISTINCT_RESULT_EPOCHS_REQUIRED")
 def test_result_pair_requires_original_bytes(self):
  x=result("pre","NIGHT",b"pre");y=result("final","CERTIFIED",b"final");y.pop("original_bytes")
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"RESULT_ORIGINAL_BYTES_OR_HASH_UNVERIFIED")
 def test_result_pair_requires_matching_hashes(self):
  x=result("pre","NIGHT",b"pre");y=result("final","CERTIFIED",b"final");y["sha256"]="0"*64
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"RESULT_ORIGINAL_BYTES_OR_HASH_UNVERIFIED")
 def test_result_pair_requires_signed_result(self):
  x=result("pre","NIGHT",b"pre");y=result("final","CERTIFIED",b"final");y["signed"]=False
  self.assertEqual(can_compare_result_pair(x,y)["reason"],"RESULT_CERTIFICATION_NOT_VERIFIED")
if __name__=="__main__":unittest.main()
