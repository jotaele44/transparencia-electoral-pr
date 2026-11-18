import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from rc21_legal_versions import classify_legal_version_pair,adjudicate_law_effectivity,validate_calendar_event_rows,classify_javaa_document
class RC21Evidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((ROOT/'evidence/rc21_legal_calendar_manifest.json').read_text())
 def test_source_rows_close(self):
  self.assertEqual(len(self.x['sources']),self.x['denominators']['discovered_source_manifestations'])
  self.assertEqual(len(set(s['id'] for s in self.x['sources'])),len(self.x['sources']))
 def test_dated_ogp_versions_do_not_merge(self):
  a,b=self.x['sources'][4],self.x['sources'][6]
  v=classify_legal_version_pair(a,b)
  self.assertEqual(v['state'],'DIFFERENT_SOURCE_EPOCHS')
  self.assertEqual(v['byte_relation'],'UNVERIFIED')
 def test_equal_source_date_not_proof_of_same_bytes(self):
  a=self.x['sources'][4]
  self.assertEqual(classify_legal_version_pair(a,a)['state'],'SAME_EPOCH_CANDIDATE')
 def test_pretend_sha_without_bytes_fails(self):
  a=dict(self.x['sources'][4]);a['sha256']='a'*64
  with self.assertRaises(ValueError):classify_legal_version_pair(a,a)
 def test_law_date_conflict_preserved(self):
  v=adjudicate_law_effectivity('2026-04-08','2026-04-09')
  self.assertTrue(v['conflict']);self.assertIsNone(v['legal_effective_date_certified'])
 def test_legal_review_cannot_self_certify(self):
  with self.assertRaises(PermissionError):adjudicate_law_effectivity('2026-04-08','2026-04-09',qualified_review=True)
 def test_calendar_preserves_duplicate_and_missing(self):
  x=validate_calendar_event_rows([{'id':'one','date':'2028-06-04','source_id':'CEE','modality':'PRIMARY'},{'id':'one','date':'2028-06-04','source_id':'CEE','modality':'PRIMARY'},{}])
  self.assertEqual((x['input'],x['classified'],len(x['unresolved'])),(3,1,2))
  self.assertIsNone(x['complete_event_denominator'])
 def test_invalid_date_classified(self):
  x=validate_calendar_event_rows([{'id':'one','date':'2028-02-30','source_id':'CEE','modality':'PRIMARY'}])
  self.assertEqual(x['unresolved'][0]['reason'],'INVALID_DATE')
 def test_full_manifest_still_needs_qa(self):
  x=validate_calendar_event_rows([],source_authority_verified=True,complete_amendment_manifest=True)
  self.assertEqual(x['certification'],'REQUIRES_INDEPENDENT_QA')
  self.assertIsNone(x['complete_event_denominator'])
 def test_2024_javaa_not_2028_operational(self):
  self.assertFalse(classify_javaa_document({'authority':'CEE','year_scope':2024})['usable_as_2028_operative'])
 def test_new_2028_javaa_cannot_self_authenticate(self):
  self.assertFalse(classify_javaa_document({'authority':'CEE','year_scope':2028})['usable_as_2028_operative'])
 def test_original_bytes_unknown(self):
  self.assertEqual(self.x['denominators']['original_sha256_verified'],0)
  self.assertIsNone(self.x['denominators']['full_cee_calendar_event_denominator'])
if __name__=='__main__':unittest.main()
