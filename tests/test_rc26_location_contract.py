import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from rc26_location_contract import candidate_observation_schema,candidate_receipt
class RC26CandidateLocation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # Structure mimics exact named Hub location properties, but is not a cached authoritative schema.
  cls.s={"type":"object","properties":{"location":{"type":"object","required":["lat","lon"],
    "properties":{"lat":{"type":"number","minimum":-90,"maximum":90},
    "lon":{"type":"number","minimum":-180,"maximum":180},
    "municipality":{"type":"string"}}}}}
 def test_municipality_only_preserved_without_latlon(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertFalse(list(Draft7Validator(c).iter_errors({"location":{"municipality":"San Juan"}})))
  self.assertNotIn("lat",{"municipality":"San Juan"})
 def test_valid_point_still_passes(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertFalse(list(Draft7Validator(c).iter_errors({"location":{"lat":18.46,"lon":-66.10,"municipality":"San Juan"}})))
 def test_missing_all_location_fields_denied(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertTrue(list(Draft7Validator(c).iter_errors({"location":{}})))
 def test_partial_point_denied_even_with_municipality(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertTrue(list(Draft7Validator(c).iter_errors({"location":{"municipality":"San Juan","lat":18.46}})))
 def test_bad_coords_denied(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertTrue(list(Draft7Validator(c).iter_errors({"location":{"lat":100,"lon":0}})))
 def test_bad_muni_type_denied(self):
  from jsonschema import Draft7Validator
  c=candidate_observation_schema(self.s)
  self.assertTrue(list(Draft7Validator(c).iter_errors({"location":{"municipality":42}})))
 def test_unknown_upstream_schema_denied(self):
  with self.assertRaises(ValueError):candidate_observation_schema({"properties":{"location":{"required":["lat"]}}})
 def test_official_source_unmodified(self):
  orig=json.dumps(self.s,sort_keys=True)
  proposal=candidate_observation_schema(self.s)
  self.assertEqual(json.dumps(self.s,sort_keys=True),orig)
  self.assertFalse(candidate_receipt(self.s,proposal)["production_change_authorized"])
if __name__=="__main__":unittest.main()
