import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RC14AuditTest(unittest.TestCase):
 def setUp(self):self.x=json.loads((ROOT/'certification/rc14_audit_only.json').read_text())
 def test_no_release(self):
  self.assertFalse(self.x['certified']);self.assertFalse(self.x['production_authorized'])
  self.assertEqual(self.x['classification'],'AUDIT_ONLY')
 def test_report_hashes_not_fabricated(self):
  self.assertEqual(self.x['report_recovery']['original_payloads'],0)
  self.assertEqual(self.x['report_recovery']['verified_sha256'],0)
  self.assertEqual(self.x['report_recovery']['version_relation'],'UNRESOLVED')
 def test_22_is_not_complete_denominator(self):
  x=self.x['reporting_units'];self.assertEqual(x['isabela_032_cee_reported_units'],22)
  self.assertIsNone(x['complete_reporting_unit_denominator'])
  self.assertEqual(x['unit_73_modality'],'VOTO_FACIL_ACCESO_EN_DOMICILIO')
  self.assertEqual(x['unit_73_college'],'01')
 def test_isabela_actas_missing(self):
  x=self.x['isabela_case'];self.assertEqual(x['original_actas'],0)
  self.assertEqual(x['verified_acta_pairs'],0)
  self.assertFalse(x['fraud_proven'])
 def test_partial_municipal_results_not_unit_level(self):
  self.assertEqual(self.x['results']['partial_mayoral_pdf'],'MUNICIPALITY_GRAIN_ONLY')
  self.assertEqual(self.x['results']['real_result_pairs'],0)
if __name__=='__main__':unittest.main()
